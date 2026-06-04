<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿
<template>
  <el-dropdown>
    <span class="el-dropdown-link">
      <el-avatar shape="square" :size="40" :src="squareUrl" />
      &nbsp;&nbsp;{{ currentUser?.username || '未知用户' }}
      <el-icon class="el-icon--right">
        <arrow-down />
      </el-icon>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item>
          <router-link :to="{ name: ROUTE_NAMES.PERSONAL_CENTER }">个人中心</router-link>
        </el-dropdown-item>
        <el-dropdown-item @click="handleLogout">安全退出</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>import { ArrowDown } from '@element-plus/icons-vue'
import requestUtil, { getServerUrl } from '@/util/request'
import router from '@/router'
import store from '@/store'
import { computed, ref } from 'vue'

// 定义路由常量提高可维护性
const ROUTE_NAMES = {
  PERSONAL_CENTER: '个人中心'
}

// 安全获取当前用户信息
const getCurrentUser = () => {
  try {
    const userStr = sessionStorage.getItem('currentUser')
    return userStr ? JSON.parse(userStr) : null
  } catch (e) {
    console.error('解析用户信息失败:', e)
    return null
  }
}

const currentUser = getCurrentUser()

// 计算头像地址并设置默认 fallback
const squareUrl = computed(() => {
  if (!currentUser?.avatar) {
    return '' // 或返回默认头像路径
  }
  return `${getServerUrl()}media/userAvatar/${encodeURIComponent(currentUser.avatar)}`
})

// 登出方法加锁防止重复触发
const isLoggingOut = ref(false)

const handleLogout = () => {
  if (isLoggingOut.value) return
  isLoggingOut.value = true

  window.sessionStorage.clear()
  store.commit('RESET_TAB')
  router.replace('/login').finally(() => {
    isLoggingOut.value = false
  })
}
</script>

<style lang="scss" scoped>.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
</style>