<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div>
    <el-card>
      <el-form :inline="true">
        <el-form-item label="审批状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待审批" :value="1"></el-option>
            <el-option label="已通过" :value="2"></el-option>
            <el-option label="已拒绝" :value="3"></el-option>
            <el-option label="已撤销" :value="4"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="initApprovalList">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="approvalList" border stripe>
        <el-table-column prop="title" label="审批标题" min-width="200"></el-table-column>
        <el-table-column prop="approval_type_display" label="审批类型" width="120"></el-table-column>
        <el-table-column prop="applicant_name" label="申请人" width="100"></el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 1" type="warning">待审批</el-tag>
            <el-tag v-else-if="scope.row.status === 2" type="success">已通过</el-tag>
            <el-tag v-else-if="scope.row.status === 3" type="danger">已拒绝</el-tag>
            <el-tag v-else type="info">已撤销</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="申请时间" width="180"></el-table-column>
        <el-table-column prop="approver_name" label="审批人" width="100"></el-table-column>
        <el-table-column prop="approve_time" label="审批时间" width="180"></el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <!-- 待审批状态：管理员可以审批，申请人可以撤销 -->
            <template v-if="scope.row.status === 1">
              <el-button 
                v-if="currentUserName === 'admin'" 
                type="success" 
                size="small"
                @click="handleApprove(scope.row.id)"
              >通过</el-button>
              <el-button 
                v-if="currentUserName === 'admin'" 
                type="danger" 
                size="small"
                @click="handleReject(scope.row.id)"
              >拒绝</el-button>
              <el-button 
                v-if="scope.row.applicant_id === currentUserId" 
                type="warning" 
                size="small"
                @click="handleCancel(scope.row.id)"
              >撤销</el-button>
            </template>
            <!-- 其他状态：查看详情 -->
            <el-button v-else type="primary" size="small" @click="showDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="pageNum"
        :page-sizes="[10, 20, 30, 40]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        style="margin-top: 20px"
      >
      </el-pagination>
    </el-card>

    <!-- 审批对话框 -->
    <el-dialog v-model="approveDialogVisible" title="审批" width="500px">
      <el-form :model="approveForm" label-width="100px">
        <el-form-item label="审批意见">
          <el-input 
            v-model="approveForm.remark" 
            type="textarea" 
            :rows="4"
            placeholder="请输入审批意见"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmApprove">确认</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="审批详情" width="600px">
      <el-descriptions :column="1" border v-if="currentApproval">
        <el-descriptions-item label="审批标题">{{ currentApproval.title }}</el-descriptions-item>
        <el-descriptions-item label="审批类型">{{ currentApproval.approval_type_display }}</el-descriptions-item>
        <el-descriptions-item label="审批内容">{{ currentApproval.content }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentApproval.applicant_name }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ currentApproval.create_time }}</el-descriptions-item>
        <el-descriptions-item label="审批状态">{{ currentApproval.status_display }}</el-descriptions-item>
        <el-descriptions-item label="审批人">{{ currentApproval.approver_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审批时间">{{ currentApproval.approve_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审批意见">{{ currentApproval.approve_remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import requestUtil from '@/util/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const approvalList = ref([])
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = ref({
  status: null
})

const approveDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const approveForm = ref({
  id: null,
  action: '',
  remark: ''
})
const currentApproval = ref(null)

// 当前用户信息
const currentUser = JSON.parse(sessionStorage.getItem('currentUser') || '{}')
const currentUserId = currentUser.id
const currentUserName = currentUser.username

// 获取审批列表
const initApprovalList = async () => {
  try {
    console.log('正在请求审批列表...')
    console.log('请求URL:', 'approval/list')
    console.log('请求参数:', {
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      status: searchForm.value.status
    })
    const result = await requestUtil.post('approval/list', {
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      status: searchForm.value.status
    })
    console.log('审批列表响应:', result.data)
    if (result.data.code === 200) {
      approvalList.value = result.data.approvalList
      total.value = result.data.total
      console.log('审批列表数据:', approvalList.value)
    } else {
      ElMessage.error(result.data.msg || '获取审批列表失败')
    }
  } catch (error) {
    console.error('请求审批列表出错:', error)
    console.error('错误详情:', error.response)
    ElMessage.error('请求失败：' + (error.response?.data?.msg || error.message))
  }
}

const resetSearch = () => {
  searchForm.value.status = null
  pageNum.value = 1
  initApprovalList()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  initApprovalList()
}

const handleCurrentChange = (val) => {
  pageNum.value = val
  initApprovalList()
}

// 通过
const handleApprove = (id) => {
  approveForm.value.id = id
  approveForm.value.action = 'approve'
  approveForm.value.remark = ''
  approveDialogVisible.value = true
}

// 拒绝
const handleReject = (id) => {
  approveForm.value.id = id
  approveForm.value.action = 'reject'
  approveForm.value.remark = ''
  approveDialogVisible.value = true
}

// 确认审批
const confirmApprove = async () => {
  const result = await requestUtil.post('approval/process', approveForm.value)
  if (result.data.code === 200) {
    ElMessage.success(result.data.msg)
    approveDialogVisible.value = false
    initApprovalList()
  } else {
    ElMessage.error(result.data.msg)
  }
}

// 撤销
const handleCancel = (id) => {
  ElMessageBox.confirm('确定要撤销此审批申请吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const result = await requestUtil.post('approval/cancel', { id })
    if (result.data.code === 200) {
      ElMessage.success('撤销成功')
      initApprovalList()
    } else {
      ElMessage.error(result.data.msg)
    }
  })
}

// 查看详情
const showDetail = (row) => {
  currentApproval.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  initApprovalList()
})
</script>

<style scoped>
</style>
