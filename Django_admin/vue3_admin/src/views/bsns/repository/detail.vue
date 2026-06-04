<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-page-header @back="goBack" content="知识库详情" />
    <div class="detail-content">
      <el-card v-loading="loading">
        <el-descriptions title="知识库信息" :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="repositoryData.is_temp ? 'warning' : repositoryData.confirmed ? 'success' : 'info'">
              {{ repositoryData.status_text || '正常' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="点赞数">
            {{ repositoryData.upvote || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="部门名称">
            {{ repositoryData.dept_name || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="用户名">
            {{ repositoryData.user_name || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="事件名称">
            {{ repositoryData.event_name || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="事件编号">
            {{ repositoryData.event_number || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ repositoryData.principal || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="事件发生时间">
            {{ repositoryData.event_occur_time_formatted || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="发生地点">
            {{ repositoryData.address || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            {{ repositoryData.types_text || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            {{ repositoryData.classify_name || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="标题" :span="2">
            <strong>{{ repositoryData.title || '暂无数据' }}</strong>
          </el-descriptions-item>
          <el-descriptions-item label="内容" :span="2">
            <div class="content-html" v-html="repositoryData.content || '暂无数据'" style="min-height: 100px; padding: 15px; border: 1px solid #ebeef5; border-radius: 4px; background-color: #fafafa; line-height: 1.8; user-select: text;" @click="handleImageClick" />
            <!-- 图片预览对话框 -->
            <el-dialog v-model="imagePreviewVisible" :title="'图片预览'" width="80%" top="5vh" :destroy-on-close="true" append-to-body>
              <img :src="previewImageUrl" alt="预览图片" style="width: 100%; height: auto; max-height: 70vh; object-fit: contain;" />
            </el-dialog>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ repositoryData.remark || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(repositoryData.create_time) || '暂无数据' }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(repositoryData.update_time) || '暂无数据' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 关联事件区域 -->
    <div class="associated-events-section" style="margin-top: 20px;">
      <el-card v-if="associatedEvents.length > 0">
        <template #header>
          <div class="card-header">
            <span style="font-weight: bold;">关联事件</span>
          </div>
        </template>
        <div class="events-list">
          <el-table :data="associatedEvents" style="width: 100%" @row-click="goToEventDetail">
            <el-table-column prop="event_number" label="事件编号" min-width="150" />
            <el-table-column prop="event_name" label="事件名称" min-width="200" />
            <el-table-column prop="principal" label="负责人" min-width="100" />
            <el-table-column prop="start_date" label="开始日期" min-width="100" />
            <el-table-column prop="end_date" label="结束日期" min-width="100" />
            <el-table-column prop="status" label="状态" min-width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === '正常' ? 'success' : 'danger'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 相关条目列表 -->
          <div v-if="hasRelatedEntries" style="margin-top: 20px;">
            <h4>相关知识库条目：</h4>
            <el-table :data="filteredRelatedEntries" style="width: 100%">
              <el-table-column prop="title" label="标题" min-width="150" />
              <el-table-column prop="maintainer" label="维护人" width="240" />
              <el-table-column prop="create_time" label="创建时间" width="300" />
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button type="primary" link @click="showRelatedEntryDetail(row)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 相关条目分页组件 -->
            <div class="related-entries-pagination" style="margin-top: 20px; display: flex; justify-content: center;">
              <el-pagination
                v-model:current-page="relatedEntriesCurrentPage"
                v-model:page-size="relatedEntriesPageSize"
                :page-sizes="[5, 10, 20, 50]"
                :background="true"
                layout="total, sizes, prev, pager, next, jumper"
                :total="relatedEntriesTotalCount"
                @size-change="handleRelatedEntriesSizeChange"
                @current-change="handleRelatedEntriesCurrentChange"
              />
            </div>
          </div>
          
          <!-- 相关条目详情弹窗 -->
          <el-dialog v-model="relatedEntryDialogVisible" title="知识库条目详情" width="80%" top="5vh" :destroy-on-close="true">
            <el-card v-if="selectedRelatedEntryFullData">
              <el-descriptions title="知识库信息" :column="2" border>
                <el-descriptions-item label="状态">
                  <el-tag :type="selectedRelatedEntryFullData.is_temp ? 'warning' : selectedRelatedEntryFullData.confirmed ? 'success' : 'info'">
                    {{ selectedRelatedEntryFullData.status_text || '正常' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="点赞数">
                  {{ selectedRelatedEntryFullData.upvote || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="部门名称">
                  {{ selectedRelatedEntryFullData.dept_name || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="用户名">
                  {{ selectedRelatedEntryFullData.user_name || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="事件名称">
                  {{ selectedRelatedEntryFullData.event_name || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="事件编号">
                  {{ selectedRelatedEntryFullData.event_number || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="负责人">
                  {{ selectedRelatedEntryFullData.principal || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="事件发生时间">
                  {{ selectedRelatedEntryFullData.event_occur_time_formatted || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="发生地点">
                  {{ selectedRelatedEntryFullData.address || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="类型">
                  {{ selectedRelatedEntryFullData.types_text || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="分类">
                  {{ selectedRelatedEntryFullData.classify_name || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="标题" :span="2">
                  <strong>{{ selectedRelatedEntryFullData.title || '暂无数据' }}</strong>
                </el-descriptions-item>
                <el-descriptions-item label="内容" :span="2">
                  <div class="content-html" v-html="selectedRelatedEntryFullData.content || '暂无数据'" style="min-height: 100px; padding: 15px; border: 1px solid #ebeef5; border-radius: 4px; background-color: #fafafa; line-height: 1.8; user-select: text;" />
                </el-descriptions-item>
                <el-descriptions-item label="备注" :span="2">
                  {{ selectedRelatedEntryFullData.remark || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  {{ formatDateTime(selectedRelatedEntryFullData.create_time) || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="更新时间">
                  {{ formatDateTime(selectedRelatedEntryFullData.update_time) || '暂无数据' }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="relatedEntryDialogVisible = false">关闭</el-button>
                <el-button type="primary" @click="goToRelatedEntry(selectedRelatedEntry)">查看完整详情</el-button>
              </span>
            </template>
          </el-dialog>
        </div>
      </el-card>
    </div>

    <!-- 复盘区域 -->
    <div class="review-section" style="margin-top: 20px;">
      <el-card>
        <template #header>
          <div class="card-header">
            <span style="font-weight: bold;">复盘</span>
          </div>
        </template>
        <ReviewList :repository-id="Number(route.params.id)" />
      </el-card>
    </div>

    <!-- 评论区域 -->
    <div class="comment-section" style="margin-top: 20px;">
      <el-card>
        <template #header>
          <div class="card-header">
            <span style="font-weight: bold;">评论 ({{ commentList.length }})</span>
          </div>
        </template>
        
        <!-- 评论输入框 -->
        <div class="comment-input" style="margin-bottom: 20px;">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="3"
            placeholder="请输入您的评论..."
            maxlength="500"
            show-word-limit
          />
          <div style="text-align: right; margin-top: 10px;">
            <el-button type="primary" :loading="submitLoading" @click="submitComment">发表评论</el-button>
          </div>
        </div>
        
        <!-- 评论列表 -->
        <div v-loading="commentsLoading" class="comment-list">
          <div v-for="comment in structuredComments" :key="comment.id" class="comment-item" style="margin-bottom: 20px; border-bottom: 1px solid #f0f0f0; padding-bottom: 15px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
              <el-avatar :size="32" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" style="margin-right: 12px;" />
              <div style="flex: 1;">
                <span style="font-weight: 500; color: #333;">{{ comment.user_name }}</span>
                <span v-if="comment.reply_to_user_name" style="margin-left: 8px; font-size: 13px; color: #666;">
                  回复 <span style="color: #409eff;">@{{ comment.reply_to_user_name }}</span>
                </span>
                <span style="margin-left: 12px; color: #999; font-size: 12px;">{{ comment.create_time }}</span>
              </div>
              <el-button type="primary" link @click="handleReply(comment)">回复</el-button>
            </div>
            <div style="padding-left: 44px; color: #666; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;">{{ comment.content }}</div>
            
            <!-- 回复输入框 -->
            <div v-if="replyingTo && replyingTo.id === comment.id" style="margin: 15px 0 0 44px; padding: 15px; background-color: #f9f9f9; border-radius: 4px;">
              <div style="margin-bottom: 10px; font-size: 13px; color: #666;">
                回复 <span style="color: #409eff;">@{{ replyingTo.user_name }}</span>:
                <el-button type="info" link @click="cancelReply" style="float: right;">取消</el-button>
              </div>
              <el-input
                v-model="replyComment"
                type="textarea"
                :rows="2"
                :placeholder="'回复 @' + replyingTo.user_name + '...'"
                maxlength="500"
                show-word-limit
              />
              <div style="text-align: right; margin-top: 10px;">
                <el-button type="primary" size="small" :loading="submitLoading" @click="submitReply">发表回复</el-button>
              </div>
            </div>

            <!-- 子回复列表 (如果有的话) -->
            <div v-if="comment.replies && comment.replies.length > 0" style="margin: 15px 0 0 44px; border-left: 2px solid #e0e0e0; padding-left: 15px;">
              <div v-for="reply in comment.replies" :key="reply.id" style="margin-bottom: 15px;">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                  <span style="font-weight: 500; color: #333; font-size: 14px;">{{ reply.user_name }}</span>
                  <span style="margin-left: 8px; font-size: 13px; color: #666;">
                    回复 <span style="color: #409eff;">@{{ reply.reply_to_user_name }}</span>
                  </span>
                  <span style="margin-left: 10px; color: #999; font-size: 12px;">{{ reply.create_time }}</span>
                  <el-button type="primary" link size="small" @click="handleReply(reply)" style="margin-left: 10px;">回复</el-button>
                </div>
                <div style="color: #666; line-height: 1.5; font-size: 14px; white-space: pre-wrap; word-wrap: break-word;">{{ reply.content }}</div>
                
                <!-- 孙子回复框 -->
                <div v-if="replyingTo && replyingTo.id === reply.id" style="margin-top: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 4px;">
                  <div style="margin-bottom: 8px; font-size: 12px; color: #666;">
                    回复 <span style="color: #409eff;">@{{ replyingTo.user_name }}</span>:
                    <el-button type="info" link @click="cancelReply" style="float: right;">取消</el-button>
                  </div>
                  <el-input
                    v-model="replyComment"
                    type="textarea"
                    :rows="2"
                    :placeholder="'回复 @' + replyingTo.user_name + '...'"
                    maxlength="500"
                    show-word-limit
                  />
                  <div style="text-align: right; margin-top: 10px;">
                    <el-button type="primary" size="small" :loading="submitLoading" @click="submitReply">发表回复</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-if="commentList.length === 0" description="暂无评论，快来抢沙发吧~" />
        </div>
        
        <!-- 评论分页组件 -->
        <div class="pagination-container" v-if="totalComments > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20, 50]"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalComments"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  <!-- 自定义返回顶部按钮 -->
  <div 
    v-if="showBackTop" 
    class="back-top-btn" 
    @click="scrollToTop"
    :style="{ right: '50px', bottom: '50px' }"
  >
    <span class="back-top-icon">↑</span>
    <span>顶部</span>
  </div>
</div>
</template>


<script setup>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElBacktop } from "element-plus"
import { ArrowUp } from '@element-plus/icons-vue'
import requestUtil from '@/util/request'
import ReviewList from './components/ReviewList.vue'

const router = useRouter()


const route = useRoute()

const repositoryData = ref({})
const loading = ref(false)
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')
const associatedEvents = ref([])
const relatedEntries = ref([])
const paginatedRelatedEntries = ref([])
const hasRelatedEntries = computed(() => {
  return relatedEntries.value && relatedEntries.value.length > 0;
})

// 相关条目分页相关
const relatedEntriesCurrentPage = ref(1)
const relatedEntriesPageSize = ref(10)
const relatedEntriesTotal = ref(0)

// 计算属性：根据当前页和页面大小过滤相关条目
const filteredRelatedEntries = computed(() => {
  if (!relatedEntries.value || relatedEntries.value.length === 0) {
    return []
  }
  
  const startIndex = (relatedEntriesCurrentPage.value - 1) * relatedEntriesPageSize.value
  const endIndex = startIndex + relatedEntriesPageSize.value
  
  return relatedEntries.value.slice(startIndex, endIndex)
})

// 计算总条数
const relatedEntriesTotalCount = computed(() => {
  return relatedEntries.value?.length || 0
})

// 相关条目详情弹窗相关
const relatedEntryDialogVisible = ref(false)
const selectedRelatedEntry = ref(null)
const selectedRelatedEntryFullData = ref(null)

const currentUser = JSON.parse(sessionStorage.getItem("currentUser") || "{}")
const commentList = ref([])
const newComment = ref('')
const replyingTo = ref(null)
const replyComment = ref('')
const commentsLoading = ref(false)
const submitLoading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const totalComments = ref(0)

// 构建树形评论结构
const structuredComments = computed(() => {
  const map = {}
  const roots = []
  
  // 先把所有评论放进 map
  commentList.value.forEach(comment => {
    map[comment.id] = { ...comment, replies: [] }
  })
  
  // 建立父子关系
  commentList.value.forEach(comment => {
    if (comment.parent && map[comment.parent]) {
      map[comment.parent].replies.push(map[comment.id])
    } else if (!comment.parent) {
      roots.push(map[comment.id])
    }
  })
  
  return roots
})

const getDetail = async () => {
  const id = route.params.id

  if (!id) {
    ElMessage.error('缺少知识库ID参数')
    return
  }

  try {
    loading.value = true
    const res = await requestUtil.get(`repository/detail?id=${id}`)
    if (res.data.code === 200) {
      repositoryData.value = res.data.item_data || {}
    } else {
      ElMessage.error(res.data.msg || '获取详情失败')
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  } finally {
    loading.value = false
    // 获取关联事件
    getAssociatedEvents()
  }
}

const getAssociatedEvents = async () => {
  const id = route.params.id

  if (!id) {
    return
  }

  try {
    const res = await requestUtil.get(`repository/associated-events?id=${id}`)
    if (res.data.code === 200) {
      associatedEvents.value = res.data.associated_events || []
      
      // 提取相关条目
      if (associatedEvents.value.length > 0 && associatedEvents.value[0].related_entries) {
        relatedEntries.value = associatedEvents.value[0].related_entries || [];
        // 重置分页到第一页
        relatedEntriesCurrentPage.value = 1;
      } else {
        relatedEntries.value = [];
      }
    } else {
      console.error('获取关联事件失败:', res.data.msg)
      relatedEntries.value = [];
    }
  } catch (error) {
    console.error('获取关联事件失败:', error)
    relatedEntries.value = [];
  }
}

const goToEventDetail = (event) => {
  // 跳转到事件详情页面
  // 尝试导航到事件管理页面
  try {
    // 尝试跳转到事件详情页面
    router.push({
      path: `/bsns/event/detail`,
      query: { id: event.id }
    }).catch(err => {
      console.error('路由跳转失败:', err);
      // 如果标准跳转失败，尝试备用方案
      ElMessage.warning('无法直接跳转，请手动导航到事件详情页');
    });
  } catch (err) {
    console.error('跳转事件详情页时出错:', err);
    ElMessage.error('跳转事件详情页失败');
  }
}

const showRelatedEntryDetail = async (entry) => {
  // 显示相关条目详情弹窗
  try {
    // 获取知识库条目的详细内容
    const res = await requestUtil.get(`repository/detail?id=${entry.id}`)
    if (res.data.code === 200) {
      selectedRelatedEntry.value = entry
      selectedRelatedEntryFullData.value = res.data.item_data
      relatedEntryDialogVisible.value = true
    } else {
      ElMessage.error('获取知识库详情失败')
    }
  } catch (error) {
    console.error('获取知识库详情失败:', error)
    ElMessage.error('获取知识库详情失败')
  }
}

const goToRelatedEntry = (entry) => {
  // 跳转到相关知识库条目的详情页面
  try {
    // 尝试多种方式获取目标ID
    let targetId = null;
    
    // 优先使用传入的entry的id
    if (entry && entry.id) {
      targetId = entry.id;
    } 
    // 其次使用selectedRelatedEntry的id
    else if (selectedRelatedEntry.value && selectedRelatedEntry.value.id) {
      targetId = selectedRelatedEntry.value.id;
    }
    // 最后尝试使用entry的其他可能字段
    else if (entry && entry.repositoryId) {
      targetId = entry.repositoryId;
    }
    
    if (!targetId) {
      ElMessage.error('无法获取目标页面ID');
      return;
    }
    
    router.push({
      path: `/bsns/repository/detail/${targetId}`,
      query: { id: targetId }
    }).catch(err => {
      console.error('路由跳转失败:', err);
      ElMessage.warning('无法直接跳转，请手动导航到知识库详情页');
    });
    // 关闭弹窗
    relatedEntryDialogVisible.value = false
  } catch (err) {
    console.error('跳转相关条目详情页时出错:', err);
    ElMessage.error('跳转相关条目详情页失败');
  }
}

const getComments = async (page = 1, size = 10) => {
  const id = route.params.id
  try {
    commentsLoading.value = true
    // 将当前用户的角色ID和用户ID传给后端，用于判断是否显示完整姓名
    const roleId = currentUser.role_id || 0
    const userId = currentUser.id || 0
    const res = await requestUtil.get(`repository/comment/list?id=${id}&role_id=${roleId}&user_id=${userId}&page=${page}&page_size=${size}`)
    if (res.data.code === 200) {
      commentList.value = res.data.comment_list || []
      // 更新分页信息
      currentPage.value = res.data.page || 1
      pageSize.value = res.data.page_size || 10
      totalComments.value = res.data.total || 0
    }
  } catch (error) {
    console.error('获取评论失败:', error)
  } finally {
    commentsLoading.value = false
  }
}

// 页码变化处理
const handleCurrentChange = (page) => {
  currentPage.value = page
  getComments(page, pageSize.value)
}

// 每页大小变化处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1  // 重置到第一页
  getComments(1, size)
}

// 相关条目分页变化处理
const handleRelatedEntriesSizeChange = (size) => {
  relatedEntriesPageSize.value = size
  relatedEntriesCurrentPage.value = 1  // 重置到第一页
}

const handleRelatedEntriesCurrentChange = (page) => {
  relatedEntriesCurrentPage.value = page
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  
  const id = route.params.id
  try {
    submitLoading.value = true
    const res = await requestUtil.post('repository/comment/submit', {
      id: Number(id),
      user_id: currentUser.id,
      content: newComment.value
    })
    if (res.data.code === 200) {
      ElMessage.success('评论成功')
      newComment.value = ''
      getComments(currentPage.value, pageSize.value) // 刷新评论列表
    } else {
      ElMessage.error(res.data.msg || '评论失败')
    }
  } catch (error) {
    console.error('提交评论失败:', error)
    ElMessage.error('提交评论失败')
  } finally {
    submitLoading.value = false
  }
}

const handleReply = (comment) => {
  replyingTo.value = comment
  replyComment.value = ''
}

const cancelReply = () => {
  replyingTo.value = null
  replyComment.value = ''
}

const submitReply = async () => {
  if (!replyComment.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  const id = route.params.id
  try {
    submitLoading.value = true
    // 如果回复的是一个回复，那么 parent_id 应该是最顶层的父评论 ID
    // 但为了简单，我们可以直接用 replyingTo.id 的 parent 或者 replyingTo.id
    const parentId = replyingTo.value.parent || replyingTo.value.id
    
    const res = await requestUtil.post('repository/comment/submit', {
      id: Number(id),
      user_id: currentUser.id,
      content: replyComment.value,
      parent_id: parentId,
      reply_to_user_id: replyingTo.value.user // user 是评论者的 ID
    })
    
    if (res.data.code === 200) {
      ElMessage.success('回复成功')
      cancelReply()
      getComments(currentPage.value, pageSize.value) // 刷新评论列表
    } else {
      ElMessage.error(res.data.msg || '回复失败')
    }
  } catch (error) {
    console.error('提交回复失败:', error)
    ElMessage.error('提交回复失败')
  } finally {
    submitLoading.value = false
  }
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const match = dateTimeString.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).*$/)
  return match ? `${match[1]} ${match[2]}` : dateTimeString
}

const handleImageClick = (event) => {
  // 检查点击的是否为图片元素
  if (event.target.tagName.toLowerCase() === 'img') {
    // 阻止默认行为，防止选中整个内容区域
    event.preventDefault();
    
    // 获取图片的src属性
    const imgSrc = event.target.src;
    
    // 显示图片预览对话框
    previewImageUrl.value = imgSrc;
    imagePreviewVisible.value = true;
  }
}

const showBackTop = ref(false)

const goBack = () => {
  // 直接导航到知识库管理列表页，而不是返回上一页
  router.push('/bsns/repository')
}

// 监听滚动事件来控制返回顶部按钮的显示
const handleScroll = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop
  showBackTop.value = scrollTop > 300 // 当滚动超过300px时显示按钮
}

// 滚动到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth' // 平滑滚动
  })
}

// 监听路由参数变化并重新加载数据
watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      // 重新加载数据
      getDetail();
      getComments();
    }
  },
  { immediate: false }
);

onMounted(() => {
  getDetail()
  getComments()
  
  // 监听滚动事件
  window.addEventListener('scroll', handleScroll)
  // 页面加载完成后也检查一次滚动位置
  handleScroll()
})

// 组件卸载时移除事件监听器
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 在 setup 语法中，直接使用导入的组件即可
</script>
<style scoped>
.detail-content {
  margin-top: 20px;
}

.content-html img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 5px 0;
  vertical-align: middle;
  /* 添加边框和阴影以提高可见性 */
  border: 1px solid #dcdfe6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.content-html p {
  margin: 10px 0;
  line-height: 1.6;
}

.content-html ul, .content-html ol {
  margin: 10px 0;
  padding-left: 20px;
}

.content-html h1, .content-html h2, .content-html h3, .content-html h4, .content-html h5, .content-html h6 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.content-html strong {
  font-weight: 600;
}

.content-html em {
  font-style: italic;
}

.content-html ul li, .content-html ol li {
  margin: 5px 0;
}

.content-html blockquote {
  margin: 15px 0;
  padding: 10px 15px;
  border-left: 4px solid #dcdfe6;
  background-color: #f5f7fa;
  color: #606266;
}

.content-html pre {
  margin: 10px 0;
  padding: 10px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
}

.content-html code {
  padding: 2px 4px;
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9em;
}

.content-html table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.content-html table th, .content-html table td {
  border: 1px solid #dcdfe6;
  padding: 8px;
  text-align: left;
}

.content-html table th {
  background-color: #f5f7fa;
}

/* 防止选择时出现异常样式 */
.content-html {
  user-select: text;
}

.content-html::selection {
  background-color: #b3d7ff;
  color: #000;
}

.content-html ::selection {
  background-color: #b3d7ff;
  color: #000;
}

/* 修复表格选择 */
.content-html table ::selection {
  background-color: #b3d7ff;
  color: #000;
}

.content-html table ::-moz-selection {
  background-color: #b3d7ff;
  color: #000;
}

.content-html td::selection,
.content-html th::selection {
  background-color: #b3d7ff;
  color: #000;
}

.content-html td::-moz-selection,
.content-html th::-moz-selection {
  background-color: #b3d7ff;
  color: #000;
}

/* 移除通用透明选择背景 */
/* .content-html *::selection {
  background: transparent;
}

.content-html *::-moz-selection {
  background: transparent;
} */

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Backtop button styling */
.back-top-btn {
  position: fixed;
  width: 50px;
  height: 50px;
  background-color: #409eff;
  color: #fff;
  border-radius: 50%;
  z-index: 9999;
  box-shadow: 0 0 8px rgba(0,0,0,.12), 0 4px 8px rgba(0,0,0,.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
}

.back-top-btn:hover {
  background-color: #66b1ff;
  transform: scale(1.1);
}
</style>
