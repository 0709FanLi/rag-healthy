<template>
  <div class="chat-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="menu-btn" @click="toggleSidebar">
          <img 
            :src="sidebarCollapsed ? menuCollapseIcon : menuExpandIcon" 
            alt="菜单" 
            class="menu-icon"
          />
        </button>
      </div>
      
      <!-- 展开状态的内容 -->
      <div class="sidebar-content" v-show="!sidebarCollapsed">
        <!-- 开始新对话 -->
        <button class="new-chat-btn" @click="startNewChat">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>开始新对话</span>
        </button>
        
        <!-- 查看历史报告 -->
        <button class="history-btn" @click="viewHistory">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 7V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>查看历史报告</span>
        </button>
        
        <!-- 历史对话列表 -->
        <div class="history-section">
          <div class="section-title">最近对话</div>
          <div class="history-list">
            <div 
              v-for="item in historyItems" 
              :key="item.id" 
              class="history-item"
              :class="{ active: item.id === sessionId }"
              @click="viewHistoryReport(item.id)"
            >
              <div class="history-text">{{ item.preview }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 折叠状态：只显示图标 -->
      <div class="sidebar-icons" v-show="sidebarCollapsed">
        <button class="icon-btn" @click="startNewChat" title="开始新对话">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <button class="icon-btn" @click="viewHistory" title="查看历史报告">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 7V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </aside>
    
    <!-- 主聊天区域 -->
    <main class="chat-main">
      <!-- 顶部栏 -->
      <header class="chat-header">
        <div class="header-left"></div>
        <div class="header-right">
          <span class="username">{{ user.username || 'Lana' }}</span>
          <div class="user-avatar">
            <img v-if="user.avatar" :src="user.avatar" alt="avatar" />
            <div v-else class="avatar-placeholder">{{ (user.username || 'L')[0].toUpperCase() }}</div>
          </div>
        </div>
      </header>
      
      <!-- 报告显示区域 -->
      <div v-if="showReport" class="report-display-area">
        <!-- 报告生成中 Loading -->
        <div v-if="reportLoading" class="report-loading">
          <div class="loading-spinner"></div>
          <p>报告生成中，请稍候...</p>
        </div>
        
        <!-- 报告内容 -->
        <div v-else-if="reportData && reportContent.html" class="report-content-area">
          <!-- HTML报告区域 -->
          <div class="html-report-section" v-html="reportContent.html"></div>

          <!-- 底部商品推荐区 -->
          <div class="products-recommendation">
            <!-- 免责声明 -->
            <div class="disclaimer-notice">
              *本报告仅供参考，不作为医学诊断依据
            </div>

            <!-- 初始状态：推荐产品按钮 + 左侧图标 -->
            <div v-if="!showProducts" class="recommend-trigger-area">
              <div class="trigger-icon-group">
                <div class="trigger-icon-circle">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="3" fill="#8B7FE5"/>
                    <path d="M5 20C5 16 8 14 12 14C16 14 19 16 19 20" fill="#8B7FE5"/>
                  </svg>
                </div>
                <div class="trigger-icon-circle">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect x="4" y="4" width="7" height="7" rx="1" fill="#6750A4"/>
                    <rect x="13" y="4" width="7" height="7" rx="1" fill="#6750A4"/>
                    <rect x="4" y="13" width="7" height="7" rx="1" fill="#6750A4"/>
                    <rect x="13" y="13" width="7" height="7" rx="1" fill="#6750A4"/>
                  </svg>
                </div>
                <div class="trigger-icon-circle">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" fill="#8B7FE5"/>
                  </svg>
                </div>
              </div>
              <button class="show-products-btn" @click="showProducts = true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M9 3H15M3 9H21M3 15H21M9 21H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                推荐产品
              </button>
            </div>

            <!-- 展开状态：产品列表 + 换一换按钮 -->
            <div v-else class="products-list-area">
              <!-- 换一换按钮 -->
              <div class="change-products-header">
                <button class="change-products-btn" @click="changeProducts">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M21 3V8H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  换一换
                </button>
              </div>

              <!-- 商品卡片列表 -->
              <div class="product-cards-grid">
                <div v-for="i in 3" :key="i" class="product-item-card">
                  <div class="product-img-placeholder">
                    <svg width="80" height="80" viewBox="0 0 100 100" fill="none">
                      <circle cx="50" cy="35" r="12" fill="#C7C7CC"/>
                      <path d="M30 70C30 60 40 55 50 55C60 55 70 60 70 70" fill="#C7C7CC"/>
                      <rect x="65" y="65" width="20" height="20" rx="4" fill="#C7C7CC"/>
                    </svg>
                  </div>
                  <div class="product-card-info">
                    <h4 class="product-card-title">保健品名称</h4>
                    <p class="product-card-desc">这是一段产品介绍文字这是一段产品介绍文字这是一段产品介绍文字</p>
                    <div class="product-card-actions">
                      <button class="product-detail-btn">查看详情</button>
                      <button class="product-buy-btn">去购买</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息区域 -->
      <div v-else class="messages-container" ref="messagesRef">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          class="message-wrapper"
          :class="msg.role"
        >
          <!-- AI 消息：只有气泡，没有头像 -->
          <template v-if="msg.role === 'assistant'">
            <div class="message-bubble">
              <div class="message-content" v-html="renderMessage(msg.content)"></div>
            </div>
          </template>
          
          <!-- 用户消息：气泡 + 右侧头像 -->
          <template v-else>
            <div class="message-bubble">
              <div class="message-content" v-html="renderMessage(msg.content)"></div>
            </div>
            <div class="message-avatar">
              <div class="avatar-circle">{{ (user.username || 'L')[0].toUpperCase() }}</div>
            </div>
          </template>
        </div>
        
        <!-- AI 思考中 - 精美 Loading -->
        <div v-if="loading" class="ai-loading-container">
          <div class="loading-card">
            <!-- 旋转动画 -->
            <div class="loading-spinner-wrapper">
              <div class="spinner-ring"></div>
              <div class="spinner-ring"></div>
              <div class="spinner-ring"></div>
              <div class="spinner-core">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" fill="#8B7FE5"/>
                </svg>
              </div>
            </div>
            
            <!-- 动态提示文字 -->
            <div class="loading-text-container">
              <h3 class="loading-title">{{ loadingTitle }}</h3>
              <p class="loading-subtitle">{{ loadingSubtitle }}</p>
            </div>
            
            <!-- 进度提示 -->
            <div class="loading-progress">
              <div class="progress-bar">
                <div class="progress-fill"></div>
              </div>
              <span class="progress-hint">预计需要 3-5 秒</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-container">
        <!-- 只读模式提示 -->
        <div v-if="isReadOnly" class="readonly-notice">
          <span>📖 正在查看历史对话（只读模式）</span>
          <button class="exit-readonly-btn" @click="startNewChat">开始新对话</button>
        </div>
        
        <div class="input-wrapper">
          <button class="attach-btn" title="上传文件">
            <img :src="uploadIcon" alt="上传" class="upload-icon" />
          </button>
          <textarea 
          v-model="inputMessage"
            :placeholder="isReadOnly ? '查看历史对话（只读模式）' : '请输入您的健康困扰...'"
            @keydown.enter.exact.prevent="sendMessage"
            :disabled="loading || isReadOnly"
            rows="1"
          ></textarea>
          <button class="send-btn" @click="sendMessage" :disabled="loading || !inputMessage.trim() || isReadOnly">
            <img :src="sendIcon" alt="发送" class="send-icon" />
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'

// 导入图标
import menuExpandIcon from '@/assets/icons/menu-expand.png'
import menuCollapseIcon from '@/assets/icons/menu-collapse.png'
import sendIcon from '@/assets/icons/send.png'
import uploadIcon from '@/assets/icons/upload.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const user = computed(() => authStore.user || {})
const md = new MarkdownIt()

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const sessionId = ref(null)
const messagesRef = ref(null)
const sidebarCollapsed = ref(false)
const isReadOnly = ref(false) // 只读模式标记
const showReport = ref(false) // 是否显示报告
const reportData = ref(null) // 报告数据
const showProducts = ref(false) // 是否显示产品列表
const reportLoading = ref(false) // 报告生成中

// Loading 动态文字
const loadingTitle = ref('正在分析您的健康状况')
const loadingSubtitle = ref('AI 正在为您生成个性化问题...')
const loadingTextIndex = ref(0)

// 历史对话列表（从后端获取）
const historyItems = ref([])

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const loadHistoryReports = async () => {
  try {
    const res = await request.get('/report/list')
    historyItems.value = res.reports.map(report => ({
      id: report.session_id,
      preview: report.preview,
      score: report.score,
      created_at: report.created_at
    }))
  } catch (error) {
    console.error('加载历史报告失败:', error)
  }
}

const viewHistory = () => {
  // 跳转到历史记录页面
  router.push({ name: 'History' })
}

const viewHistoryReport = async (targetSessionId) => {
  // 加载历史对话内容（只读模式）
  try {
    // 重置状态
    showReport.value = false
    showProducts.value = false
    reportData.value = null
    isReadOnly.value = true
    
    const res = await request.get(`/chat/session/${targetSessionId}`)
    
    // 切换到该 session
    sessionId.value = res.session_id
    messages.value = []
    
    if (res.messages && Array.isArray(res.messages)) {
      res.messages.forEach(msg => {
        messages.value.push({ role: msg.role, content: msg.content })
      })
    }
    
    // 标记为只读模式
    isReadOnly.value = true
    ElMessage.info('正在查看历史对话（只读模式）')
    
    scrollToBottom()
  } catch (error) {
    console.error(error)
    ElMessage.error('加载历史对话失败')
  }
}

const renderMessage = (content) => {
  return md.render(content).trim()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const loadActiveSession = async () => {
  try {
    const activeSession = await request.get('/chat/active')
    sessionId.value = activeSession.session_id
    messages.value = []
    
    if (activeSession.messages && Array.isArray(activeSession.messages)) {
      activeSession.messages.forEach(msg => {
        messages.value.push({ role: msg.role, content: msg.content })
      })
    }
    
    console.log(`✅ 恢复会话 ${sessionId.value}，包含 ${messages.value.length} 条消息`)
    scrollToBottom()
  } catch (error) {
    console.log('📝 没有活跃会话，创建新会话...')
    await startNewChat()
  }
}

const startNewChat = async () => {
  try {
    messages.value = []
    isReadOnly.value = false // 退出只读模式
    showReport.value = false // 退出报告显示
    showProducts.value = false // 重置产品显示
    reportData.value = null
    
    const res = await request.post('/chat/start')
    sessionId.value = res.session_id
    
    if (res.messages && Array.isArray(res.messages)) {
      res.messages.forEach(msg => {
        messages.value.push({ role: msg.role, content: msg.content })
      })
    }
    console.log(`✅ 创建新会话 ${sessionId.value}`)
    scrollToBottom()
  } catch (error) {
    console.error(error)
  }
}

// Loading 文字轮换
const loadingTexts = [
  { title: '正在分析您的健康状况', subtitle: 'AI 正在为您生成个性化问题...' },
  { title: '深度理解您的需求', subtitle: '根据您的回答定制专属问卷...' },
  { title: '智能匹配健康方案', subtitle: '这可能需要几秒钟，请稍候...' }
]

let loadingInterval = null

const startLoadingAnimation = () => {
  loadingTextIndex.value = 0
  loadingTitle.value = loadingTexts[0].title
  loadingSubtitle.value = loadingTexts[0].subtitle
  
  loadingInterval = setInterval(() => {
    loadingTextIndex.value = (loadingTextIndex.value + 1) % loadingTexts.length
    loadingTitle.value = loadingTexts[loadingTextIndex.value].title
    loadingSubtitle.value = loadingTexts[loadingTextIndex.value].subtitle
  }, 2000)
}

const stopLoadingAnimation = () => {
  if (loadingInterval) {
    clearInterval(loadingInterval)
    loadingInterval = null
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  
  const content = inputMessage.value
  messages.value.push({ role: 'user', content })
  inputMessage.value = ''
  scrollToBottom()
  
  loading.value = true
  startLoadingAnimation()
  
  try {
    const res = await request.post('/chat/message', {
      session_id: sessionId.value,
      content
    })
    
    if (res.response) {
    messages.value.push({ role: 'assistant', content: res.response })
    } else if (res.messages && Array.isArray(res.messages)) {
      res.messages.forEach(msg => {
        messages.value.push({ role: 'assistant', content: msg })
      })
    }
    
    scrollToBottom()
    
    if (res.action === 'report') {
      // 延迟加载报告，让用户看到感谢语
      setTimeout(async () => {
        // 不显示消息，直接切换到报告加载状态
        await loadReport(sessionId.value)
      }, 2000)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('发送失败，请重试')
  } finally {
    loading.value = false
    stopLoadingAnimation()
  }
}

const loadReport = async (reportSessionId) => {
  try {
    // 先切换到报告显示状态并显示 loading
    showReport.value = true
    reportLoading.value = true
    
    const res = await request.get(`/report/${reportSessionId}`)
    
    if (res.content && res.content.status === 'generating') {
      await generateAndPollReport(reportSessionId)
    } else {
      reportData.value = res
      reportLoading.value = false
      ElMessage.success('报告已生成！')
    }
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败')
    reportLoading.value = false
  }
}

const generateAndPollReport = async (reportSessionId) => {
  try {
    await request.post(`/report/${reportSessionId}/generate`)
    
    let attempts = 0
    const maxAttempts = 30
    
    const pollInterval = setInterval(async () => {
      attempts++
      
      if (attempts > maxAttempts) {
        clearInterval(pollInterval)
        ElMessage.error('报告生成超时，请刷新页面重试')
        reportLoading.value = false
        return
      }
      
      try {
        const res = await request.get(`/report/${reportSessionId}`)
        
        if (res.content && res.content.status === 'completed') {
          clearInterval(pollInterval)
          reportData.value = res
          showReport.value = true
          reportLoading.value = false
          ElMessage.success('报告生成完成！')
        } else if (res.content && res.content.status === 'error') {
          clearInterval(pollInterval)
          ElMessage.error('报告生成失败：' + (res.content.error || '未知错误'))
          reportLoading.value = false
        }
      } catch (error) {
        console.error('轮询错误:', error)
      }
    }, 2000)
  } catch (error) {
    console.error('触发生成失败:', error)
    ElMessage.error('无法触发报告生成')
    reportLoading.value = false
  }
}

const changeProducts = () => {
  ElMessage.success('换一换功能暂未实现')
}

const reportContent = computed(() => {
  if (!reportData.value) return {}
  if (reportData.value.content && reportData.value.content.html) {
    return { html: reportData.value.content.html }
  }
  return { html: '' }
})

onMounted(async () => {
  // 检查是否有只读模式参数
  const targetSessionId = route.query.sessionId
  const readOnly = route.query.readOnly === 'true'
  
  if (targetSessionId && readOnly) {
    // 只读模式：加载指定会话的历史记录
    await viewHistoryReport(parseInt(targetSessionId))
  } else {
    // 正常模式：加载或创建活跃会话
    await loadActiveSession()
  }
  
  loadHistoryReports()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.chat-container {
  display: flex;
  height: 100vh;
  background: #F5F5F7;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

/* ========== 左侧边栏 ========== */
.sidebar {
  width: 220px;
  background: #FFFFFF;
  border-radius: 32px;
  margin: 12px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.sidebar.collapsed {
  width: 70px;
  background: #6750A4;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #E5E5EA;
}

.sidebar.collapsed .sidebar-header {
  border-bottom-color: rgba(255, 255, 255, 0.2);
  padding: 20px 0;
  display: flex;
  justify-content: center;
}

.menu-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #1C1C1E;
  transition: background 0.2s, color 0.2s;
  padding: 0;
}

.sidebar.collapsed .menu-btn {
  color: #FFFFFF;
}

.menu-btn:hover {
  background: #F2F2F7;
}

.sidebar.collapsed .menu-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.menu-icon {
  width: 24px;
  height: 24px;
  display: block;
}

.sidebar.collapsed .menu-icon {
  filter: brightness(0) invert(1);
}

.sidebar-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 折叠状态下的图标按钮 */
.sidebar-icons {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
}

.icon-btn {
  width: 48px;
  height: 48px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #FFFFFF;
  transition: background 0.2s;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.icon-btn svg {
  color: #FFFFFF;
  width: 24px;
  height: 24px;
}

.new-chat-btn {
  width: 100%;
  padding: 8px 16px;
  margin-bottom: 12px;
  border: none;
  background: #EADDFF;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #4F378A;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: #E1D4F8;
}

.new-chat-btn svg {
  color: #6750A4;
}

.history-btn {
  width: 100%;
  padding: 12px 16px;
  margin-bottom: 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #4F378A;
  transition: all 0.2s;
}

.history-btn:hover {
  background: #F2F2F7;
}

.history-btn svg {
  color: #4F378A;
}

.history-section {
  margin-top: 24px;
}

.section-title {
  font-size: 14px;
  color: #49454F;
  margin-bottom: 8px;
  font-weight: 500;
  padding: 0 16px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px 16px;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 1px solid transparent;
}

.history-item:hover {
  background: #F2F2F7;
  border-color: #E5E5EA;
  transform: translateX(4px);
}

.history-item.active {
  background: #E8E5F7;
  border-color: #6750A4;
}

.history-text {
  font-size: 13px;
  color: #1D192B;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  font-weight: 500;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-badge {
  font-size: 11px;
  color: #6750A4;
  background: #EADDFF;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

/* ========== 主聊天区域 ========== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
}

.chat-header {
  height: 64px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
}

.chat-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 24px;
  right: 24px;
  height: 1px;
  background: #F2F2F7;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 15px;
  font-weight: 600;
  color: #1C1C1E;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 16px;
}

/* ========== 消息区域 ========== */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 32px 48px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  margin-bottom: 16px;
}

.message-wrapper.assistant {
  justify-content: flex-start;
  flex-direction: row;
}

.message-wrapper.user {
  justify-content: flex-end;
  flex-direction: row;
}

.message-bubble {
  max-width: 680px;
  min-width: 100px;
  flex-shrink: 1;
}

.message-wrapper.assistant .message-bubble {
  background: #ECE6F0;
  border-radius: 20px 20px 20px 8px;
  padding: 11px 16px;
}

.message-wrapper.user .message-bubble {
  background: #625B71;
  border-radius: 20px 20px 8px 20px;
  padding: 11px 16px;
}

.message-content {
  font-size: 15px;
  line-height: 1.5;
  color: #1C1C1E;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* 去除 markdown 生成的 p 标签边距 */
.message-content :deep(p) {
  margin: 0 !important;
}

.message-content :deep(p:not(:last-child)) {
  margin-bottom: 8px !important; /* 段落之间保持间距 */
}

.message-wrapper.user .message-content {
  color: #FFFFFF;
}

.message-avatar {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  align-self: center;
}

.avatar-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 16px;
  font-size: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.avatar-circle.ai {
    background: linear-gradient(135deg, #8B7FE5 0%, #6750A4 100%);
}

/* ========== AI Loading 精美动画 ========== */
.ai-loading-container {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loading-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F7FC 100%);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 
    0 8px 32px rgba(139, 127, 229, 0.15),
    0 2px 8px rgba(0, 0, 0, 0.05);
  max-width: 480px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  border: 1px solid rgba(139, 127, 229, 0.1);
}

/* 旋转动画容器 */
.loading-spinner-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid transparent;
  animation: spinRing 2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: #8B7FE5;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  width: 85%;
  height: 85%;
  border-top-color: #A89FF5;
  animation-delay: 0.15s;
}

.spinner-ring:nth-child(3) {
  width: 70%;
  height: 70%;
  border-top-color: #C5BFF8;
  animation-delay: 0.3s;
}

@keyframes spinRing {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.spinner-core {
  position: relative;
  z-index: 10;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #8B7FE5 0%, #6750A4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 4px 16px rgba(139, 127, 229, 0.4),
    inset 0 2px 8px rgba(255, 255, 255, 0.2);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 
      0 4px 16px rgba(139, 127, 229, 0.4),
      inset 0 2px 8px rgba(255, 255, 255, 0.2);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 
      0 6px 24px rgba(139, 127, 229, 0.6),
      inset 0 2px 8px rgba(255, 255, 255, 0.3);
  }
}

/* 文字容器 */
.loading-text-container {
  text-align: center;
  animation: textFade 2s ease-in-out infinite;
}

@keyframes textFade {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.loading-title {
  font-size: 20px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #6750A4 0%, #8B7FE5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.loading-subtitle {
  font-size: 15px;
  color: #8E8E93;
  margin: 0;
  line-height: 1.5;
}

/* 进度提示 */
.loading-progress {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: #E5E5EA;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8B7FE5 0%, #A89FF5 50%, #8B7FE5 100%);
  background-size: 200% 100%;
  animation: progressSlide 2s linear infinite;
  border-radius: 2px;
}

@keyframes progressSlide {
  0% {
    width: 0%;
    background-position: 0% 0%;
  }
  50% {
    width: 70%;
    background-position: 100% 0%;
  }
  100% {
    width: 100%;
    background-position: 200% 0%;
  }
}

.progress-hint {
  font-size: 13px;
  color: #A0A0A8;
  text-align: center;
}

/* ========== 报告显示区域 ========== */
.report-display-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 48px 40px;
}

.report-loading {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #E5E5EA;
  border-top-color: #6750A4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.report-loading p {
  color: #8E8E93;
  font-size: 15px;
}

.report-content-area {
  max-width: 800px;
  margin: 0 auto;
}

.html-report-section {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
}

/* 产品推荐区域 */
.products-recommendation {
  margin-top: 16px;
}

.disclaimer-notice {
  font-size: 12px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0 0 20px 0;
}

.recommend-trigger-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.trigger-icon-group {
  display: flex;
  gap: 12px;
}

.trigger-icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #F5F5F7 0%, #E5E5EA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.show-products-btn {
  padding: 14px 32px;
  background: #8B7FE5;
  color: #FFFFFF;
  border: none;
  border-radius: 28px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(139, 127, 229, 0.3);
}

.show-products-btn:hover {
  background: #7B6FD5;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 127, 229, 0.4);
}

.products-list-area {
  animation: productFadeIn 0.3s ease-in;
}

@keyframes productFadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.change-products-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.change-products-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: #FFFFFF;
  border: 2px solid #6750A4;
  border-radius: 24px;
  color: #6750A4;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.change-products-btn:hover {
  background: #6750A4;
  color: #FFFFFF;
}

.product-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.product-item-card {
  background: #FFFFFF;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.product-img-placeholder {
  height: 180px;
  background: linear-gradient(135deg, #F5F5F7 0%, #E5E5EA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-card-info {
  padding: 16px;
}

.product-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0 0 8px 0;
}

.product-card-desc {
  font-size: 13px;
  color: #8E8E93;
  line-height: 1.5;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-card-actions {
  display: flex;
  gap: 8px;
}

.product-detail-btn,
.product-buy-btn {
  flex: 1;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.product-detail-btn {
  background: #F2F2F7;
  color: #1C1C1E;
}

.product-detail-btn:hover {
  background: #E5E5EA;
}

.product-buy-btn {
  background: #6750A4;
  color: #FFFFFF;
}

.product-buy-btn:hover {
  background: #5A3D99;
}

/* ========== 输入区域 ========== */
.input-container {
  padding: 20px 48px 24px;
  background: #FFFFFF;
  border-top: 1px solid #E5E5EA;
}

.readonly-notice {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #FFF4E6;
  border: 1px solid #FFE5B4;
  border-radius: 12px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #B06000;
}

.exit-readonly-btn {
  padding: 6px 16px;
  background: #6750A4;
  color: #FFFFFF;
  border: none;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.exit-readonly-btn:hover {
  background: #5A3D99;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #ECE6F0;
  border-radius: 28px;
  padding: 14px 20px;
  border: none;
  max-width: 100%;
}

.attach-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8E8E93;
  transition: color 0.2s;
  flex-shrink: 0;
}

.attach-btn:hover {
  color: #1C1C1E;
}

.upload-icon {
  width: 20px;
  height: 20px;
  display: block;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.attach-btn:hover .upload-icon {
  opacity: 1;
}

.input-wrapper textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  outline: none;
  font-size: 15px;
  color: #1C1C1E;
  font-family: inherit;
  line-height: 1.5;
  max-height: 120px;
  padding: 6px 0;
}

.input-wrapper textarea::placeholder {
  color: #8E8E93;
}

.send-btn {
  width: 35px;
  height: 35px;
  border: none;
  background: #1C1C1E;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #2C2C2E;
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-icon {
  width: 20px;
  height: 20px;
  display: block;
  filter: brightness(0) invert(1);
}

/* ========== Markdown 样式 ========== */
.message-content :deep(p) {
  margin: 0 0 8px 0;
}

.message-content :deep(p:last-child) {
  margin: 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-content :deep(li) {
  margin: 4px 0;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}

.message-wrapper.user .message-content :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

/* ========== 滚动条样式 ========== */
.messages-container::-webkit-scrollbar,
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track,
.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb,
.sidebar-content::-webkit-scrollbar-thumb {
  background: #C7C7CC;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover,
.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #AEAEB2;
}
</style>
