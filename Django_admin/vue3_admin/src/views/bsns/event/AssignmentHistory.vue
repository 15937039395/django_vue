<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-row :gutter="20" class="header">
      <el-col :span="7">
        <el-input placeholder="搜索事件名称、编号或人员姓名..." v-model="queryForm.query" clearable @clear="initHistoryList"></el-input>
      </el-col>
      <el-button type="primary" :icon="Search" @click="initHistoryList">搜索</el-button>
      <el-button type="info" :icon="Refresh" @click="resetQuery">重置</el-button>
    </el-row>

    <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
      <el-table-column prop="operate_time" label="操作时间" width="180" align="center">
        <template #default="scope">
          {{ formatDateTime(scope.row.operate_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="event_name" label="事件名称" width="180" align="center" show-overflow-tooltip />
      <el-table-column prop="event_number" label="事件编号" width="150" align="center" />
      <el-table-column prop="user_name" label="参与人员" width="120" align="center" />
      <el-table-column prop="action_text" label="操作类型" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.action === 1 ? 'success' : 'danger'">
            {{ scope.row.action_text }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="operator_name" label="操作人" width="120" align="center" />
      <el-table-column prop="remark" label="备注" show-overflow-tooltip />
    </el-table>

    <el-pagination
      v-model:currentPage="queryForm.pageNum"
      v-model:page-size="queryForm.pageSize"
      :page-sizes="[10, 20, 30, 50]"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import requestUtil from '@/util/request'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const queryForm = ref({
  query: '',
  pageNum: 1,
  pageSize: 10
})

const initHistoryList = async () => {
  loading.value = true
  try {
    const res = await requestUtil.post("event/assignment/history", queryForm.value)
    if (res.data.code === 200) {
      tableData.value = res.data.historyList
      total.value = res.data.total
    } else {
      ElMessage.error(res.data.msg || '获取记录失败')
    }
  } catch (error) {
    console.error('获取分配记录失败:', error)
    ElMessage.error('获取分配记录失败')
  } finally {
    loading.value = false
  }
}

const resetQuery = () => {
  queryForm.value.query = ''
  queryForm.value.pageNum = 1
  initHistoryList()
}

const handleSizeChange = (pageSize) => {
  queryForm.value.pageSize = pageSize
  queryForm.value.pageNum = 1
  initHistoryList()
}

const handleCurrentChange = (pageNum) => {
  queryForm.value.pageNum = pageNum
  initHistoryList()
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const match = dateTimeString.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).*$/)
  if (match) {
    return `${match[1]} ${match[2]}`
  }
  return dateTimeString.replace('T', ' ').split('.')[0]
}

onMounted(() => {
  initHistoryList()
})
</script>

<style lang="scss" scoped>
.header {
  padding-bottom: 16px;
  box-sizing: border-box;
}

.el-pagination {
  float: right;
  padding: 20px;
  box-sizing: border-box;
}

:deep(th.el-table__cell) {
  word-break: break-word;
  background-color: #f8f8f9 !important;
  color: #515a6e;
  height: 40px;
  font-size: 13px;
}
</style>
