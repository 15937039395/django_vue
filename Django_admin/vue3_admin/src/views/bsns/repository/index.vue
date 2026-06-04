<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿
<template>
  <div class="app-container">
    <el-row :gutter="20" class="header">
      <el-col :span="7">
        <el-input placeholder="请输入搜索的内容..." v-model="queryForm.query" clearable></el-input>
      </el-col>
      <el-button type="primary" :icon="Search" @click="initRepositoryList">搜索</el-button>
      <el-button type="success" :icon="DocumentAdd" @click="goToAdd">新增</el-button>
<!--      <el-popconfirm title="您确定批量删除这些记录吗？" @confirm="handleDelete(null)">-->
<!--        <template #reference>-->
<!--          <el-button type="danger" :disabled="delBtnStatus" :icon="Delete">批量删除</el-button>-->
<!--        </template>-->
<!--      </el-popconfirm>-->
    </el-row>
    <el-table
        :data="tableData"
        stripe        style="width: 100%"
        row-key="id"
        :tree-props="{children: 'historyChildren', hasChildren: 'hasHistory'}"
        @selection-change="handleSelectionChange"
    >
<!--      <el-table-column type="selection" width="55"/>-->


      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.is_temp ? 'warning' : scope.row.confirmed ? 'success' : 'info'">
            {{ scope.row.is_temp ? '临时' : scope.row.confirmed ? '已确认' : '正常' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="visibility" label="可见性" width="100" align="center">
        <template #default="scope">
          <el-tag 
            v-if="!scope.row.isHistory"
            :type="scope.row.visibility === 1 ? 'info' : scope.row.visibility === 2 ? 'warning' : 'success'"
            size="small">
            <el-icon style="margin-right: 4px;">
              <Lock v-if="scope.row.visibility === 1" />
              <OfficeBuilding v-else-if="scope.row.visibility === 2" />
              <User v-else />
            </el-icon>
            {{ scope.row.visibility === 1 ? '仅自己' : scope.row.visibility === 2 ? '部门' : '全员' }}
          </el-tag>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="event_name" label="事件名称" sortable width="120" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.event_name }}</span>
          <span v-else style="color: #909399; font-style: italic;">[历史记录]</span>
        </template>
      </el-table-column>
      <el-table-column prop="event_number" label="项目编号" sortable width="120" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.event_number }}</span>
          <span v-else style="color: #909399; font-size: 12px;">{{ scope.row.historyDisplay }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="principal" label="负责人" sortable width="100" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.principal }}</span>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="event_occur_time_formatted" label="事件发生时间" sortable width="120" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.event_occur_time_formatted }}</span>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="address" label="发生地点" sortable width="120" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.address }}</span>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="dept_name" label="部门名称" sortable width="100" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.dept_name }}</span>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="user_name" label="用户名" sortable width="100" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.user_name }}</span>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="types_text" label="类型" sortable width="100" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.types_text }}</span>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="classify_name" label="分类" sortable width="100" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.classify_name }}</span>
          <span v-else style="color: #c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" sortable width="180" align="center">
        <template #default="scope">
          <span v-if="!scope.row.isHistory">{{ scope.row.title }}</span>
          <span v-else style="color: #909399; font-weight: bold;">{{ scope.row.title }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="内容" sortable width="400">
        <template #default="scope">
          <div class="content-truncate-auto" :title="stripHtml(scope.row.content)">
            <span v-if="!scope.row.isHistory">{{ stripHtml(scope.row.content) }}</span>
            <span v-else style="color: #909399; font-size: 13px;">{{ stripHtml(scope.row.content) }}</span>
          </div>
        </template>
      </el-table-column>
<!--      <el-table-column prop="create_time" label="创建时间" sortable width="180">-->
<!--        <template #default="scope">-->
<!--          {{ formatDateTime(scope.row.create_time) }}-->
<!--        </template>-->
<!--      </el-table-column>-->
<!--      <el-table-column prop="update_time" label="更新时间" width="180">-->
<!--        <template #default="scope">-->
<!--          {{ formatDateTime(scope.row.update_time) }}-->
<!--        </template>-->
<!--      </el-table-column>-->
      <el-table-column prop="upvote" label="点赞数" width="80" align="center"/>
      <el-table-column prop="remark" label="备注" width="180"/>

      <el-table-column prop="action" label="操作" width="400" fixed="right" align="center">
        <template v-slot="scope">
          <template v-if="!scope.row.isHistory">
            <div class="action-buttons">
              <!-- 编辑按钮：未确认记录的创建者或管理员可编辑 -->
              <el-tooltip content="编辑" placement="top" v-if="(scope.row.user_id === currentUser.id && !scope.row.confirmed) || (currentUser.role_id && Number(currentUser.role_id) === 1)">
                <span>
                  <el-button 
                    type="primary" 
                    :icon="Edit" 
                    @click="goToEdit(scope.row.id)"
                  />
                </span>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top" v-else>
                <span>
                  <el-button 
                    type="primary" 
                    :icon="Edit" 
                    @click="goToEdit(scope.row.id)"
                    :disabled="true"
                  />
                </span>
              </el-tooltip>
              
              <!-- 点赞按钮 -->
              <el-tooltip content="点赞" placement="top">
                <el-button :type="scope.row.user_liked ? 'danger' : 'default'" :icon="IconParkLike" @click="handleLike(scope.row)" circle size="small" />
              </el-tooltip>
              <el-button type="success" :icon="View" size="small" @click="goToDetail(scope.row.id)">
                查看
              </el-button>
              <el-button type="warning" :icon="Star" size="small" @click="goToReview(scope.row.id)">
                复盘
              </el-button>
              
              <!-- 删除按钮：未确认记录的创建者或管理员可删除 -->
              <el-popconfirm 
                v-if="(scope.row.user_id === currentUser.id && !scope.row.confirmed) || (currentUser.role_id && Number(currentUser.role_id) === 1)"
                title="您确定要删除这条记录吗？" 
                @confirm="handleDelete(scope.row.id)">
                <template #reference>
                  <el-button type="danger" :icon="Delete"/>
                </template>
              </el-popconfirm>
              <el-button 
                v-else
                type="danger" 
                :icon="Delete"
                :disabled="true"
              />
            </div>
          </template>
          <span v-else style="color: #c0c4cc; font-size: 12px;">历史记录</span>
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
import { Search, Delete, DocumentAdd, Edit, Tools, RefreshRight, Star, View, Lock, OfficeBuilding, User } from '@element-plus/icons-vue'
import { Like } from '@icon-park/vue-next';
import requestUtil from '@/util/request'
import { ref, watch } from "vue"
import { ElMessage } from "element-plus"

// 注册 IconPark 图标
const IconParkLike = Like
import { useRouter } from 'vue-router'

// 获取当前登录用户信息
const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {};

const router = useRouter()

// 去除HTML标签，保留纯文本
const stripHtml = (html) => {
  if (!html) return ''
  return html.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&quot;/g, '"')
}

// 添加跳转到详情页的方法
const goToDetail = (id) => {
  router.push(`/bsns/repository/detail/${id}`)
}

// 添加跳转到复盘页的方法
const goToReview = (id) => {
  router.push(`/bsns/repository/detail/${id}`)
}

// 添加跳转到新增页面的方法
const goToAdd = () => {
  router.push('/bsns/repository/add')
}

// 添加跳转到编辑页面的方法
const goToEdit = (id) => {
  router.push(`/bsns/repository/edit/${id}`)
}

const tableData = ref([])
const total = ref(0)
const queryForm = ref({
  query: '',
  pageNum: 1,
  pageSize: 10
})

const multipleSelection = ref([])
const delBtnStatus = ref(true)

watch(multipleSelection, (newVal) => {
  delBtnStatus.value = newVal.length === 0
})

const handleSelectionChange = (selection) => {
  multipleSelection.value = selection
}

const handleDelete = async (id) => {
  let ids = []
  if (id) {
    ids.push(id)
  } else {
    ids = multipleSelection.value.map(item => item.id)
  }

  if (ids.length === 0) {
    ElMessage.warning('请选择需要删除的数据')
    return
  }

  try {
    // 添加用户信息用于后端权限检查
    const deleteData = {
      ids: ids,
      user_id: currentUser.id,
      role_id: currentUser.role_id
    };
    
    const res = await requestUtil.del("repository/action", deleteData)
    if (res.data.code === 200) {
      ElMessage.success('删除成功!')
      initRepositoryList()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (err) {
    ElMessage.error('系统异常，请稍后再试')
  }
}

// 初始化表格数据
const initRepositoryList = async () => {
  try {
    // 获取当前登录用户信息
    const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {};
    const userId = currentUser.id;
    const roleId = currentUser.role_id;
    
    // 将用户ID和角色ID添加到查询参数中，用于后端权限过滤
    const params = {
      ...queryForm.value,
      user_id: userId,
      role_id: roleId
    };
    
    const res = await requestUtil.post("repository/search", params)
    console.log('>>>>sou',res.data.repositoryList)
    let repositoryList = res.data.repositoryList || []
    
    // 为每条记录添加历史记录子节点（并行请求优化）
    const historyPromises = repositoryList.map(record => 
      requestUtil.get(`repository/history?id=${record.id}`)
        .then(historyRes => {
          if (historyRes.data.code === 200 && historyRes.data.history_list.length > 0) {
            // 添加历史记录作为子节点
            record.historyChildren = historyRes.data.history_list.map((history, index) => ({
              id: `${record.id}-history-${index}`, // 确保子节点有唯一的ID
              version: history.version,
              remarks: history.remarks,
              modified_time: history.modified_time,
              title: history.title,
              content: history.content,
              isHistory: true, // 标记这是历史记录
              // 显示特定字段用于历史记录展示
              historyDisplay: `[V${history.version}] ${history.remarks} (${history.modified_time})`
            }));
            record.hasHistory = true;
          } else {
            record.hasHistory = false;
            record.historyChildren = [];
          }
        })
        .catch(historyErr => {
          console.error('获取历史记录失败:', historyErr);
          record.hasHistory = false;
          record.historyChildren = [];
        })
    );
    
    // 等待所有历史记录请求完成
    await Promise.all(historyPromises);
    
    tableData.value = repositoryList;
    total.value = res.data.total || 0
  } catch (err) {
    ElMessage.error('获取列表失败')
  }
}

// 分页处理
const handleSizeChange = (pageSize) => {
  queryForm.value.pageSize = pageSize
  queryForm.value.pageNum = 1
  initRepositoryList()
}

const handleCurrentChange = (pageNum) => {
  queryForm.value.pageNum = pageNum
  initRepositoryList()
}

initRepositoryList()

// 局部更新单条记录，避免刷新整个列表
const updateSingleRecord = async (updatedRecord) => {
  try {
    // 查找记录在表格中的索引
    const index = tableData.value.findIndex(item => item.id === updatedRecord.id);
    
    if (index !== -1) {
      // 获取更新后的历史记录
      try {
        const historyRes = await requestUtil.get(`repository/history?id=${updatedRecord.id}`);
        if (historyRes.data.code === 200 && historyRes.data.history_list.length > 0) {
          updatedRecord.historyChildren = historyRes.data.history_list.map((history, idx) => ({
            id: `${updatedRecord.id}-history-${idx}`,
            version: history.version,
            remarks: history.remarks,
            modified_time: history.modified_time,
            title: history.title,
            content: history.content,
            isHistory: true,
            historyDisplay: `[V${history.version}] ${history.remarks} (${history.modified_time})`
          }));
          updatedRecord.hasHistory = true;
        } else {
          updatedRecord.hasHistory = false;
          updatedRecord.historyChildren = [];
        }
      } catch (historyErr) {
        console.error('获取历史记录失败:', historyErr);
        updatedRecord.hasHistory = false;
        updatedRecord.historyChildren = [];
      }
      
      // 更新表格中的记录
      tableData.value[index] = updatedRecord;
    } else {
      // 如果找不到记录，则刷新整个列表
      await initRepositoryList();
    }
  } catch (err) {
    console.error('更新记录失败:', err);
    // 如果更新失败，则刷新整个列表
    await initRepositoryList();
  }
}

// 格式化日期
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const match = dateTimeString.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).*$/)
  return match ? `${match[1]} ${match[2]}` : dateTimeString
}

// 点赞处理
const handleLike = async (row) => {
  try {
    // 获取当前登录用户ID
    const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {};
    const userId = currentUser.id;
    
    if (!userId) {
      ElMessage.error('请先登录');
      return;
    }
    
    const res = await requestUtil.post("repository/like", {
      id: row.id,
      user_id: userId
    })

    if (res.data.code === 200) {
      // 更新本地数据
      const index = tableData.value.findIndex(item => item.id === row.id)
      if (index !== -1) {
        tableData.value[index].upvote = res.data.upvote;
        // 更新用户点赞状态
        tableData.value[index].user_liked = res.data.liked;
      }
      
      // 根据返回的消息判断是点赞还是取消点赞
      if (res.data.msg.includes('取消')) {
        ElMessage.info(res.data.msg)
      } else {
        ElMessage.success(res.data.msg)
      }
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (err) {
    ElMessage.error('系统异常，请稍后再试')
    console.error(err)
  }
}
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

.el-tag--small {
  margin-left: 5px;
}

.content-truncate-auto {
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  line-height: 24px;
  cursor: default;
}
// 点赞按钮样式
.liked {
  color: #ffd700 !important;
}

:deep(.content-truncate-auto) {
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  line-height: 24px;
  cursor: default;
}

:deep(.action-buttons) {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: nowrap;
}
</style>