<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

<template>
  <div class="notification-bell">
    <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99">
      <el-icon @click="showNotifications" class="bell-icon">
        <Bell />
      </el-icon>
    </el-badge>

    <!-- 通知下拉面板 -->
    <el-popover
      v-model:visible="popoverVisible"
      placement="bottom-end"
      :width="350"
      trigger="click"
    >
      <template #reference>
        <div style="display: none;"></div>
      </template>

      <div class="notification-panel">
        <div class="panel-header">
          <span>消息通知</span>
          <el-button link type="primary" size="small" @click="markAllRead">全部已读</el-button>
        </div>
        
        <el-scrollbar style="height: 300px;">
          <div v-if="notifications.length === 0" class="empty-tip">
            暂无消息
          </div>
          <div
            v-for="item in notifications"
            :key="item.id"
            class="notification-item"
            :class="{ unread: item.status === 0 }"
            @click="handleNotificationClick(item)"
          >
            <div class="item-title">{{ item.title }}</div>
            <div class="item-content">{{ item.content }}</div>
            <div class="item-time">{{ item.create_time }}</div>
          </div>
        </el-scrollbar>

        <div class="panel-footer">
          <el-button link type="primary" @click="goToNotificationPage">查看全部消息</el-button>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/util/request'

const router = useRouter()
const unreadCount = ref(0)
const notifications = ref([])
const popoverVisible = ref(false)
let pollTimer = null

const loadUnreadCount = async () => {
  try {
    const res = await request.get('/notification/unread-count')
    if (res.data.code === 200) {
      unreadCount.value = res.data.data.count
    }
  } catch (error) {
    console.error('获取未读数量失败')
  }
}

const loadNotifications = async () => {
  try {
    const res = await request.get('/notification/list', { params: { page: 1, pageSize: 5 } })
    if (res.data.code === 200) {
      notifications.value = res.data.data
    }
  } catch (error) {
    console.error('获取通知列表失败')
  }
}

const showNotifications = () => {
  popoverVisible.value = true
  loadNotifications()
}

const handleNotificationClick = (item) => {
  if (item.status === 0) {
    markAsRead(item.id)
  }
  popoverVisible.value = false
}

const markAsRead = async (id) => {
  try {
    await request.post('/notification/mark-read', { id })
    loadUnreadCount()
    loadNotifications()
  } catch (error) {
    console.error('标记已读失败')
  }
}

const markAllRead = async () => {
  try {
    await request.post('/notification/mark-read', {})
    ElMessage.success('已全部标记为已读')
    loadUnreadCount()
    loadNotifications()
  } catch (error) {
    console.error('标记全部已读失败')
  }
}

const goToNotificationPage = () => {
  popoverVisible.value = false
  router.push('/sys/notification')
}

onMounted(() => {
  loadUnreadCount()
  // 每30秒轮询一次未读数量
  pollTimer = setInterval(loadUnreadCount, 30000)
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})
</script>

<style scoped>
.notification-bell {
  display: flex;
  align-items: center;
}

.bell-icon {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.bell-icon:hover {
  color: #409eff;
}

.notification-panel {
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid #ebeef5;
    font-weight: 600;
  }

  .empty-tip {
    text-align: center;
    padding: 40px 0;
    color: #909399;
  }

  .notification-item {
    padding: 12px;
    border-bottom: 1px solid #f2f6fc;
    cursor: pointer;
    transition: background 0.3s;

    &:hover {
      background: #f5f7fa;
    }

    &.unread {
      background: #ecf5ff;
    }

    .item-title {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      margin-bottom: 4px;
    }

    .item-content {
      font-size: 12px;
      color: #606266;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .item-time {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }

  .panel-footer {
    padding: 12px;
    text-align: center;
    border-top: 1px solid #ebeef5;
  }
}
</style>
