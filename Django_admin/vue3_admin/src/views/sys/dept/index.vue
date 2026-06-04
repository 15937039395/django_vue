<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">

    <el-row class="header">
      <el-button type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增</el-button>
    </el-row>

    <el-table
        :data="tableData"
        style="width: 100%; height: calc(100vh - 200px)"
        row-key="id"
        border
        stripe
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
    >
      <el-table-column prop="name" label="部门名称" min-width="180"/>
      <el-table-column prop="leader" label="部门负责人" min-width="120"/>
      <el-table-column prop="sort" label="排序" min-width="80" align="center"/>
      <el-table-column prop="type" label="部门类型" min-width="100" :formatter="formatDeptType"/>
      <el-table-column prop="create_time" label="创建时间" min-width="180" align="center">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="action" label="操作" min-width="200" fixed="right" align="center">
        <template #default="scope">
          <el-button type="primary" :icon="Edit" @click="handleDialogValue(scope.row.id)"/>
          <el-popconfirm title="您确定要删除这条记录吗？" @confirm="handleDelete(scope.row.id)">
            <template #reference>
              <el-button type="danger" :icon="Delete"/>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

  </div>
  <Dialog v-model="dialogVisible" :tableData="tableData" :dialogVisible="dialogVisible" :id="id"
          :dialogTitle="dialogTitle" @initMenuList="initMenuList"></Dialog>

</template>

<script setup>
import {Delete, DocumentAdd, Edit} from '@element-plus/icons-vue'
import {ref} from 'vue'
import requestUtil from "@/util/request";
import {ElMessage} from 'element-plus'
import Dialog from './components/dialog'

const formatDeptType = (row) => {
  const typeMap = {
    0: '待分配',
    1: '公司',
    2: '子公司',
    3: '部门',
    4: '小组'
  };
  return typeMap[row.type] ?? '部门';
};

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const match = dateTimeString.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).*$/)
  if (match) {
    return `${match[1]} ${match[2]}`
  }
  return dateTimeString
}

const tableData = ref([])

const initMenuList = async () => {
  const res = await requestUtil.get("department/treeList");
  tableData.value = res.data.treeList || [];
}

initMenuList();

const id = ref(-1)
const dialogVisible = ref(false)
const dialogTitle = ref('')

const handleDialogValue = (deptId) => {
  if (deptId) {
    id.value = deptId;
    dialogTitle.value = "部门修改"
  } else {
    id.value = -1;
    dialogTitle.value = "部门添加"
  }
  dialogVisible.value = true
}

const handleDelete = async (deptId) => {
  const res = await requestUtil.del("department/action", deptId)
  if (res.data.code == 200) {
    ElMessage.success('删除成功!')
    initMenuList();
  } else {
    ElMessage.error(res.data.msg)
  }
}

</script>

<style lang="scss" scoped>

.app-container {
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.header {
  padding-bottom: 16px;
}

:deep(th.el-table__cell) {
  word-break: break-word;
  background-color: #f8f8f9 !important;
  color: #515a6e;
  height: 40px;
  font-size: 13px;
}

</style>