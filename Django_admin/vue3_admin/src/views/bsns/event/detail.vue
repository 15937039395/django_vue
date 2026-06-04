<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-page-header @back="goBack" content="事件详情" />
    <div class="detail-content">
      <el-card v-loading="loading">
        <el-descriptions title="事件信息" :column="2" border>
          <el-descriptions-item label="事件编号">
            {{ eventData.event_number || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="事件名称">
            {{ eventData.event_name || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ eventData.principal || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">
            {{ eventData.start_date || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期">
            {{ eventData.end_date || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="eventData.status === '正常' ? 'success' : 'danger'">
              {{ eventData.status || '暂无数据' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(eventData.create_time) || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(eventData.update_time) || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ eventData.remark || '暂无数据' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 参与人员列表 -->
    <div class="participants-section" style="margin-top: 20px;">
      <el-card>
        <template #header>
          <div class="card-header">
            <span style="font-weight: bold;">参与人员</span>
          </div>
        </template>
        <el-table :data="participants" style="width: 100%">
          <el-table-column prop="realname" label="姓名" />
          <el-table-column prop="username" label="用户名" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from "element-plus"
import requestUtil from '@/util/request'

const route = useRoute()

const eventData = ref({})
const participants = ref([])
const loading = ref(false)

const getDetail = async () => {
  const eventId = route.query.id || route.params.id

  if (!eventId) {
    ElMessage.error('缺少事件ID参数')
    return
  }

  try {
    loading.value = true
    const res = await requestUtil.get(`event/detail?id=${eventId}`)
    if (res.data.code === 200) {
      eventData.value = res.data.event || {}
      participants.value = res.data.participants || []
    } else {
      ElMessage.error(res.data.msg || '获取详情失败')
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  } finally {
    loading.value = false
  }
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const match = dateTimeString.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).*$/)
  return match ? `${match[1]} ${match[2]}` : dateTimeString
}

const goBack = () => {
  window.history.back()
}

onMounted(() => {
  getDetail()
})
</script>

<style scoped>
.detail-content {
  margin-top: 20px;
}
</style>