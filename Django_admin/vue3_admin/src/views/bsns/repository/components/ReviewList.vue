<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="review-list-container">
    <div class="review-header">
      <h3>复盘记录</h3>
      <el-button type="primary" @click="showAddReviewDialog">添加复盘</el-button>
    </div>
    
    <el-divider />

    <div v-if="reviews.length === 0" class="empty-state">
      <el-empty description="暂无复盘记录" />
    </div>

    <div v-else class="reviews">
      <div v-for="review in reviews" :key="review.id" class="review-card">
        <div class="review-header-info">
          <div class="reviewer-info">
            <span class="reviewer-name">{{ review.reviewer_name }}</span>
            <span class="review-date">{{ review.review_date_formatted }}</span>
          </div>
          <div class="review-actions">
            <el-button v-if="canEdit(review)" size="small" @click="showEditReviewDialog(review)">编辑</el-button>
            <el-popconfirm
              v-if="canEdit(review)"
              title="确定要删除这条复盘记录吗？"
              @confirm="deleteReview(review.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>

        <div class="review-content">
          <div class="review-section">
            <h4>发生了什么</h4>
            <p>{{ review.what_happened }}</p>
          </div>

          <div class="review-section">
            <h4>做得好的地方</h4>
            <p>{{ review.what_went_well }}</p>
          </div>

          <div class="review-section">
            <h4>需要改进的地方</h4>
            <p>{{ review.what_not_went_well }}</p>
          </div>

          <div class="review-section">
            <h4>学到的经验</h4>
            <p>{{ review.lessons_learned }}</p>
          </div>

          <div class="review-section">
            <h4>行动计划与方案</h4>
            <p>{{ review.action_items }}</p>
          </div>

          <div class="review-ratings">
            <div class="rating-item">
              <span class="label">有效性评分:</span>
              <el-rate v-model="review.effectiveness_score" disabled show-score />
            </div>
            <div class="rating-item">
              <span class="label">改进潜力评分:</span>
              <el-rate v-model="review.improvement_potential" disabled show-score />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页组件 -->
    <div class="pagination-container" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 复盘对话框 -->
    <ReviewDialog
      ref="reviewDialogRef"
      :repository-id="repositoryId"
      :review-data="currentReview"
      @success="loadReviews"
      @close="currentReview = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ReviewDialog from './ReviewDialog.vue'
import { getReviewList, deleteReview as apiDeleteReview } from '@/views/bsns/repository/api'

const props = defineProps({
  repositoryId: {
    type: Number,
    required: true
  }
})

const reviews = ref([])
const currentReview = ref(null)
const reviewDialogRef = ref()

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取当前登录用户信息
const currentUser = computed(() => {
  const userStr = window.sessionStorage.getItem('currentUser')
  return userStr ? JSON.parse(userStr) : null
})

// 判断是否可以编辑/删除某条复盘记录
const canEdit = (review) => {
  if (!currentUser.value) return false
  return review.reviewer === currentUser.value.id
}

// 加载复盘列表
const loadReviews = async (page = 1, size = 10) => {
  try {
    console.log('开始加载复盘列表，repositoryId:', props.repositoryId, '页码:', page, '每页:', size)
    
    const result = await getReviewList(props.repositoryId, page, size)
    console.log('获取复盘列表结果:', result)
    
    // 检查响应结构并处理数据
    let responseData = null
    if (result.data && result.data.code === 200) {
      // 处理Axios响应结构
      responseData = result.data
      reviews.value = responseData.review_list || []
      total.value = responseData.total || 0
      currentPage.value = responseData.page || 1
      pageSize.value = responseData.page_size || 10
    } else if (result.code === 200) {
      // 如果直接是后端返回的格式
      responseData = result
      reviews.value = responseData.review_list || []
      total.value = responseData.total || 0
      currentPage.value = responseData.page || 1
      pageSize.value = responseData.page_size || 10
    } else {
      // 即使获取失败，也显示空列表，不显示错误消息
      reviews.value = []
      total.value = 0
      console.log('获取复盘列表失败，显示空列表')
    }
    
    console.log('加载的复盘记录数:', reviews.value.length, '总数:', total.value)
  } catch (error) {
    console.error('加载复盘列表失败:', error)
    // 出现异常时也显示空列表，不显示错误消息
    reviews.value = []
    total.value = 0
  }
}

// 页码变化处理
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadReviews(page, pageSize.value)
}

// 每页大小变化处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1  // 重置到第一页
  loadReviews(1, size)
}

// 显示添加复盘对话框
const showAddReviewDialog = () => {
  currentReview.value = null
  if (reviewDialogRef.value) {
    reviewDialogRef.value.showDialog()
  }
}

// 显示编辑复盘对话框
const showEditReviewDialog = (review) => {
  currentReview.value = review
  if (reviewDialogRef.value) {
    reviewDialogRef.value.showDialog(review)
  }
}

// 删除复盘
const deleteReview = async (reviewId) => {
  try {
    const result = await apiDeleteReview({ id: reviewId })
    if (result.code === 200) {
      ElMessage.success(result.msg || '复盘删除成功')
      // 如果删除后当前页为空且不是第一页，则跳转到上一页
      if (reviews.value.length === 1 && currentPage.value > 1) {
        currentPage.value -= 1
      }
      loadReviews(currentPage.value, pageSize.value) // 重新加载当前页列表
    } else {
      ElMessage.error(result.msg || '复盘删除失败')
    }
  } catch (error) {
    console.error('删除复盘失败:', error)
    ElMessage.error('删除复盘失败，请重试')
  }
}

// 监听repositoryId变化并重新加载数据
watch(
  () => props.repositoryId,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      // 重新加载数据
      loadReviews();
    }
  },
  { immediate: false }
);

// 组件挂载时加载数据
onMounted(() => {
  loadReviews()
})
</script>

<style scoped>
.review-list-container {
  padding: 20px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.review-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.review-header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.reviewer-info {
  display: flex;
  flex-direction: column;
}

.reviewer-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.review-date {
  color: #909399;
  font-size: 12px;
}

.review-actions {
  display: flex;
  gap: 8px;
}

.review-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-section {
  margin-bottom: 10px;
}

.review-section h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.review-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

.review-ratings {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.rating-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-weight: 500;
  color: #606266;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #909399;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>