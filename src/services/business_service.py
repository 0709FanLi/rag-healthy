import re
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.tables import Session, Message, Report
from src.services.llm_service import llm_service
from src.services.prompts import PHASE_0_CHECK, REPORT_GENERATION

class BusinessService:
    async def create_session(self, db: AsyncSession, user_id: int) -> Session:
        session = Session(user_id=user_id, status="active", meta_data={})
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def get_session(self, db: AsyncSession, session_id: int) -> Session:
        result = await db.execute(select(Session).where(Session.id == session_id))
        return result.scalars().first()

    async def process_chat(self, db: AsyncSession, session_id: int, user_input: str) -> dict:
        """
        处理聊天逻辑
        Returns:
            dict: {
                "response": str,  # 展示给用户的文本
                "action": str,    # 'chat' 或 'report'
                "report_data": dict | None
            }
        """
        session = await self.get_session(db, session_id)
        if not session:
            raise ValueError("Session not found")

        # 1. 保存用户消息
        user_msg = Message(session_id=session_id, role="user", content=user_input)
        db.add(user_msg)
        await db.commit()

        # 2. 检查会话状态
        current_track = session.meta_data.get("track") if session.meta_data else None
        question_count = session.meta_data.get("question_count", 0) if session.meta_data else 0
        answered_count = session.meta_data.get("answered_count", 0) if session.meta_data else 0
        last_question_sent = session.meta_data.get("last_question_sent", False) if session.meta_data else False
        
        print(f"DEBUG: Before update - Track: {current_track}, Q: {question_count}, A: {answered_count}, LastSent: {last_question_sent}")

        # ⚠️ 关键修复：只有在已经发送过问题后，用户的回复才算是回答问题
        # 如果赛道已锁定、有问题计划、且上次已发送问题，说明用户刚回答了一个问题
        if current_track and question_count > 0 and last_question_sent:
            answered_count += 1
            # 立即更新到 session (先不 commit)
            meta = dict(session.meta_data) if session.meta_data else {}
            meta["answered_count"] = answered_count
            session.meta_data = meta
            print(f"DEBUG: Updated answered_count to {answered_count}")
        
        # 检查是否已有报告（异步查询）
        report_check = await db.execute(
            select(Report).where(Report.session_id == session_id)
        )
        existing_report = report_check.scalar_one_or_none()
        
        # 判断是否应该生成报告（所有问题都回答完）
        should_generate_report = (
            current_track 
            and not existing_report 
            and question_count > 0 
            and answered_count >= question_count
        )
        
        print(f"DEBUG: Should generate? {should_generate_report} (Existing: {bool(existing_report)})")
        
        if should_generate_report:
            # --- 生成报告阶段 ---
            
            # 1. 准备结束语（固定格式，不调用LLM）
            thank_you_msg = "收到！您的答案我们已记录。正在为您生成健康报告..."
            
            # 2. 创建空的报告记录（status = "generating"）
            new_report = Report(
                session_id=session_id,
                score=0,  # 初始值
                risk_level="生成中",  # 初始值
                content={"status": "generating", "html": ""}
            )
            db.add(new_report)
            
            # 3. 更新会话状态
            session.status = "generating_report"
            
            # 4. 保存 AI 的感谢语消息
            ai_msg = Message(session_id=session_id, role="assistant", content=thank_you_msg)
            db.add(ai_msg)
            
            await db.commit()
            await db.refresh(new_report)  # 获取 report ID
            
            # 5. 立即返回，让前端跳转
            return {
                "response": thank_you_msg,
                "action": "report",
                "report_data": {"id": new_report.id, "status": "generating"}
            }

        else:
            # --- 普通/问卷生成阶段 ---
            db_messages = await db.execute(
                select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
            )
            history_msgs = db_messages.scalars().all()
            
            api_messages = []
            for msg in history_msgs:
                api_messages.append({"role": msg.role, "content": msg.content})
            
            # 调用 LLM (对话阶段使用低思考模式)
            response_text = await llm_service.chat_completion(
                messages=api_messages,
                system_prompt=PHASE_0_CHECK,
                thinking_level="low"
            )
            
            # 解析思维链
            ai_thinking = ""
            user_reply = response_text
            
            if "【给用户的回复】" in response_text:
                parts = response_text.split("【给用户的回复】")
                ai_thinking = parts[0]
                user_reply = parts[1].strip()
            
            # 更新 session metadata
            meta = dict(session.meta_data) if session.meta_data else {}
            
            # 检查是否锁定赛道
            track_match = re.search(r"锁定赛道[:：]\s*(.+)", ai_thinking)
            if track_match:
                track = track_match.group(1).strip()
                meta["track"] = track
            
            # 提取问题总数（仅在首次设置）
            if "question_count" not in meta or meta["question_count"] == 0:
                question_count_match = re.search(r"总问题数[:：]\s*(\d+)", ai_thinking)
                if question_count_match:
                    meta["question_count"] = int(question_count_match.group(1))
                    # 初始化 answered_count 为 0（还没开始回答）
                    if "answered_count" not in meta:
                        meta["answered_count"] = 0
            
            # 检测是否发送了问题（通过检测当前问题编号）
            current_question_match = re.search(r"当前问题编号[:：]\s*(\d+)", ai_thinking)
            if current_question_match:
                # 说明 AI 刚发送了一个问题，标记状态
                meta["last_question_sent"] = True
            
            # 保存 metadata
            if meta != session.meta_data:
                session.meta_data = meta
                db.add(session)
            
            # 格式化AI回复
            formatted_reply = self._format_question(user_reply)
            
            # 关键修复：检测 AI 是否自行结束了对话（即使状态机认为还没结束）
            # 如果 AI 回复中包含结束语，强制进入报告生成流程
            if "生成健康报告" in formatted_reply or "正在为您生成" in formatted_reply:
                print(f"DEBUG: AI triggered completion. Text: {formatted_reply[:30]}...")
                
                # 1. 创建空的报告记录（status = "generating"）
                new_report = Report(
                    session_id=session_id,
                    score=0,  # 初始值
                    risk_level="生成中",  # 初始值
                    content={"status": "generating", "html": ""}
                )
                db.add(new_report)
                
                # 2. 更新会话状态
                session.status = "generating_report"
                
                # 3. 保存 AI 的消息
                ai_msg = Message(session_id=session_id, role="assistant", content=formatted_reply)
                db.add(ai_msg)
                
                await db.commit()
                await db.refresh(new_report)
                
                return {
                    "response": formatted_reply,
                    "action": "report",
                    "report_data": {"id": new_report.id, "status": "generating"}
                }
            
            # 保存AI回复
            ai_msg = Message(session_id=session_id, role="assistant", content=formatted_reply)
            db.add(ai_msg)
            await db.commit()
            
            return {
                "response": formatted_reply,
                "action": "chat",
                "report_data": None
            }

    def _format_question(self, response_text: str) -> str:
        """
        格式化AI回复，确保问题的选项换行
        """
        formatted = re.sub(
            r'([^\n])\s+([ABCD]\.)', 
            r'\1\n\2', 
            response_text
        )
        formatted = re.sub(
            r'(\d+\.)\s*([^\n])', 
            r'\1 \2', 
            formatted
        )
        return formatted.strip()

    async def _get_chat_history(self, db, session_id) -> str:
        result = await db.execute(
            select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
        )
        msgs = result.scalars().all()
        return "\n".join([f"{m.role}: {m.content}" for m in msgs])

    async def generate_report_content(self, db: AsyncSession, session_id: int):
        """生成报告内容（LLM调用）"""
        # 获取 session 和 report
        session = await self.get_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        
        report_result = await db.execute(
            select(Report).where(Report.session_id == session_id)
        )
        report = report_result.scalar_one_or_none()
        if not report:
            raise ValueError("Report not found")
        
        # 检查是否已生成
        if report.content.get("status") != "generating":
            return  # 已生成，无需重复
        
        try:
            # 获取历史消息
            history = await self._get_chat_history(db, session_id)
            current_track = session.meta_data.get("track", "未知")
            
            # 调用 LLM 生成报告
            report_prompt = REPORT_GENERATION.format(
                user_info=session.meta_data.get("user_info", "未提取"),
                track=current_track,
                qa_pairs=f"Full Context: {history}"
            )
            
            # 调用 LLM 生成报告 (报告阶段使用高思考模式)
            raw_report = await llm_service.chat_completion(
                messages=[{"role": "user", "content": "请生成HTML报告"}],
                system_prompt=report_prompt,
                thinking_level="high"
            )
            
            # 清理 Markdown 标记
            clean_report = re.sub(r"```html\s*|\s*```", "", raw_report).strip()
            
            # 提取分数和风险等级
            score = 0
            risk_level = "Unknown"
            
            score_match = re.search(r'class="score-value">(\d+)<', clean_report)
            if score_match:
                score = int(score_match.group(1))
                
            risk_match = re.search(r'class="risk-badge[^"]*">([^<]+)<', clean_report)
            if risk_match:
                risk_level = risk_match.group(1).strip()
            
            # 更新报告
            report.score = score
            report.risk_level = risk_level
            report.content = {"status": "completed", "html": clean_report}
            
            # 更新会话状态
            session.status = "completed"
            
            db.add(report)
            db.add(session)
            await db.commit()
            
        except Exception as e:
            # 生成失败，标记错误
            report.content = {"status": "error", "error": str(e), "html": ""}
            db.add(report)
            await db.commit()
            raise

business_service = BusinessService()
