// Copyright (c) 2025 知识库管理系统. All rights reserved.

import { createApp } from 'vue'
import SvgIcon from '@/icons'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
// 引入wangEditor样式
import '@wangeditor/editor/dist/css/style.css'
// 国际化中文
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import '@/assets/styles/border.css'
import '@/assets/styles/reset.css'
import '@/assets/styles/theme.css'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import authManager from '@/util/auth' // 引入认证管理器

const app=createApp(App)

// 全局错误处理 - 过滤掉浏览器扩展的错误
app.config.errorHandler = (err, vm, info) => {
  // 忽略来自浏览器扩展的错误
  const errorMessage = err?.message || ''
  const errorStack = err?.stack || ''
  const ignorePatterns = [
    'crypto.randomUUID is not a function',
    'chrome-extension://',
    'page.js'
  ]
  
  const shouldIgnore = ignorePatterns.some(pattern => 
    errorMessage.includes(pattern) || errorStack.includes(pattern)
  )
  
  if (!shouldIgnore) {
    // 只输出非扩展错误
    console.error('Vue Error:', err)
  }
}

// 全局捕获未处理的 Promise 错误
window.addEventListener('unhandledrejection', (event) => {
  const errorMessage = event?.reason?.message || ''
  const errorStack = event?.reason?.stack || ''
  const ignorePatterns = [
    'crypto.randomUUID is not a function',
    'chrome-extension://',
    'page.js'
  ]
  
  const shouldIgnore = ignorePatterns.some(pattern => 
    errorMessage.includes(pattern) || errorStack.includes(pattern)
  )
  
  if (shouldIgnore) {
    event.preventDefault() // 阻止错误显示
  }
})

// 全局捕获普通错误
window.addEventListener('error', (event) => {
  const errorMessage = event?.message || ''
  const filename = event?.filename || ''
  const ignorePatterns = [
    'crypto.randomUUID is not a function',
    'chrome-extension://',
    'page.js'
  ]
  
  const shouldIgnore = ignorePatterns.some(pattern => 
    errorMessage.includes(pattern) || filename.includes(pattern)
  )
  
  if (shouldIgnore) {
    event.preventDefault() // 阻止错误显示
  }
})

SvgIcon(app);

// 注册全局权限指令
app.directive('permission', {
  mounted(el, binding) {
    const { value } = binding
    const permissions = JSON.parse(sessionStorage.getItem('permissions') || '[]')
    
    if (value && value instanceof Array && value.length > 0) {
      const hasPermission = permissions.some(perm => value.includes(perm))
      
      if (!hasPermission) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  }
})

app.use(store)

app.use(router)

app.use(ElementPlus, {
    locale: zhCn,
})
app.mount('#app')
