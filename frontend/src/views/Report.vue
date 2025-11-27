<template>
  <div class="report-page">
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
              :class="{ active: item.id === currentReportId }"
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

    <!-- 主内容区域 -->
    <main class="report-main">
      <!-- 顶部导航栏 -->
      <div class="top-nav">
        <div class="header-left"></div>
      <h1 class="page-title">查看历史报告</h1>
      <div class="user-info">
          <span class="username">{{ user.username || 'Lana' }}</span>
        <div class="avatar">
          <img v-if="user.avatar" :src="user.avatar" alt="avatar" />
          <div v-else class="avatar-placeholder">{{ (user.username || 'L')[0].toUpperCase() }}</div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="page-content">
      <!-- Loading 状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>报告生成中，请稍候...</p>
      </div>

      <!-- 报告内容 -->
      <div v-else-if="report && reportContent.html" class="report-wrapper">
        <!-- HTML报告区域（红框部分） -->
        <div class="html-report-area" v-html="reportContent.html"></div>

          <!-- 底部商品推荐区 -->
        <div class="products-section">
          <!-- 免责声明 -->
          <div class="disclaimer-text">
            *本报告仅供参考，不作为医学诊断依据
          </div>

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

      <!-- 错误状态 -->
      <div v-else class="empty-state">
        <p>暂无报告数据</p>
        <button class="retry-btn" @click="fetchReport">重试</button>
      </div>
    </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import menuCollapseIcon from '@/assets/icons/menu-collapse.png'
import menuExpandIcon from '@/assets/icons/menu-expand.png'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user || {})

const loading = ref(true)
const report = ref(null)
const sidebarCollapsed = ref(false)
const showProducts = ref(false)
const historyItems = ref([])
const currentReportId = computed(() => route.query.id)

const reportContent = computed(() => {
  if (!report.value) return {}
  if (report.value.content && report.value.content.html) {
    return { html: report.value.content.html }
  }
  return { html: '' }
})

const fetchReport = async () => {
  const id = route.query.id
  if (!id) {
    ElMessage.error('未找到报告 ID')
    router.push('/chat')
    return
  }
  
  loading.value = true
  try {
    const res = await request.get(`/report/${id}`)
    report.value = res
    
    if (res.content && res.content.status === 'generating') {
      await generateAndPoll(id)
    } else {
      loading.value = false
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取报告失败')
    loading.value = false
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
        ElMessage.error('报告生成超时，请刷新页面重试')
        loading.value = false
        return
      }
      
      try {
        const res = await request.get(`/report/${sessionId}`)
        
        if (res.content && res.content.status === 'completed') {
          clearInterval(pollInterval)
          report.value = res
          loading.value = false
          ElMessage.success('报告生成完成！')
        } else if (res.content && res.content.status === 'error') {
          clearInterval(pollInterval)
          ElMessage.error('报告生成失败：' + (res.content.error || '未知错误'))
          loading.value = false
        }
      } catch (error) {
        console.error('轮询错误:', error)
      }
    }, 2000)
  } catch (error) {
    console.error('触发生成失败:', error)
    ElMessage.error('无法触发报告生成')
    loading.value = false
  }
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const startNewChat = () => {
  router.push('/chat')
}

const viewHistory = () => {
  router.push('/history')
}

const viewHistoryReport = (reportId) => {
  router.push(`/report?id=${reportId}`)
}

const changeProducts = () => {
  ElMessage.success('换一换功能暂未实现')
}

const fetchHistoryList = async () => {
  try {
    const res = await request.get('/report/list', {
      params: { page: 1, page_size: 10 }
    })
    historyItems.value = res.items.map(item => ({
      id: item.session_id,
      preview: item.preview || `报告 ${item.session_id}`
    }))
  } catch (error) {
    console.error('获取历史列表失败:', error)
  }
}

onMounted(() => {
  // 重置产品显示状态
  showProducts.value = false
  fetchReport()
  fetchHistoryList()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.report-page {
  min-height: 100vh;
  background: #F3EDF7;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  display: flex;
}

/* ========== 左侧边栏 ========== */
.sidebar {
  width: 280px;
  background: #FFFFFF;
  border-right: 1px solid #E5E5EA;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid #E5E5EA;
}

.menu-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
  padding: 0;
}

.menu-btn:hover {
  background: #F2F2F7;
}

.menu-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.sidebar-content {
  flex: 1;
  padding: 20px 16px;
  overflow-y: auto;
}

.new-chat-btn,
.history-btn {
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: #8B7FE5;
  color: #FFFFFF;
  font-size: 15px;
  font-weight: 500;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
  margin-bottom: 12px;
}

.new-chat-btn:hover,
.history-btn:hover {
  background: #7B6FD5;
}

.history-btn {
  background: #6750A4;
}

.history-btn:hover {
  background: #574094;
}

.history-section {
  margin-top: 24px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #8E8E93;
  margin-bottom: 12px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px;
  background: #F2F2F7;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: #E5E5EA;
}

.history-item.active {
  background: #8B7FE5;
}

.history-item.active .history-text {
  color: #FFFFFF;
}

.history-text {
  font-size: 14px;
  color: #1C1C1E;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-icons {
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: #F2F2F7;
  color: #8B7FE5;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.icon-btn:hover {
  background: #E5E5EA;
}

/* ========== 主内容区域 ========== */
.report-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ========== 顶部导航栏 ========== */
.top-nav {
  background: #FFFFFF;
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #E5E5EA;
  position: sticky;
  top: 0;
  z-index: 100;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 15px;
  font-weight: 500;
  color: #1C1C1E;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #8B7FE5 0%, #6750A4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 16px;
}

/* ========== 主体内容 ========== */
.page-content {
  max-width: 680px;
  margin: 0 auto;
  padding: 24px 20px 40px;
}

/* Loading */
.loading-container {
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

.loading-container p {
  color: #8E8E93;
  font-size: 15px;
}

/* 报告包装器 */
.report-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* HTML报告区域（红框内容） */
.html-report-area {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* ========== 底部商品推荐区 ========== */
.products-section {
  margin-top: 10px;
}

.disclaimer-text {
  font-size: 12px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0 0 20px 0;
}

/* 推荐产品触发区域 */
.recommend-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
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
  padding: 12px 24px;
  background: #8B7FE5;
  color: #FFFFFF;
  border: none;
  border-radius: 24px;
  font-size: 15px;
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

.recommend-btn:active {
  transform: translateY(0);
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

/* 错误状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #8E8E93;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 24px;
  background: #6750A4;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
}

.retry-btn:hover {
  background: #5A3D99;
}

/* ========== HTML报告内容样式（:deep） ========== */
/* 这些样式应用于AI生成的HTML */

:deep(.report-container) {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 报告标题卡片 */
:deep(.report-header) {
  background: linear-gradient(135deg, #6750A4 0%, #8B7FE5 100%);
  color: #FFFFFF;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
}

:deep(.report-header h1) {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

:deep(.report-header .meta) {
  font-size: 13px;
  opacity: 0.9;
}

/* 评分区域 */
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
  font-size: 32px;
  font-weight: 700;
  color: #6750A4;
  z-index: 1;
  line-height: 1;
  margin: 0;
}

:deep(.score-circle .score-label) {
  position: relative;
  font-size: 11px;
  color: #8E8E93;
  z-index: 1;
  margin-top: 4px;
  text-align: center;
  line-height: 1.2;
}

:deep(.score-info) {
  flex: 1;
  margin-left: 32px;
}

/* 适配AI生成的 .risk-info 类名 */
:deep(.risk-info) {
  flex: 1;
  margin-left: 32px;
}

:deep(.score-label) {
  font-size: 12px;
  color: #8E8E93;
  margin-bottom: 4px;
}

:deep(.score-text) {
  font-size: 32px;
  font-weight: 700;
  color: #1C1C1E;
}

:deep(.score-total) {
  font-size: 18px;
  color: #8E8E93;
}

:deep(.score-desc) {
  font-size: 13px;
  color: #8E8E93;
  margin-top: 4px;
}

/* 风险卡片 */
:deep(.risk-cards) {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

:deep(.risk-card) {
  padding: 16px;
  border-radius: 12px;
  position: relative;
}

:deep(.risk-card.orange) { background: #FFF4E6; }
:deep(.risk-card.green) { background: #E6F4EA; }
:deep(.risk-card.blue) { background: #E3F2FD; }
:deep(.risk-card.purple) { background: #F3E5F5; }

:deep(.risk-icon) {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
}

:deep(.risk-card.orange .risk-icon) { background: #FF9500; }
:deep(.risk-card.green .risk-icon) { background: #34C759; }
:deep(.risk-card.blue .risk-icon) { background: #007AFF; }
:deep(.risk-card.purple .risk-icon) { background: #AF52DE; }

:deep(.risk-title) {
  font-size: 15px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0 0 8px 0;
}

:deep(.risk-content) {
  font-size: 13px;
  color: #49454F;
  line-height: 1.5;
}

:deep(.risk-content ul) {
  margin: 4px 0 0 0;
  padding-left: 16px;
}

:deep(.risk-content li) {
  margin-bottom: 4px;
}

/* 建议区域 */
:deep(.suggestions) {
  background: #F9F9FB;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 16px;
}

:deep(.suggestions h3) {
  font-size: 16px;
  font-weight: 600;
  color: #1C1C1E;
  margin: 0 0 12px 0;
}

:deep(.suggestions ul) {
  margin: 0;
  padding-left: 20px;
}

:deep(.suggestions li) {
  font-size: 14px;
  color: #49454F;
  line-height: 1.6;
  margin-bottom: 8px;
}

/* 通用样式 */
:deep(h1), :deep(h2), :deep(h3), :deep(h4) {
  color: #1C1C1E;
}

:deep(p) {
  color: #49454F;
  line-height: 1.6;
}

:deep(strong) {
  font-weight: 600;
  color: #1C1C1E;
}
</style>
