<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <el-menu
      active-text-color="#ffd04b"
      background-color="#2d3a4b"
      class="el-menu-vertical-demo"
      text-color="#fff"
      router
      :default-active="defaultActivePath"
      :collapse="isCollapse"
      :collapse-transition="false"
  >
    <el-menu-item index="/index" @click="openTab({name:'首页',path:'/index'})">
      <el-icon>
        <home-filled/>
      </el-icon>
      <span>首页</span>
    </el-menu-item>
    <!-- 有子菜单的菜单（子菜单方式） -->
    <el-sub-menu :index="menu.path" v-for="menu in safeMenuList.menusWithChildren" :key="menu.path">
      <template #title>
        <el-icon>
          <svg-icon :icon="menu.icon"/>
        </el-icon>
        <span>{{ menu.name }}</span>
      </template>
      <el-menu-item :index="item.path" v-for="item in menu.children" :key="item.path" @click="openTab(item)">
        <el-icon>
          <svg-icon :icon="item.icon"/>
        </el-icon>
        <span>{{ item.name }}</span>
      </el-menu-item>
    </el-sub-menu>
    
    <!-- 没有子菜单的菜单（直接显示为菜单项） -->
    <el-menu-item :index="menu.path" v-for="menu in safeMenuList.menusWithoutChildren" :key="menu.path" @click="openTab(menu)">
      <el-icon>
        <svg-icon :icon="menu.icon"/>
      </el-icon>
      <span>{{ menu.name }}</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import store from '@/store'
import { HomeFilled } from '@element-plus/icons-vue'
import { computed } from 'vue'

// 默认激活路径
const defaultActivePath = '/index'

// 获取折叠状态
const isCollapse = computed(() => store.state.isCollapse)

// 安全地从 sessionStorage 获取 menuList 并设置默认值
const rawMenuList = sessionStorage.getItem("menuList")
let parsedMenuList = []

if (rawMenuList) {
  try {
    parsedMenuList = JSON.parse(rawMenuList)
  } catch (e) {
    console.error('Failed to parse menuList from sessionStorage:', e)
  }
}

// 对 menuList 进行基础校验以避免渲染错误
const safeMenuList = computed(() => {
  if (!Array.isArray(parsedMenuList)) return []
  
  // 区分有子菜单和无子菜单的菜单项
  const menusWithChildren = []
  const menusWithoutChildren = []
  
  parsedMenuList.forEach(menu => {
    if (typeof menu !== 'object' || typeof menu.path !== 'string') {
      return // 跳过无效菜单
    }
    
    if (Array.isArray(menu.children) && menu.children.length > 0) {
      // 有子菜单的菜单
      menusWithChildren.push(menu)
    } else if (!Array.isArray(menu.children) || menu.children.length === 0) {
      // 没有子菜单的菜单（一级菜单）
      menusWithoutChildren.push(menu)
    }
  })
  
  return { menusWithChildren, menusWithoutChildren }
})

// 打开 tab 之前进行简单校验
const openTab = (item) => {
  if (
      !item ||
      typeof item !== 'object' ||
      typeof item.name !== 'string' ||
      typeof item.path !== 'string'
  ) {
    console.warn('Invalid tab item:', item)
    return
  }
  store.commit('ADD_TABS', item)
}
</script>

<style lang="scss" scoped>
</style>
