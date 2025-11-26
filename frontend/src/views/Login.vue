<template>
  <div class="login-container">
    <div class="login-card">
      <div class="input-field">
        <p class="field-label">邮箱</p>
        <div class="input-wrapper">
          <input 
            v-model="form.username" 
            type="text"
            class="field-input" 
            placeholder="请输入邮箱"
          />
        </div>
      </div>
      
      <div class="input-field">
        <p class="field-label">密码</p>
        <div class="input-wrapper">
          <input 
            v-model="form.password" 
            type="password"
            class="field-input" 
            placeholder="请输入密码"
          />
        </div>
      </div>
      
      <div class="button-group">
        <button 
          class="login-button" 
          @click="handleLogin"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登  录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    // 使用 x-www-form-urlencoded 格式
    const formData = new FormData()
    formData.append('username', form.value.username)
    formData.append('password', form.value.password)

    const res = await request.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    authStore.setToken(res.access_token, { username: res.username, id: res.user_id })
    ElMessage.success('登录成功')
    router.push('/chat')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 容器样式 - 淡紫色背景，占满全屏 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  background-color: #fef7ff;
  padding: 20px;
  margin: 0;
  box-sizing: border-box;
}

/* 登录卡片 - 白色卡片，圆角，边框 */
.login-card {
  width: 100%;
  max-width: 561px;
  min-width: 320px;
  background-color: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-sizing: border-box;
}

/* Input Field - 对应 Figma 的 Input Field 组件 */
.input-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

/* 字段标签 */
.field-label {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1.4;
  color: #1e1e1e;
  margin: 0;
  padding: 0;
}

/* 输入框包装器 */
.input-wrapper {
  width: 100%;
  min-width: 240px;
  background-color: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  padding: 12px 16px;
  transition: border-color 0.2s ease;
}

.input-wrapper:hover {
  border-color: #8c8c8c;
}

.input-wrapper:focus-within {
  border-color: #2c2c2c;
}

/* 输入框本身 */
.field-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1;
  color: #1e1e1e;
  padding: 0;
  margin: 0;
  min-width: 0;
}

.field-input::placeholder {
  color: #b3b3b3;
}

/* 按钮组 - 对应 Figma 的 Button Group */
.button-group {
  display: flex;
  gap: 16px;
  width: 100%;
}

/* 登录按钮 */
.login-button {
  flex: 1;
  min-width: 0;
  background-color: #2c2c2c;
  border: 1px solid #2c2c2c;
  border-radius: 8px;
  padding: 12px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1;
  color: #f5f5f5;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-button:hover:not(:disabled) {
  background-color: #1a1a1a;
  border-color: #1a1a1a;
}

.login-button:active:not(:disabled) {
  background-color: #0f0f0f;
  border-color: #0f0f0f;
  transform: scale(0.98);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    max-width: 100%;
    padding: 20px;
  }
  
  .input-field {
    gap: 6px;
  }
}
</style>

