<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿
<template>
  <div class="navbar">
    <div class="hamburger-container" @click="toggleSidebar">
      <el-icon :size="20">
        <Fold v-if="!isCollapse" />
        <Expand v-else />
      </el-icon>
    </div>
    <Breadcrumb />
    <div class="navbar-right">
      <NotificationBell />
      <Avatar />
    </div>
  </div>
</template>

<script setup>
import Breadcrumb from './components/breadcrumb.vue'
import Avatar from './components/avatar.vue'
import NotificationBell from './components/notificationBell.vue'
import { Fold, Expand } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

const isCollapse = computed(() => store.state.isCollapse)

const toggleSidebar = () => {
  store.commit('TOGGLE_COLLAPSE')
}
</script>

<style lang="scss" scoped>
.navbar {
  width: 100%;
  height: 60px;
  overflow: hidden;
  background-color: #f5f5f5;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 16px;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  position: relative;

  .hamburger-container {
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 15px;
    cursor: pointer;
    transition: background 0.3s;
    
    &:hover {
      background-color: rgba(0, 0, 0, 0.05);
    }
  }

  .navbar-right {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
  }

  :deep(.navbar-item) {
    display: inline-block;
    margin-left: 18px;
    font-size: 22px;
    color: #5a5e66;
    box-sizing: border-box;
    cursor: pointer;
  }
}
</style>