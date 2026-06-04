<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

<template>
  <div class="app-container">
    <el-row :gutter="20" class="header">
      <el-col :span="7">
        <el-input placeholder="请输入操作内容" v-model="queryForm.query" clearable></el-input>
      </el-col>
      <el-button type="primary" :icon="Search" @click="initLogList">搜索</el-button>
    </el-row>
    <el-table
        :data="tableData"
        stripe
        style="width: 100%"
    >
      <el-table-column prop="user_name" label="操作用户" sortable width="120"/>
      <el-table-column prop="operation" label="操作内容" sortable width="200"/>
      <el-table-column prop="method" label="请求方法" sortable width="100"/>
      <el-table-column prop="path" label="请求路径" sortable width="200"/>
      <el-table-column prop="ip" label="客户端IP" sortable width="150"/>
      <el-table-column prop="status" label="状态" sortable width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === 0 ? 'success' : 'danger'" size="small">
            {{ scope.row.status === 0 ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="error_msg" label="错误信息" width="200">
        <template #default="scope">
          <span v-if="scope.row.error_msg" class="error-text">{{ scope.row.error_msg }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" sortable width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
        v-model:current-page="queryForm.pageNum"
        v-model:page-size="queryForm.pageSize"
        :page-sizes="[10, 20, 30, 40]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import {Search} from '@element-plus/icons-vue'
import requestUtil from '@/util/request'
import {ref} from "vue";

const tableData = ref([])
const total = ref(0)
const queryForm = ref({
  query: '',
  pageNum: 1,
  pageSize: 10
})

const initLogList = async () => {
  const res = await requestUtil.post("log/log/", queryForm.value)
  tableData.value = res.data.logList
  total.value = res.data.total
}

const handleSizeChange = (pageSize) => {
  queryForm.value.pageSize = pageSize
  queryForm.value.pageNum = 1
  initLogList()
}

const handleCurrentChange = (pageNum) => {
  queryForm.value.pageNum = pageNum
  initLogList()
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const match = dateTimeString.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).*$/)
  if (match) {
    return `${match[1]} ${match[2]}`
  }
  return dateTimeString
}

initLogList()
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

.error-text {
  color: #f56c6c;
  font-size: 12px;
}
</style>