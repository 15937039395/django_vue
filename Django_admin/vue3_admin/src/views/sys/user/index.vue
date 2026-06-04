<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-row :gutter="20" class="header">
      <el-col :span="7">
        <el-input placeholder="请输入用户名 ..." v-model="queryForm.query" clearable></el-input>
      </el-col>
      <el-button type="primary" :icon="Search" @click="initUserList">搜索</el-button>
      <el-button v-permission="['sys:user:add']" type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增</el-button>
      <el-popconfirm title="您确定批量删除这些记录吗？" @confirm="handleDelete(null)">
        <template #reference>
          <el-button v-permission="['sys:user:delete']" type="danger" :disabled="delBtnStatus" :icon="Delete">批量删除</el-button>
        </template>
      </el-popconfirm>
    </el-row>

    <el-table :data="tableData" stripe style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55"/>
      <el-table-column prop="avatar" label="头像" width="80" align="center">
        <template v-slot="scope">
          <img :src="getServerUrl()+'media/userAvatar/'+scope.row.avatar" width="50" height="50"/>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="账号" width="100" align="center"/>
      <el-table-column prop="realname" label="姓名" width="100" align="center"/>
      <el-table-column prop="nickname" label="花名" width="100" align="center"/>
      <el-table-column prop="gender" label="性别" width="100" align="center">
        <template #default="{ row }">
          {{ getGenderText(row.gender) }}
        </template>
      </el-table-column>
      <el-table-column prop="roles" label="拥有角色" width="200" align="center">
        <template v-slot="scope">
          <el-tag size="small" type="warning" v-for="item in scope.row.roleList"> {{ item.name }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="level_name" label="职级" width="100" align="center"/>
      <el-table-column prop="post_name" label="岗位" width="100" align="center"/>
      <el-table-column prop="dept_name" label="部门" width="100" align="center"/>
      <el-table-column prop="email" label="邮箱" width="200" align="center"/>
      <el-table-column prop="phone" label="手机号" width="120" align="center"/>
      <el-table-column prop="status" label="状态？" width="200" align="center">
        <template v-slot="{row}">
          <el-switch v-model="row.status" @change="statusChangeHandle(row)" active-text="正常"
                     inactive-text="禁用" :active-value="1" :inactive-value="2"></el-switch>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="200" align="center"/>
      <el-table-column prop="login_date" label="最后登录时间" width="200" align="center"/>
      <el-table-column prop="remark" label="备注"/>
      <el-table-column v-if="isAdmin" prop="action" label="操作" width="400" fixed="right" align="center">
        <template v-slot="scope">
          <el-button type="primary" :icon="Tools" @click="handleRoleDialogValue(scope.row.id,scope.row.roleList)">分配角色
          </el-button>

          <el-popconfirm v-if="scope.row.username!='admin'" title="您确定要对这个用户重置密码吗？"
                         @confirm="handleResetPassword(scope.row.id)">
            <template #reference>
              <el-button type="warning" :icon="RefreshRight">重置密码</el-button>
            </template>
          </el-popconfirm>

          <el-button type="primary" v-if="scope.row.username!='admin'" :icon="Edit"
                     @click="handleDialogValue(scope.row.id)"></el-button>
          <el-popconfirm v-if="scope.row.username!='admin'" title="您确定要删除这条记录吗？"
                         @confirm="handleDelete(scope.row.id)">
          <template #reference>
            <el-button type="danger" :icon="Delete"/>
          </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
        v-model:currentPage="queryForm.pageNum"
        v-model:page-size="queryForm.pageSize"
        :page-sizes="[10, 20, 30, 40]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
    />
    <Dialog v-model="dialogVisible" :dialogVisible="dialogVisible" :id="id" :dialogTitle="dialogTitle"
            @initUserList="initUserList"></Dialog>
    <RoleDialog v-model="roleDialogVisible" :sysRoleList="sysRoleList" :roleDialogVisible="roleDialogVisible" :id="id"
                @initUserList="initUserList"></RoleDialog>
  </div>
</template>





<script setup>
import requestUtil,{getServerUrl} from '@/util/request'
import {Search, Delete, DocumentAdd, Edit, Tools, RefreshRight} from '@element-plus/icons-vue'
import {ref, computed} from "vue";
import Dialog from './components/dialog'
import {ElMessage} from 'element-plus'
import RoleDialog from './components/roleDialog'






const tableData = ref([])
const total=ref(0)
const queryForm=ref({
  query:'',
  pageNum:1,
  pageSize:10
})

const dialogVisible = ref(false)

const dialogTitle = ref("")

const id = ref(-1)

const sysRoleList = ref([])

const roleDialogVisible = ref(false)

const delBtnStatus = ref(true)

const multipleSelection = ref([])

// 获取当前用户信息
const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser") || '{}')
const currentUserRoleId = currentUser.role_id

// 判断当前用户是否为管理员（超级管理员或管理员角色）
const isAdmin = computed(() => {
  // 优先通过角色名称判断（更可靠）
  if (currentUser.roles && typeof currentUser.roles === 'string') {
    const hasAdminRole = currentUser.roles.includes('管理员') || 
                        currentUser.roles.includes('超级管理员') ||
                        currentUser.roles.toLowerCase().includes('admin')
    if (hasAdminRole) {
      return true
    }
  }
  
  // 其次通过 role_id 判断（role_id 为 1 表示管理员）
  if (currentUserRoleId === 1 || currentUserRoleId === '1') {
    return true
  }
  
  return false
})

const handleSelectionChange = (selection) => {
  console.log("勾选了")
  console.log(selection)
  multipleSelection.value = selection;
  delBtnStatus.value = selection.length == 0;
}

const handleDialogValue = (userId) => {
  if (userId) {
    id.value = userId;
    dialogTitle.value = "用户修改"
  } else {
    id.value = -1;
    dialogTitle.value = "用户添加"
  }
  dialogVisible.value = true
}

const initUserList=async ()=>{
  const res=await requestUtil.post("user/search",queryForm.value)
  tableData.value=res.data.userList
  total.value=res.data.total
}

const handleSizeChange=(pageSize)=>{
  queryForm.value.pageSize=pageSize
  queryForm.value.pageNum=1
  initUserList()
}

const handleCurrentChange=(pageNum)=>{
  queryForm.value.pageNum=pageNum
  initUserList()
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
  const res = await requestUtil.del("user/action", ids)
  if (res.data.code == 200) {
    ElMessage({
      type: 'success',
      message: '执行成功!'
    })
    initUserList();
  } else {
    ElMessage({
      type: 'error',
      message: res.data.msg,
    })
  }
}

const getGenderText = (gender) => {
  const genderMap = {
    1: '男',
    2: '女',
    3: '保密'
  }
  return genderMap[gender] || '未知'
}

const handleResetPassword = async (id) => {
  const res = await requestUtil.get("user/resetPassword?id=" + id)
  if (res.data.code == 200) {
    ElMessage({
      type: 'success',
      message: '执行成功!'
    })
    initUserList();
  } else {
    ElMessage({
      type: 'error',
      message: res.data.msg,
    })
  }
}


const statusChangeHandle = async (row) => {
  let res = await requestUtil.post("user/status", {id: row.id, status: row.status});
  if (res.data.code == 200) {
    ElMessage({
      type: 'success',
      message: '执行成功!'
    })
  } else {
    ElMessage({
      type: 'error',
      message: res.data.msg,
    })
    initUserList();
  }
}

const handleRoleDialogValue = (userId, roleList) => {
  console.log("roleList：", roleList)
  console.log("id:", id)
  id.value = userId;
  sysRoleList.value = roleList;
  roleDialogVisible.value = true
}
initUserList()
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