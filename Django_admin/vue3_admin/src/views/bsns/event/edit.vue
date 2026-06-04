<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-page-header @back="goBack" :content="`编辑事件 - ${form.event_name || '未命名'}`" />
    
    <el-card style="margin-top: 20px;">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="150px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门" prop="dept_id">
              <el-select v-model="form.dept_id" placeholder="请选择部门" style="width: 100%">
                <el-option
                  v-for="dept in deptList"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="用户名" prop="user_id">
              <el-select v-model="form.user_id" placeholder="请选择用户名" style="width: 100%">
                <el-option
                  v-for="user in userList"
                  :key="user.id"
                  :label="user.realname"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="事件名称" prop="event_name">
              <el-input v-model="form.event_name" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="负责人" prop="principal">
              <el-select v-model="form.principal" placeholder="请选择负责人" style="width: 100%" filterable>
                <el-option
                  v-for="user in userList"
                  :key="user.id"
                  :label="user.realname"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="项目起始时间" prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="选择项目起始时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%">
              </el-date-picker>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="项目终止时间" prop="end_date">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="选择项目终止时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%">
              </el-date-picker>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="配置通知时间" prop="notification_time">
              <el-date-picker
                v-model="form.notification_time"
                type="datetime"
                placeholder="请选择通知参与人员维护事件时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%">
              </el-date-picker>
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" type="textarea" :rows="4" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="submitting" 
            @click="handleConfirm">
            确认
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue";
import { useRoute, useRouter } from 'vue-router';
import requestUtil from "@/util/request";
import { ElMessage } from "element-plus";

const route = useRoute();
const router = useRouter();

// 表单数据
const form = ref({
  id: -1,
  dept_id: "",
  user_id: "",
  event_name: "",
  principal: "",
  start_date: "",
  end_date: "",
  notification_time: "",
  remark: "",
});

// 选项列表
const deptList = ref([]);
const userList = ref([]);

const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {};

// 表单验证规则
const rules = ref({
  dept_id: [{ required: true, message: "请选择部门", trigger: "change" }],
  user_id: [{ required: true, message: "请选择用户", trigger: "change" }],
  event_name: [{ required: true, message: "请输入事件名称", trigger: "blur" }],
  principal: [{ required: true, message: "请选择负责人", trigger: "change" }],
  start_date: [{ required: true, message: "请选择项目起始时间", trigger: "change" }],
  end_date: [{ required: true, message: "请选择项目终止时间", trigger: "change" }],
  notification_time: [{ required: true, message: "请选择通知参与人员维护事件时间", trigger: "change" }],
});

const formRef = ref(null);
const submitting = ref(false);

// 获取部门列表
const getDeptList = async () => {
  try {
    const res = await requestUtil.get("event/dept/list");
    if (res.data.code === 200) {
      deptList.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error("获取部门列表失败");
    console.error(error);
  }
};

// 获取用户列表
const getUserList = async () => {
  try {
    const res = await requestUtil.get("event/user/list");
    if (res.data.code === 200) {
      userList.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error("获取用户列表失败");
    console.error(error);
  }
};

// 加载所有选项数据
const loadOptionData = async () => {
  await Promise.all([getDeptList(), getUserList()]);
};

// 初始化表单数据（编辑场景）
const initFormData = async (id) => {
  try {
    const res = await requestUtil.get(`event/action?id=${id}`);
    if (res.data.code === 200 && res.data.event) {
      const eventData = res.data.event;
      // 从后端获取的数据，其中包含名称字段
      const { dept_name, user_name, principal_name, ...otherEventData } = eventData;
      
      form.value = {
        ...otherEventData,
        id: eventData.id || -1,
        dept_id: eventData.dept_id || "",
        user_id: eventData.user_id || "",
        event_name: eventData.event_name || "",
        principal: eventData.principal || "",
        start_date: eventData.start_date || "",
        end_date: eventData.end_date || "",
        notification_time: eventData.notification_time || "",
        remark: eventData.remark || "",
      };
      
      // 等待组件渲染后，再设置下拉框的值
      await nextTick();
      
      // 设置部门下拉框的值为名称（显示），但实际值是ID
      if (dept_name) {
        const deptOption = deptList.value.find(dept => dept.name === dept_name);
        if (deptOption) {
          form.value.dept_id = deptOption.id;
        }
      }
      
      // 设置用户名下拉框的值
      if (user_name) {
        const userOption = userList.value.find(user => user.realname === user_name);
        if (userOption) {
          form.value.user_id = userOption.id;
        }
      }
      
      // 设置负责人下拉框的值
      if (principal_name) {
        const principalOption = userList.value.find(user => user.realname === principal_name);
        if (principalOption) {
          form.value.principal = principalOption.id;
        }
      }
    } else {
      ElMessage.error(res.data.msg || "获取详情失败");
      // 如果获取数据失败，重定向回列表页
      router.push('/bsns/event');
    }
  } catch (error) {
    ElMessage.error("获取详情失败");
    console.error(error);
    // 如果出现错误，重定向回列表页
    router.push('/bsns/event');
  }
};

// 返回列表页
const goBack = () => {
  router.go(-1); // 直接返回上一页
};

// 确认提交
const handleConfirm = async () => {
  if (!formRef.value) return;

  // 先验证表单
  const valid = await formRef.value.validate().catch(() => false);
  if (valid) {
    submitting.value = true;
    try {
      // 添加当前用户角色信息用于权限验证
      const submitData = {
        ...form.value,
        current_role_id: currentUser.role_id
      }
      
      const res = await requestUtil.post("event/save", submitData);
      if (res.data.code === 200) {
        ElMessage.success("操作成功");
        // 跳转到列表页并自动打开关联人员弹窗
        router.push({
          path: '/bsns/event',
          query: { openGrant: res.data.id }
        });
      } else {
        ElMessage.error(res.data.message || res.data.msg || "操作失败");
      }
    } catch (error) {
      ElMessage.error("提交请求失败，请重试");
      console.error("提交失败：", error);
    } finally {
      submitting.value = false;
    }
  } else {
    ElMessage.warning("请完善必填项");
  }
};

onMounted(async () => {
  // 先加载选项数据
  await loadOptionData();
  
  const id = parseInt(route.params.id);
  if (id && id !== -1) {
    await initFormData(id);
  }
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}
</style>