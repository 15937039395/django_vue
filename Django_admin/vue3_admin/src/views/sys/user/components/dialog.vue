<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <el-dialog
      model-value="dialogVisible"
      :title="dialogTitle"
      width="40%"
      @close="handleClose"
  >

    <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="账号" prop="username">
            <el-input v-model="form.username" :disabled="form.id === -1 ? false : true"/>
            <el-alert
                v-if="form.id === -1"
                title="默认初始密码：123456"
                :closable="false"
                style="line-height: 10px;"
                type="success">
            </el-alert>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="姓名" prop="realname">
            <el-input v-model="form.realname"/>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="花名" prop="nickname">
            <el-input v-model="form.nickname"/>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别" prop="gender">
            <el-select v-model="form.gender" placeholder="请选择性别">
              <el-option label="男" :value="1"></el-option>
              <el-option label="女" :value="2"></el-option>
              <el-option label="保密" :value="3"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone"/>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email"/>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="部门" prop="dept_id">
            <el-select v-model="form.dept_id" placeholder="请选择部门">
              <el-option
                v-for="dept in deptList"
                :key="dept.id"
                :label="dept.name"
                :value="dept.id">
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="岗位" prop="position_id">
            <el-select v-model="form.position_id" placeholder="请选择岗位">
              <el-option
                v-for="post in postList"
                :key="post.id"
                :label="post.name"
                :value="post.id">
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="职级" prop="level_id">
            <el-select v-model="form.level_id" placeholder="请选择职级">
              <el-option
                v-for="level in levelList"
                :key="level.id"
                :label="level.name"
                :value="level.id">
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="form.status">
              <el-radio :label="1">正常</el-radio>
              <el-radio :label="2">禁用</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="查看评论人" prop="can_view_commenter">
            <el-radio-group v-model="form.can_view_commenter">
              <el-radio :label="1">是</el-radio>
              <el-radio :label="0">否</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注" prop="remark">
            <el-input v-model="form.remark" type="textarea" :rows="4"/>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="handleConfirm">确认</el-button>
        <el-button @click="handleClose">取消</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>

import {defineEmits, defineProps, ref, watch,onMounted} from "vue";
import requestUtil from "@/util/request";
import {ElMessage} from 'element-plus'


const props = defineProps(
    {
      id: {
        type: Number,
        default: -1,
        required: true
      },
      dialogTitle: {
        type: String,
        default: '',
        required: true
      },
      dialogVisible: {
        type: Boolean,
        default: false,
        required: true
      }
    }
)

// 表单数据
const form = ref({
  id: -1,
  username: "",
  password: "123456",
  realname: "",
  nickname: "",
  gender: "",
  status: 1,
  can_view_commenter: 0,
  phone: "",
  email: "",
  remark: "",
  dept_id: "",      // 部门ID
  position_id: "",  // 岗位ID
  level_id: ""      // 职级ID
})

// 选项列表
const deptList = ref([])    // 部门列表
const postList = ref([])    // 岗位列表
const levelList = ref([])   // 职级列表

// 获取部门列表
const getDeptList = async () => {
  try {
    const res = await requestUtil.get("user/dept/list");
    if (res.data.code === 200) {
      deptList.value = res.data.deptList;
    }
  } catch (error) {
    ElMessage.error("获取部门列表失败");
    console.error(error);
  }
}

// 获取岗位列表
const getPostList = async () => {
  try {
    const res = await requestUtil.get("user/post/list");
    if (res.data.code === 200) {
      postList.value = res.data.postList;
    }
  } catch (error) {
    ElMessage.error("获取岗位列表失败");
    console.error(error);
  }
}

// 获取职级列表
const getLevelList = async () => {
  try {
    const res = await requestUtil.get("user/level/list");
    if (res.data.code === 200) {
      levelList.value = res.data.levelList;
    }
  } catch (error) {
    ElMessage.error("获取职级列表失败");
    console.error(error);
  }
}

// 加载所有选项数据
const loadOptionData = async () => {
  await Promise.all([
    getDeptList(),
    getPostList(),
    getLevelList()
  ]);
}

const checkUsername = async (rule, value, callback) => {
  if (form.value.id == -1) {
    const res = await requestUtil.post("user/check", {username: form.value.username});
    if (res.data.code == 500) {
      callback(new Error("用户名已存在！"));
    } else {
      callback();
    }
  } else {
    callback();
  }

}


const rules = ref({
  username: [
    {required: true, message: '请输入用户名'},
    {required: true, validator: checkUsername, trigger: "blur"}
  ],
  email: [{required: true, message: "邮箱地址不能为空", trigger: "blur"}, {
    type: "email",
    message: "请输入正确的邮箱地址",
    trigger: ["blur", "change"]
  }],
  phone: [{required: true, message: "手机号码不能为空", trigger: "blur"}, {
    pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/,
    message: "请输入正确的手机号码",
    trigger: "blur"
  }],
})

const formRef = ref(null)

const initFormData = async (id) => {
  const res = await requestUtil.get("user/action?id=" + id);
  form.value = res.data.user;
}


watch(
  () => props.dialogVisible,
  async (newVal) => { // 改为async函数
    if (newVal) { // 只有当对话框显示时才加载数据
      await loadOptionData(); // 等待部门/岗位/职级数据加载完成
      const id = props.id;
      if (id !== -1) {
        await initFormData(id); // 加载用户详情（依赖选项数据）
      } else {
        // 重置表单
        form.value = {
          id: -1,
          username: "",
          password: "123456",
          realname: "",
          nickname: "",
          gender: "",
          status: 1,
          can_view_commenter: 0,
          phone: "",
          email: "",
          remark: "",
          dept_id: "",
          position_id: "",
          level_id: ""
        };
      }
    }
  }
)


const emits = defineEmits(['update:modelValue', 'initUserList'])

const handleClose = () => {
  emits('update:modelValue', false)
}

const handleConfirm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      let result = await requestUtil.post("user/save", form.value);
      let data = result.data;
      if (data.code == 200) {
        ElMessage.success("执行成功！")
        formRef.value.resetFields();
        emits("initUserList")
        handleClose();
      } else {
        ElMessage.error(data.msg);
      }
    } else {
      console.log("fail")
    }
  })
}
// 组件挂载时加载数据
onMounted(() => {
  if (props.dialogVisible) {
    loadOptionData();
  }
})

</script>

<style scoped>

</style>
