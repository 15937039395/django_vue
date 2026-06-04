<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

<template>
  <div class="notification-container">
    <el-card class="notification-card">
      <template #header>
        <div class="card-header">
          <span>消息通知</span>
          <div class="header-actions">
            <el-button @click="loadNotifications" :icon="Refresh" plain>刷新</el-button>
            <el-button type="primary" @click="markAllRead" plain>全部已读</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-radio-group v-model="filterStatus" @change="handleFilterChange">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button :label="0">未读</el-radio-button>
          <el-radio-button :label="1">已读</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 通知列表 -->
      <el-table :data="notifications" v-loading="loading" stripe border style="width: 100%">
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 0 ? 'warning' : 'info'" effect="plain">
              {{ row.status_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" align="center" />
        <el-table-column prop="read_time" label="阅读时间" width="170" align="center">
          <template #default="{ row }">{{ row.read_time }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 0"
              type="primary"
              size="small"
              @click="markAsRead(row.id)"
            >
              标记已读
            </el-button>
            <el-button type="danger" size="small" @click="deleteNotification(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import request from '@/util/request'

const notifications = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterStatus = ref('')

const typeMap = {
  'event': '事件通知',
  'system': '系统通知',
  'approval': '审批通知',
}

const getTypeText = (type) => {
  return typeMap[type] || type
}

const loadNotifications = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
    }
    if (filterStatus.value !== '') {
      params.status = filterStatus.value
    }
    
    const res = await request.get('/notification/list', { params })
    if (res.data.code === 200) {
      notifications.value = res.data.data
      total.value = res.data.total
    }
  } catch (error) {
    ElMessage.error('加载通知列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadNotifications()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadNotifications()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadNotifications()
}

const markAsRead = async (id) => {
  try {
    const res = await request.post('/notification/mark-read', { id })
    if (res.data.code === 200) {
      ElMessage.success('已标记为已读')
      loadNotifications()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const markAllRead = async () => {
  try {
    await ElMessageBox.confirm('确定要将所有消息标记为已读吗？', '提示', {
      type: 'warning',
    })
    
    const res = await request.post('/notification/mark-read', {})
    if (res.data.code === 200) {
      ElMessage.success('已全部标记为已读')
      loadNotifications()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const deleteNotification = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
      type: 'warning',
    })
    
    const res = await request.post('/notification/delete', { id })
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      loadNotifications()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadNotifications()
})
</script>

<style lang="scss" scoped>
.notification-container {
  padding: 20px;

  .notification-card {
    border-radius: 8px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;

      .header-actions {
        display: flex;
        gap: 10px;
      }
    }

    .filter-bar {
      margin-bottom: 20px;
    }

    .pagination-container {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>
