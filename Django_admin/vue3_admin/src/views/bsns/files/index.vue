<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>文件上传</span>
        </div>
      </template>
      
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        :action="uploadUrl"
        :headers="getHeaders()"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :on-change="handleFileChange"
        :file-list="fileList"
        multiple
        :limit="5"
        :auto-upload="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持单个或批量上传，支持扩展名：.jpg, .jpeg, .png, .gif, .pdf, .doc, .docx, .xls, .xlsx, .txt
          </div>
        </template>
      </el-upload>
      
      <div class="upload-controls" style="margin-top: 20px;">
        <el-button type="primary" @click="submitUpload">开始上传</el-button>
        <el-button @click="clearFiles">清空列表</el-button>
      </div>
    </el-card>

    <!-- 文件列表 -->
    <el-card class="file-list-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>已上传文件</span>
          <span style="color: #909399; font-size: 14px; font-weight: normal; margin-left: 10px;">
            (共 {{ totalFiles }} 个文件)
          </span>
        </div>
      </template>
      
      <el-table :data="uploadedFiles" style="width: 100%" :height="500">
        <el-table-column prop="original_filename" label="文件名" min-width="250">
          <template #default="{ row }">
            <div class="file-info">
              <el-icon><document /></el-icon>
              <span class="file-name" @click="downloadFile(row)" style="cursor: pointer; color: #409EFF;">{{ row.original_filename }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="uploader_name" label="上传人" min-width="120" align="center">
          <template #default="{ row }">
            {{ row.uploader_name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" min-width="100" align="center">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="downloadFile(row)" :icon="Download">下载</el-button>
            <el-popconfirm 
              v-if="canDelete(row)"
              title="确定要删除这个文件吗？" 
              @confirm="deleteFile(row)">
              <template #reference>
                <el-button type="danger" size="small" :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="uploadedFiles.length === 0" class="empty-state">
        <el-empty description="暂无上传文件" />
      </div>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalFiles"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document, Download, Delete } from '@element-plus/icons-vue'
import requestUtil from '@/util/request'

// 数据
const uploadRef = ref(null)
const uploadUrl = ref('/files/upload')
const fileList = ref([])
const uploadedFiles = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalFiles = ref(0)

// 获取当前用户信息
const currentUser = JSON.parse(sessionStorage.getItem("currentUser") || "{}")

// 动态获取headers（每次都从sessionStorage读取最新token）
const getHeaders = () => {
  return {
    'Authorization': `Bearer ${sessionStorage.getItem('token') || ''}`
  }
}

// 判断是否可以删除文件
const canDelete = (file) => {
  // 管理员可以删除所有文件
  if (currentUser.username === 'admin') {
    return true
  }
  // 文件上传者可以删除自己的文件
  if (file.uploader === currentUser.id) {
    return true
  }
  return false
}

// 方法
const handleFileChange = (file, fileListParam) => {
  // 当文件列表发生变化时更新fileList
  fileList.value = fileListParam
}
const beforeUpload = (file) => {
  const allowedTypes = [
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
    'application/pdf',
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain'
  ]
  
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('文件类型不支持！')
    return false
  }
  
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB！')
    return false
  }
  
  return true
}

const handleUploadSuccess = (response, file, fileList) => {
  ElMessage.success('文件上传成功！')
  loadUploadedFiles()
}

const handleUploadError = (error, file, fileList) => {
  ElMessage.error('文件上传失败！')
  console.error('Upload error:', error)
}

const submitUpload = () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件！')
    return
  }
  
  // 使用Promise.all来等待所有文件上传完成
  const uploadPromises = fileList.value.map(fileObj => {
    const formData = new FormData()
    formData.append('file', fileObj.raw)
    formData.append('user_id', currentUser.id || 0)
    
    return requestUtil.fileUpload('/files/upload/', formData)
      .then(response => {
        // 后端返回201状态码表示创建成功
        if (response.data.code === 200 || response.status === 201) {
          return { success: true, name: fileObj.name }
        } else {
          return { success: false, name: fileObj.name, error: response.data.msg }
        }
      })
      .catch(error => {
        return { success: false, name: fileObj.name, error: error.message }
      })
  })
  
  Promise.all(uploadPromises).then(results => {
    const successCount = results.filter(r => r.success).length
    const failCount = results.length - successCount
    
    if (successCount > 0) {
      ElMessage.success(`成功上传 ${successCount} 个文件`)
      loadUploadedFiles()
      clearFiles()
    }
    
    if (failCount > 0) {
      ElMessage.warning(`${failCount} 个文件上传失败`)
    }
  })
}

const clearFiles = () => {
  fileList.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const loadUploadedFiles = async () => {
  try {
    // 检查token是否存在
    const token = sessionStorage.getItem('token')
    if (!token) {
      ElMessage.warning('请先登录')
      return
    }
    
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await requestUtil.get('/files/list/', params)
    if (response.data.code === 200) {
      uploadedFiles.value = response.data.file_list || []
      totalFiles.value = response.data.total || 0
    } else {
      // Show error only for actual API errors, not for empty results
      if (response.data.msg && !response.data.msg.includes('无数据')) {
        ElMessage.error(response.data.msg || '获取文件列表失败')
      }
    }
  } catch (error) {
    // Show error only for network or server errors
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      // 不需要手动跳转，request.js的拦截器会处理
    } else if (error.response) {
      ElMessage.error('服务器错误: ' + (error.response.data?.msg || error.response.statusText))
    } else if (error.request) {
      ElMessage.error('网络错误，请检查连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    // Set empty arrays to clear any previous data
    uploadedFiles.value = []
    totalFiles.value = 0
  }
}

const downloadFile = async (file) => {
  try {
    const token = sessionStorage.getItem('token')
    if (!token) {
      ElMessage.warning('请先登录')
      return
    }
    
    // 使用axios下载，携带token
    const response = await requestUtil.get(`/files/download/${file.id}`, {}, { responseType: 'blob' })
    
    // 创建blob链接并触发下载
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', file.original_filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error('下载失败: ' + (error.response?.data?.msg || error.message))
    }
  }
}

const deleteFile = async (file) => {
  try {
    const response = await requestUtil.delete(`/files/delete/${file.id}/`)
    if (response.data.code === 200) {
      ElMessage.success('文件删除成功！')
      loadUploadedFiles()
    } else {
      ElMessage.error('文件删除失败')
    }
  } catch (error) {
    console.error('Delete file error:', error)
    ElMessage.error('文件删除失败')
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  switch (status) {
    case '已上传': return 'success'
    case '处理中': return 'warning'
    case '已删除': return 'info'
    default: return 'danger'
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadUploadedFiles()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadUploadedFiles()
}

// 初始化
onMounted(() => {
  loadUploadedFiles()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.upload-card {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
}

.upload-demo {
  text-align: center;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name {
  word-break: break-all;
}

.file-name:hover {
  text-decoration: underline;
}

.file-list-card {
  margin: 0 auto;
  min-height: 600px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.upload-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

:deep(.el-pagination) {
  margin-top: 20px;
  justify-content: center;
}
</style>