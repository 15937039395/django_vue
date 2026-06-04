<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-row :gutter="20" class="header">
      <el-col :span="7">
        <el-input placeholder="请输入编号或名称" v-model="queryForm.query" clearable></el-input>
      </el-col>
      <el-button type="primary" :icon="Search" @click="initItemsList">搜索</el-button>
      <el-button type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增</el-button>
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
        @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55"/>

      <el-table-column  prop="project_number" label="项目编号及名称" sortable min-width="350"/>
      <el-table-column  prop="user_name" label="创建人" sortable min-width="120"/>
      <el-table-column prop="create_time" label="创建时间" sortable min-width="150">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="update_time" label="更新时间" min-width="150">
        <template #default="scope">
          {{ formatDateTime(scope.row.update_time) }}
        </template>
      </el-table-column>

      <el-table-column prop="action" label="操作" min-width="150" fixed="right" align="center">
        <template v-slot="scope">
          <el-button type="primary" :icon="Edit" @click="handleDialogValue(scope.row.id)"/>
          <el-popconfirm title="您确定要删除这条记录吗？" @confirm="handleDelete(scope.row.id)">
            <template #reference>
              <el-button type="danger" :icon="Delete"/>
            </template>
          </el-popconfirm>
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
    <Dialog v-model="dialogVisible" :dialogVisible="dialogVisible" :id="id" :dialogTitle="dialogTitle"
            @initItemsList="initItemsList"></Dialog>
  </div>
</template>

<script setup>
import {Search, Delete, DocumentAdd, Edit, Tools, RefreshRight} from '@element-plus/icons-vue'
import requestUtil,{getServerUrl} from '@/util/request'
import {ref} from "vue";
import Dialog from './components/dialog'
import {ElMessage} from "element-plus";


const id = ref(-1)
const dialogVisible = ref(false)
const dialogTitle = ref('')

// 对话框处理
const handleDialogValue = (roleId) => {
  if (roleId) {
    id.value = roleId;
    dialogTitle.value = "项目修改"
  } else {
    id.value = -1;
    dialogTitle.value = "项目添加"
  }
    dialogVisible.value = true
}


const tableData = ref([])
const total=ref(0)
const queryForm=ref({
  query:'',
  pageNum:1,
  pageSize:10
})

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
  const res = await requestUtil.del("items/action", ids)
  if (res.data.code == 200) {
    ElMessage({
      type: 'success',
      message: '执行成功!'
    })
    initItemsList();
  } else {
    ElMessage({
      type: 'error',
      message: res.data.msg,
    })
  }
}

// 初始化表格数据
const initItemsList=async ()=>{

  const res=await requestUtil.post("items/search",queryForm.value)
  tableData.value=res.data.itemsList
  total.value=res.data.total

}
// 分页处理
const handleSizeChange=(pageSize)=>{
  queryForm.value.pageSize=pageSize
  queryForm.value.pageNum=1
  initItemsList()
}

const handleCurrentChange=(pageNum)=>{
  queryForm.value.pageNum=pageNum
  initItemsList()
}

initItemsList()
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