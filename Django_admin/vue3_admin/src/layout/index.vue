<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-wrapper" @click="updateActivity" @keydown="updateActivity" @scroll="updateActivity">
    <el-container>
      <el-aside :width="sidebarWidth" class="sidebar-container"><Menu/></el-aside>
      <el-container>
        <el-header><Header/></el-header>
        <el-main><Tabs/><router-view/></el-main>
        <el-footer><Footer/></el-footer>
      </el-container>
    </el-container>
  </div>
</template>


<script setup>
import Menu from '@/layout/menu'
import Header from '@/layout/header'
import Footer from '@/layout/footer'
import Tabs from '@/layout/tabs'
import { computed } from 'vue'
import { useStore } from 'vuex'
import { touch } from '@/util/auth' // 引入认证管理器的touch方法

const store = useStore()

// 计算侧边栏宽度
const sidebarWidth = computed(() => {
  return store.state.isCollapse ? '64px' : '200px'
})

// 更新用户活动时间
const updateActivity = () => {
  touch(); // 调用认证管理器的touch方法更新活动时间
}
</script>

<style scoped>

.app-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.sidebar-container {
  background-color: #2d3a4b;
  height: 100%;
  transition: width 0.28s ease-out;
  overflow-x: hidden;
}

.el-container {
  height: 100%
}

.el-header {
  padding-left: 0px;
  padding-right: 0px;
}

:deep(ul.el-menu) {
  border-right-width: 0px
}
</style>