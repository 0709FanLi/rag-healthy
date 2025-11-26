<template>
  <div class="history-page">
    <!-- 左侧：报告列表 -->
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
        
        <div class="sidebar-content" v-show="!sidebarCollapsed">
          <!-- 开始新对话 -->
          <button class="new-chat-btn" @click="startNewChat">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span>开始新对话</span>
          </button>
          
          <!-- 查看历史报告 -->
          <button class="history-btn active">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
              <path d="M12 7V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span>查看历史报告</span>
          </button>
          
          <div class="history-section">
            <div class="section-title">最近对话</div>
            <div class="reports-list">
              <div 
                v-for="item in reportsList" 
                :key="item.session_id"
                class="report-item"
                @click="selectHistoryChat(item.session_id)"
              >
                <div class="report-preview">{{ item.preview }}</div>
                <div class="report-meta">
                  <span class="report-date">{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
              
              <div v-if="reportsList.length === 0" class="empty-list">
                <p>暂无历史对话</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 折叠状态：只显示图标 -->
        <div class="sidebar-icons" v-show="sidebarCollapsed">
          <button class="icon-btn" @click="startNewChat" title="开始新对话">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
          <button class="icon-btn active" title="查看历史报告">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
              <path d="M12 7V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </aside>

      <!-- 右侧：主内容区 -->
      <div class="main-content">
        <!-- 顶部头部 -->
        <header class="history-header">
          <div class="header-left"></div>
          <h1 class="page-title">查看历史报告</h1>
          <div class="header-right">
            <span class="username">{{ user.username || 'Lana' }}</span>
            <div class="user-avatar">
              <div class="avatar-placeholder">{{ (user.username || 'L')[0].toUpperCase() }}</div>
            </div>
          </div>
        </header>
        
        <!-- 报告详情 -->
        <main class="report-detail">
          <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="currentReport" class="report-content-wrapper">
          <!-- 报告信息栏 -->
          <div class="report-info-bar">
            <div class="info-left">
              <span class="info-label">生成时间</span>
              <span class="info-value">{{ formatDateTime(currentReport.created_at) }}</span>
            </div>
            <div class="navigation-buttons">
              <button 
                class="view-newer-btn" 
                @click="viewNewerReport"
                :disabled="currentReportIndex <= 0"
                v-if="currentReportIndex > 0"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                查看上一个报告
              </button>
              <button 
                class="view-older-btn" 
                @click="viewOlderReport"
                :disabled="currentReportIndex >= reportsList.length - 1"
              >
                查看更早报告
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M19 12H5M5 12L12 5M5 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- HTML报告内容 -->
          <div class="html-report" v-html="reportContent"></div>

          <!-- 免责声明 -->
          <div class="disclaimer-text">
            *本报告仅供参考，不作为医学诊断依据
          </div>

          <!-- 底部商品推荐区 -->
          <div class="products-section">
            <!-- 初始状态：推荐产品按钮 + 左侧图标 -->
            <div v-if="!showProducts" class="recommend-trigger">
              <div class="trigger-icons">
                <div class="icon-circle">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="3" fill="#8B7FE5"/>
                    <path d="M5 20C5 16 8 14 12 14C16 14 19 16 19 20" fill="#8B7FE5"/>
                  </svg>
                </div>
                <div class="icon-circle">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect x="4" y="4" width="7" height="7" rx="1" fill="#6750A4"/>
                    <rect x="13" y="4" width="7" height="7" rx="1" fill="#6750A4"/>
                    <rect x="4" y="13" width="7" height="7" rx="1" fill="#6750A4"/>
                    <rect x="13" y="13" width="7" height="7" rx="1" fill="#6750A4"/>
                  </svg>
                </div>
                <div class="icon-circle">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" fill="#8B7FE5"/>
                  </svg>
                </div>
              </div>
              <button class="recommend-btn" @click="showProducts = true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M9 3H15M3 9H21M3 15H21M9 21H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                推荐产品
              </button>
            </div>

            <!-- 展开状态：产品列表 + 换一换按钮 -->
            <div v-else class="products-expanded">
              <!-- 换一换按钮 -->
              <div class="products-header">
                <div class="change-products">
                  <button class="change-btn" @click="changeProducts">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      <path d="M21 3V8H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    换一换
                  </button>
                </div>
              </div>

              <!-- 商品卡片 -->
              <div class="products-grid">
                <div v-for="i in 3" :key="i" class="product-card">
                  <!-- 占位图 -->
                  <div class="product-image-placeholder">
                    <svg width="80" height="80" viewBox="0 0 100 100" fill="none">
                      <circle cx="50" cy="35" r="12" fill="#C7C7CC"/>
                      <path d="M30 70C30 60 40 55 50 55C60 55 70 60 70 70" fill="#C7C7CC"/>
                      <rect x="65" y="65" width="20" height="20" rx="4" fill="#C7C7CC"/>
                    </svg>
                  </div>
                  <div class="product-info">
                    <h4 class="product-title">保健品名称</h4>
                    <p class="product-desc">这是一段产品介绍文字这是一段产品介绍文字这是一段产品介绍文字这是一段产品介绍文字这是一段产品介绍文字这是一段产品介绍文字</p>
                    <div class="product-actions">
                      <button class="view-details-btn">查看详情</button>
                      <button class="buy-now-btn">去购买</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

          <div v-else class="empty-detail">
            <p>请从左侧选择一个报告查看</p>
          </div>
        </main>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

// 导入图标
import menuExpandIcon from '@/assets/icons/menu-expand.png'
import menuCollapseIcon from '@/assets/icons/menu-collapse.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const user = computed(() => authStore.user || {})

const reportsList = ref([]) // 所有报告列表，按时间倒序
const currentReportIndex = ref(0) // 当前显示的报告索引（0 = 最新）
const currentReport = ref(null)
const loading = ref(false)
const sidebarCollapsed = ref(false)
const showProducts = ref(false) // 是否显示产品列表

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const startNewChat = () => {
  router.push('/chat')
}

const viewHistory = () => {
  // 已经在历史页面，不需要跳转，或许可以刷新列表或重置
  loadReportsList()
}

const reportContent = computed(() => {
  if (!currentReport.value || !currentReport.value.content) return ''
  if (currentReport.value.content.html) {
    return currentReport.value.content.html
  }
  return ''
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return ''
    
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    
    return `${year}-${month}-${day} ${hours}:${minutes}`
  } catch (e) {
    console.error('日期格式化错误:', e)
    return ''
  }
}

const loadReportsList = async () => {
  try {
    const res = await request.get('/report/list')
    reportsList.value = res.reports || []
    
    // 默认加载最新报告（索引 0）
    if (reportsList.value.length > 0) {
      currentReportIndex.value = 0
      await loadReportByIndex(0)
    }
  } catch (error) {
    console.error('加载报告列表失败:', error)
    ElMessage.error('加载报告列表失败')
  }
}

// 点击左侧"最近对话"项，跳转到对话页面（只读模式）
const selectHistoryChat = (sessionId) => {
  router.push({
    path: '/chat',
    query: {
      sessionId: sessionId,
      readOnly: 'true'
    }
  })
}

// 根据索引加载报告
const loadReportByIndex = async (index) => {
  if (index < 0 || index >= reportsList.value.length) {
    return
  }
  
  // 切换报告时重置产品显示状态
  showProducts.value = false
  
  loading.value = true
  const sessionId = reportsList.value[index].session_id
  
  try {
    const res = await request.get(`/report/${sessionId}`)
    currentReport.value = res
    currentReportIndex.value = index
    
    // 如果报告正在生成，触发生成并轮询
    if (res.content && res.content.status === 'generating') {
      await generateAndPoll(sessionId)
    }
  } catch (error) {
    console.error('加载报告详情失败:', error)
    ElMessage.error('加载报告详情失败')
  } finally {
    loading.value = false
  }
}

// 查看更早报告
const viewOlderReport = async () => {
  const nextIndex = currentReportIndex.value + 1
  if (nextIndex < reportsList.value.length) {
    await loadReportByIndex(nextIndex)
  }
}

// 查看上一个报告（更新的报告）
const viewNewerReport = async () => {
  const prevIndex = currentReportIndex.value - 1
  if (prevIndex >= 0) {
    await loadReportByIndex(prevIndex)
  }
}

const generateAndPoll = async (sessionId) => {
  try {
    await request.post(`/report/${sessionId}/generate`)
    
    let attempts = 0
    const maxAttempts = 30
    
    const pollInterval = setInterval(async () => {
      attempts++
      
      if (attempts > maxAttempts) {
        clearInterval(pollInterval)
        ElMessage.error('报告生成超时')
        loading.value = false
        return
      }
      
      try {
        const res = await request.get(`/report/${sessionId}`)
        
        if (res.content && res.content.status === 'completed') {
          clearInterval(pollInterval)
          currentReport.value = res
          loading.value = false
        }
      } catch (error) {
        console.error('轮询错误:', error)
      }
    }, 2000)
  } catch (error) {
    console.error('触发生成失败:', error)
    loading.value = false
  }
}

const selectReport = async (sessionId) => {
  selectedSessionId.value = sessionId
  await loadReportDetail(sessionId)
}

const changeProducts = () => {
  ElMessage.success('换一换功能暂未实现')
}

onMounted(() => {
  loadReportsList()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.history-page {
  display: flex;
  height: 100vh;
  background: #F5F5F7;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

/* 右侧：主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #F3EDF7;
  overflow: hidden;
}

/* 顶部导航栏 */
.history-header {
  height: 64px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  flex-shrink: 0;
}

.history-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 24px;
  right: 24px;
  height: 1px;
  background: #F2F2F7;
}

.header-left {
  width: 40px;
}

.page-title {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0;
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

/* 左侧：报告列表 */
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

.icon-btn.active {
  background: rgba(255, 255, 255, 0.2);
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

.history-btn.active {
  background: #F2F2F7;
  color: #4F378A;
  font-weight: 600;
}

.history-btn svg {
  color: #4F378A;
  flex-shrink: 0;
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

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-item {
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

.report-item:hover {
  background: #F2F2F7;
  border-color: #E5E5EA;
  transform: translateX(4px);
}

.report-preview {
  font-size: 13px;
  color: #1D192B;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  font-weight: 500;
  margin: 0;
}

.report-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-date {
  font-size: 11px;
  color: #8E8E93;
}

.empty-list {
  text-align: center;
  padding: 20px;
  color: #8E8E93;
  font-size: 13px;
}

/* 右侧：报告详情 */
.report-detail {
  flex: 1;
  overflow-y: auto;
  background: #F3EDF7;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #E5E5EA;
  border-top-color: #6750A4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #8E8E93;
}

.empty-detail {
  text-align: center;
  padding: 60px 20px;
  color: #8E8E93;
}

.report-content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px;
}

/* 报告信息栏 */
.report-info-bar {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.navigation-buttons {
  display: flex;
  gap: 12px;
}

.info-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-size: 13px;
  color: #8E8E93;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #1C1C1E;
}

.view-older-btn,
.view-newer-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #6750A4;
  border-radius: 20px;
  color: #6750A4;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.view-older-btn:hover,
.view-newer-btn:hover {
  background: #6750A4;
  color: #FFFFFF;
}

.view-older-btn:disabled,
.view-newer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #C7C7CC;
  color: #C7C7CC;
}

.view-older-btn:disabled:hover,
.view-newer-btn:disabled:hover {
  background: transparent;
  color: #C7C7CC;
}

/* HTML报告内容 */
.html-report {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 报告内容样式（复用Report.vue的样式） */
:deep(.report-container) {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 评分区域样式 */
:deep(.score-section) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #F9F9FB;
  border-radius: 12px;
  margin-bottom: 16px;
}

:deep(.score-circle) {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(#6750A4 0% 65%, #E5E5EA 65% 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

:deep(.score-circle::before) {
  content: '';
  position: absolute;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: #FFFFFF;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

:deep(.score-value) {
  position: relative;
  font-size: 32px !important;
  font-weight: 700 !important;
  color: #6750A4 !important;
  z-index: 1;
  line-height: 1 !important;
  margin: 0 !important;
}

:deep(.score-circle .score-label) {
  position: relative;
  font-size: 11px !important;
  color: #8E8E93 !important;
  z-index: 1;
  margin-top: 4px;
  text-align: center;
  line-height: 1.2;
}

:deep(.risk-info) {
  flex: 1;
  margin-left: 32px;
}

/* 产品推荐区样式 */
.products-section {
  margin-top: 32px;
}

.disclaimer-text {
  font-size: 12px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 16px 0 20px 0;
}

/* 推荐产品触发区域 */
.recommend-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.trigger-icons {
  display: flex;
  gap: 12px;
}

.icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #F5F5F7 0%, #E5E5EA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.recommend-btn {
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

.recommend-btn:hover {
  background: #7B6FD5;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 127, 229, 0.4);
}

/* 产品展开区域 */
.products-expanded {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.products-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.product-card {
  background: #FFFFFF;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.product-image-placeholder {
  height: 180px;
  background: linear-gradient(135deg, #F5F5F7 0%, #E5E5EA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-info {
  padding: 16px;
}

.product-title {
  font-size: 16px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0 0 8px 0;
}

.product-desc {
  font-size: 13px;
  color: #8E8E93;
  line-height: 1.5;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-actions {
  display: flex;
  gap: 8px;
}

.view-details-btn,
.buy-now-btn {
  flex: 1;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.view-details-btn {
  background: #F2F2F7;
  color: #1C1C1E;
}

.view-details-btn:hover {
  background: #E5E5EA;
}

.buy-now-btn {
  background: #6750A4;
  color: #FFFFFF;
}

.buy-now-btn:hover {
  background: #5A3D99;
}

.change-products {
  display: inline-block;
}

.change-btn {
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

.change-btn:hover {
  background: #6750A4;
  color: #FFFFFF;
}

.change-btn svg {
  transition: transform 0.3s;
}

.change-btn:hover svg {
  transform: rotate(180deg);
}

/* 滚动条样式 */
.reports-list::-webkit-scrollbar,
.report-detail::-webkit-scrollbar {
  width: 6px;
}

.reports-list::-webkit-scrollbar-track,
.report-detail::-webkit-scrollbar-track {
  background: transparent;
}

.reports-list::-webkit-scrollbar-thumb,
.report-detail::-webkit-scrollbar-thumb {
  background: #C7C7CC;
  border-radius: 3px;
}

.reports-list::-webkit-scrollbar-thumb:hover,
.report-detail::-webkit-scrollbar-thumb:hover {
  background: #AEAEB2;
}
</style>

