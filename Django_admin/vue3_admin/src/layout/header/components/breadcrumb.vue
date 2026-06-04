<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿
<template>
  <el-icon>
    <HomeFilled />
  </el-icon>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item
      v-for="(item, index) in breadcrumbList"
      :key="index"
    >
      <span>{{ item.name }}</span>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup>import { HomeFilled } from '@element-plus/icons-vue'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const breadcrumbList = ref([])

// 过滤有效面包屑项并确保数据安全
const initBreadcrumbList = () => {
  if (Array.isArray(route.matched)) {
    breadcrumbList.value = route.matched.filter(
      item => item && typeof item === 'object' && item.name
    )
  } else {
    breadcrumbList.value = []
  }
}

// 精确监听路由路径变化以提高性能
watch(
  () => route.path,
  () => {
    initBreadcrumbList()
  },
  { immediate: true }
)
</script>

<style lang="scss" scoped></style>