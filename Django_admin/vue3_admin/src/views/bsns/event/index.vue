<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">

    <el-row :gutter="20" class="header">
      <el-col :span="7">
        <el-input placeholder="请输入事件名称..." v-model="queryForm.query" clearable></el-input>
      </el-col>
      <el-button type="primary" :icon="Search" @click="initEventList">搜索</el-button>
      <el-button type="success" :icon="DocumentAdd" @click="handleAdd()">新增</el-button>
      <el-button type="warning" :icon="RefreshRight" @click="handleHistory">分配记录</el-button>
      <el-popconfirm title="您确定批量删除这些记录吗？" @confirm="handleDelete(null)">
        <template #reference>
          <el-button type="danger" :disabled="delBtnStatus" :icon="Delete">批量删除</el-button>
        </template>
      </el-popconfirm>
    </el-row>
    <el-table
        :data="tableData"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55"/>
      <el-table-column prop="dept_name" label="部门名称" sortable width="100" align="center"/>
      <el-table-column prop="user_name" label="用户名" sortable  width="100" align="center"/>
      <el-table-column prop="event_number" label="事件编号" width="200" align="center"/>
      <el-table-column prop="event_name" label="事件名称" width="200" align="center"/>
      <el-table-column prop="principal" label="负责人" width="100" align="center"/>
      <el-table-column prop="start_date" label="项目起始时间" width="120" align="center"/>
      <el-table-column prop="end_date" label="项目终止时间" width="120" align="center"/>
      <el-table-column prop="notification_time" label="配置通知时间" width="180" align="center"/>
      <el-table-column prop="create_time" label="创建时间" sortable width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="update_time" label="更新时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" width="200"/>

      <el-table-column prop="action" label="操作" width="400" fixed="right" align="center">
        <template v-slot="scope">
          <!-- 关联参与人员按钮 - 管理员或事件创建者可操作，其他人禁用 -->
          <el-button 
            type="primary" 
            :icon="Tools" 
            :disabled="!canOperate(scope.row)"
            @click="handleEventDialogValue(scope.row.id)">
            关联参与人员
          </el-button>

          <!-- 编辑按钮 - 管理员或事件创建者可操作，其他人禁用 -->
          <el-button 
            type="primary" 
            :icon="Edit"
            :disabled="!canOperate(scope.row)"
            @click="handleEdit(scope.row.id)"/>

          <!-- 删除按钮 - 管理员或事件创建者可操作，其他人禁用 -->
          <el-popconfirm 
            title="您确定要删除这条记录吗？" 
            @confirm="handleDelete(scope.row.id)">
            <template #reference>
              <el-button 
                type="danger" 
                :icon="Delete"
                :disabled="!canOperate(scope.row)"/>
            </template>
          </el-popconfirm>

        </template>
      </el-table-column>
    </el-table>
    <el-pagination
        v-model:currentPage="queryForm.pageNum"
        v-model:page-size="queryForm.pageSize"
        :page-sizes="[10, 20, 30, 40,50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
    />
  </div>
  <EventDialog v-model="eventDialogVisible" :eventDialogVisible="eventDialogVisible" :id="id"
              @initEventList="initEventList"></EventDialog>
</template>

<script setup>
import {Search, Delete, DocumentAdd, Edit, Tools, RefreshRight} from '@element-plus/icons-vue'
import {ref, onMounted} from 'vue'
import { useRouter, useRoute } from 'vue-router'
import requestUtil, {getServerUrl} from "@/util/request";
import {ElMessage, ElMessageBox} from 'element-plus'

import EventDialog from './components/eventDialog'

const router = useRouter()
const route = useRoute()

// 获取当前登录用户信息
const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {}
const currentUserId = currentUser.id
const currentUserRoleId = currentUser.role_id

const id = ref(-1)

const eventDialogVisible = ref(false)

const handleEventDialogValue = (roleId) => {
  if (roleId) {
    id.value = roleId;
  }
  eventDialogVisible.value = true
}

// 判断是否可以操作该事件（编辑、删除、关联参与人员）
const canOperate = (row) => {
  // 管理员（role_id === 1）可以操作所有事件
  if (currentUserRoleId === 1) {
    return true
  }
  // 普通用户只能操作自己创建的事件
  // row.user_id 是字符串类型，需要转换为数字进行比较
  return String(row.user_id) === String(currentUserId)
}

// 新增事件
const handleAdd = () => {
  router.push('/bsns/event/add');
}

// 编辑事件
const handleEdit = (eventId) => {
  router.push(`/bsns/event/edit/${eventId}`);
}

// 查看分配历史
const handleHistory = () => {
  router.push('/bsns/event/assignment-history');
}

const queryForm = ref({
  query: '',
  pageNum: 1,
  pageSize: 10
})

const total = ref(0)

const tableData = ref([])

const multipleSelection = ref([])

const delBtnStatus = ref(true)


const handleSelectionChange = (selection) => {
  console.log("勾选了")
  console.log(selection)
  multipleSelection.value = selection;
  delBtnStatus.value = selection.length == 0;
}


const handleDelete = async (id) => {
  var ids = []
  if (id) {
    ids.push(id)
  } else {
    multipleSelection.value.forEach(row => {
      ids.push(row.id)
    })
  }
  
  // 传递用户信息进行权限验证
  const requestData = {
    ids: ids,
    role_id: currentUserRoleId,
    user_id: currentUserId
  }
  
  const res = await requestUtil.del("event/action", requestData)
  if (res.data.code == 200) {
    ElMessage({
      type: 'success',
      message: '执行成功!'
    })
    initEventList();
  } else {
    ElMessage({
      type: 'error',
      message: res.data.message || res.data.msg || '删除失败',
    })
  }
}

const initEventList = async () => {
  const res = await requestUtil.post("event/search", queryForm.value)
  tableData.value = res.data.eventList;
  total.value = res.data.total;
}

onMounted(() => {
  initEventList();
  // 如果从新增页面跳转过来带有 openGrant 参数，则自动打开关联弹窗
  if (route.query.openGrant) {
    id.value = Number(route.query.openGrant);
    eventDialogVisible.value = true;
  }
})

const handleSizeChange = (pageSize) => {
  queryForm.value.pageNum = 1;
  queryForm.value.pageSize = pageSize;
  initEventList();
}

const handleCurrentChange = (pageNum) => {
  queryForm.value.pageNum = pageNum;
  initEventList();
}

//格式化日期
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  // 使用正则表达式提取日期和时间部分
  const match = dateTimeString.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).*$/)
  if (match) {
    return `${match[1]} ${match[2]}`
  }
  return dateTimeString
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

:deep(.el-tag--small) {
  margin-left: 5px;
}
</style>
