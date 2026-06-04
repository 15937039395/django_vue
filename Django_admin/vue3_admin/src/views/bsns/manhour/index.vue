<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-row :gutter="20" class="header">
      <el-col :span="7">
        <el-input placeholder="请输入搜索的内容..." v-model="queryForm.query" clearable></el-input>
      </el-col>
      <el-button type="primary" :icon="Search" @click="initManhourList">搜索</el-button>
      <el-button v-if="canAdd()" type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增</el-button>
<!--      <el-popconfirm title="您确定批量删除这些记录吗？" @confirm="handleDelete(null)">-->
<!--        <template #reference>-->
<!--          <el-button type="danger" :disabled="delBtnStatus" :icon="Delete">批量删除</el-button>-->
<!--        </template>-->
<!--      </el-popconfirm>-->
    </el-row>
    <div class="tips-row">
      <span class="tips-text">提示：日报只填写正常打卡上班工时，已默认为8小时，如有加班申请，请修改工时, 月报工时已默认为0，不需要填写工时</span>
    </div>
    <el-table
        :data="tableData"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55"/>
      <el-table-column prop="dept_name" label="部门名称" sortable width="100" align="center"/>
      <el-table-column prop="user_name" label="用户名" sortable  width="100" align="center"/>
      <el-table-column  prop="date_time" label="日期" sortable width="180"/>
      <el-table-column  prop="report_type" label="类型" sortable width="100"/>
      <el-table-column  prop="project_number" label="项目编号及名称" sortable width="180"/>

      <el-table-column
        prop="job_description"
        label="工作描述"
        sortable
        width="400"
        :min-width="200"
      >
        <template #default="scope">
          <span class="detail-link" @click="showDetail(scope.row)">
            {{ (scope.row.job_description || '无工作描述').substring(0, 20) }}{{ (scope.row.job_description || '').length > 20 ? '...' : '' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column  prop="man_hour" label="工时" width="180"/>

      <el-table-column  prop="issue" label="存在的问题" sortable width="180"/>
      <el-table-column  prop="coordinate" label="需协调的事项" sortable width="180"/>
      <el-table-column  prop="work_plan" label="次日工作计划" sortable width="180"/>
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

      <el-table-column  prop="remark" label="备注" width="180"/>
      <el-table-column prop="action" label="操作" width="200" fixed="right" align="center">
        <template v-slot="scope">
          <el-button type="primary" :icon="Edit" :disabled="!canEditOrDelete(scope.row)" @click="handleDialogValue(scope.row.id)"/>
          <el-popconfirm title="您确定要删除这条记录吗？" @confirm="handleDelete(scope.row.id)" :disabled="!canEditOrDelete(scope.row)">
            <template #reference>
              <el-button type="danger" :icon="Delete" :disabled="!canEditOrDelete(scope.row)"/>
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

    <Dialog
      v-model:dialogVisible="dialogVisible"
      :id="id"
      :dialogTitle="dialogTitle"
      @initManhourList="initManhourList">
      </Dialog>
  </div>

  <!-- 工作描述详情弹窗 -->
  <el-dialog v-model="detailVisible" title="工作描述详情" width="600px">
    <div class="detail-content" v-html="detailText.replace(/\n/g, '<br>')"></div>
    <template #footer>
      <el-button @click="detailVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import {Search, Delete, DocumentAdd, Edit, Tools, RefreshRight} from '@element-plus/icons-vue'
import requestUtil,{getServerUrl} from '@/util/request'
import {ref} from "vue";
import Dialog from './components/dialog'
import {ElMessage} from "element-plus";

const detailVisible = ref(false)
const detailText = ref('')

// 显示工作描述详情
const showDetail = (row) => {
  detailText.value = row.job_description || '无工作描述'
  detailVisible.value = true
}

// 获取当前登录用户信息
const getCurrentUser = () => {
  const userStr = window.sessionStorage.getItem("currentUser")
  return userStr ? JSON.parse(userStr) : {}
}

// 判断当前用户是否可以编辑或删除某条工时
const canEditOrDelete = (row) => {
  const currentUser = getCurrentUser()
  const currentUserId = currentUser.id || currentUser.user_id
  const currentUserRoles = currentUser.roles || []
  
  // 超级管理员（ID=1）可以编辑删除
  if (currentUserId === 1) return true
  
  // 管理员角色可以编辑删除
  if (currentUserRoles.some && currentUserRoles.some(r => r.name && r.name.includes('管理员'))) return true
  
  // 只有当是自己的记录时才能编辑删除
  if (currentUserId && row.user_id === currentUserId) return true
  
  // 其他情况只能查看
  return false
}

// 判断当前用户是否可以新增工时
const canAdd = () => {
  // 所有人都可以新增自己的工时
  return true
}


const id = ref(-1)
const dialogVisible = ref(false)
const dialogTitle = ref('')

// 对话框处理
const handleDialogValue = (roleId) => {
  if (roleId) {
    id.value = roleId;
    dialogTitle.value = "工时修改"
  } else {
    id.value = -1;
    dialogTitle.value = "工时添加"
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
  const res = await requestUtil.del("manhour/action", ids)
  if (res.data.code == 200) {
    ElMessage({
      type: 'success',
      message: '执行成功!'
    })
    initManhourList();
  } else {
    ElMessage({
      type: 'error',
      message: res.data.msg,
    })
  }
}

// 初始化表格数据
const initManhourList=async ()=>{

  const res=await requestUtil.post("manhour/search",queryForm.value)
  tableData.value=res.data.manhourList
  total.value=res.data.total

}
// 分页处理
const handleSizeChange=(pageSize)=>{
  queryForm.value.pageSize=pageSize
  queryForm.value.pageNum=1
  initManhourList()
}

const handleCurrentChange=(pageNum)=>{
  queryForm.value.pageNum=pageNum
  initManhourList()
}

initManhourList()
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

.tips-row {
  padding: 10px 0;
  margin-bottom: 10px;
}

.tips-text {
  color: #909399;
  font-size: 13px;
}

.el-tag--small {
  margin-left: 5px;
}
/* 容器：限制宽度、溢出隐藏，确保表格行高一致 */
:deep(.content-truncate-auto) {
  width: 100%;
  overflow: hidden;
  white-space: nowrap; /* 强制单行显示 */
  line-height: 24px; /* 与表格默认行高对齐 */
}
/* 文本：截断样式优化，hover 效果增强 */
:deep(.text-ellipsis) {
  display: inline-block;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis; /* 末尾省略号 */
  color: var(--el-text-color-primary);
  transition: color 0.2s;
}

/* hover 高亮提示可点击感 */
.text-ellipsis:hover {
  color: var(--el-color-primary);
  cursor: default;
}

.tips-row {
  padding: 10px 0;
  margin-bottom: 10px;
}

.tips-text {
  color: #f56c6c;
  font-size: 16px;
  font-weight: bold;
}

.detail-link {
  color: #409eff;
  cursor: pointer;
}

.detail-link:hover {
  text-decoration: underline;
}


.detail-content {
  white-space: pre-wrap;
  line-height: 1.8;
}
</style>