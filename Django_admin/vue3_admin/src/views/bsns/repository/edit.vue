<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="app-container">
    <el-page-header @back="goBack" :content="`编辑知识库 - ${form.title || '未命名'}`" />
    
    <el-card style="margin-top: 20px;">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
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
            <el-form-item label="所属事件" prop="event_id">
              <el-select v-model="form.event_id" placeholder="请输入或者下拉选择" style="width: 100%" filterable>
                <el-option
                  v-for="event in eventList"
                  :key="event.id"
                  :label="event.event_name"
                  :value="event.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="事件发生时间" prop="event_occur_time">
              <el-date-picker
                v-model="form.event_occur_time"
                type="date"
                placeholder="选择事件发生时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%">
              </el-date-picker>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="发生地点" prop="address">
              <el-input v-model="form.address" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="类型" prop="types">
              <el-select v-model="form.types" placeholder="请下拉选择" style="width: 100%">
                <el-option label="内部事件" :value="1" />
                <el-option label="外部事件" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="分类" prop="classify">
              <el-select v-model="form.classify" placeholder="请输入或者下拉选择" style="width: 100%" filterable>
                <el-option
                  v-for="classify in classifyList"
                  :key="classify.id"
                  :label="classify.project_number"
                  :value="classify.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="标题" prop="title">
              <el-input v-model="form.title" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="可见性" prop="visibility">
              <el-radio-group v-model="form.visibility">
                <el-tooltip content="仅您自己可以查看此记录" placement="top">
                  <el-radio :label="1">仅自己</el-radio>
                </el-tooltip>
                <el-tooltip content="您所在部门的成员可以查看" placement="top">
                  <el-radio :label="2">部门</el-radio>
                </el-tooltip>
                <el-tooltip content="所有内部人员都可以查看" placement="top">
                  <el-radio :label="3">全员</el-radio>
                </el-tooltip>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="内容" prop="content" label-width="80px" style="margin-left: 0; margin-right: 0;">
          <QuillEditor v-model="form.content" placeholder="请输入内容..." />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="submitting" 
            @click="handleTempSave">
            临时保存
          </el-button>
          <el-button
            type="success"
            :loading="submitting"
            @click="handleConfirm">
            确认
          </el-button>
          <el-button @click="goBack">取消</el-button>
          <el-button type="info" @click="goToReview">复盘</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from 'vue-router';
import requestUtil from "@/util/request";
import { ElMessage } from "element-plus";

// 引入 Quill 编辑器组件
import QuillEditor from '@/components/QuillEditor/index.vue';

const route = useRoute();
const router = useRouter();

// 表单数据
const form = ref({
  id: -1,
  dept_id: 0,
  user_id: 0,
  event_id: null,
  event_occur_time: "",
  address: "",
  types: null,
  classify: null,
  title: "",
  content: "",
  visibility: 3,  // 默认全员可见
  remark: "",
});

// 选项列表（从接口获取）
const deptList = ref([]);
const userList = ref([]);
const eventList = ref([]);
const classifyList = ref([]);

const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {};

// 原始数据存储
const originalData = ref({});

// 获取部门列表
const getDeptList = async () => {
  try {
    const res = await requestUtil.get("repository/dept/list");
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
    const res = await requestUtil.get("repository/user/list");
    if (res.data.code === 200) {
      userList.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error("获取用户列表失败");
    console.error(error);
  }
};

// 获取事件列表
const getEventList = async () => {
  try {
    const res = await requestUtil.get("event/event/list"); // 事件列表接口
    if (res.data.code === 200) {
      eventList.value = res.data.data || [];
    } else {
      ElMessage.error(res.data.msg || "获取事件列表失败");
    }
  } catch (error) {
    ElMessage.error("获取事件列表失败");
    console.error(error);
  }
};

// 获取分类列表
const getClassifyList = async () => {
  try {
    const res = await requestUtil.get("classify/list"); // 分类列表接口
    if (res.data.code === 200) {
      classifyList.value = res.data.data || [];
    } else {
      ElMessage.error(res.data.msg || "获取分类列表失败");
    }
  } catch (error) {
    ElMessage.error("获取分类列表失败");
    console.error(error);
  }
};

// 加载所有选项数据
const loadOptionData = async () => {
  await Promise.all([getDeptList(), getUserList(), getEventList(), getClassifyList()]);
};

// 表单验证规则
const rules = ref({
  dept_id: [{ required: true, message: "请选择部门", trigger: "change" }],
  user_id: [{ required: true, message: "请选择用户", trigger: "change" }],
  event_id: [{ required: true, message: "请选择所属事件", trigger: "change" }],
  event_occur_time: [{ required: true, message: "请选择事件发生时间", trigger: "change" }],
  types: [{ required: true, message: "请选择类型", trigger: "change" }],
  classify: [{ required: true, message: "请选择分类", trigger: "change" }],
  title: [{ required: true, message: "请输入标题", trigger: "blur" }],
  visibility: [{ required: true, message: "请选择可见性", trigger: "change" }],
});

const formRef = ref(null);
const submitting = ref(false);

// 初始化表单数据（编辑场景）
const initFormData = async (id) => {
  try {
    const res = await requestUtil.get("repository/action?id=" + id);
    if (res.data.code === 200 && res.data.repository) {
      const repositoryData = res.data.repository;
      // 确保数值字段为数字类型
      const loadedData = {
        ...repositoryData,
        types: Number(repositoryData.types) || null,
        classify: Number(repositoryData.classify) || null,
        dept_id: Number(repositoryData.dept_id) || 0,
        user_id: Number(repositoryData.user_id) || 0,
        event_id: Number(repositoryData.event_id) || null,
        is_temp: repositoryData.is_temp || false,
      };
      
      // 保存原始数据用于比较
      originalData.value = { ...loadedData };
      
      form.value = loadedData;
    } else {
      ElMessage.error(res.data.msg || "获取详情失败");
      // 如果获取数据失败，重定向回列表页
      router.push('/bsns/repository');
    }
  } catch (error) {
    ElMessage.error("获取详情失败");
    console.error(error);
    // 如果出现错误，重定向回列表页
    router.push('/bsns/repository');
  }
};

// 返回列表页
const goBack = () => {
  router.go(-1); // 直接返回上一页，不再弹出确认对话框
};

// 跳转到复盘页面
const goToReview = () => {
  if (form.value.id && form.value.id !== -1) {
    router.push(`/bsns/repository/detail/${form.value.id}`);
  } else {
    ElMessage.warning('请先保存当前记录再进行复盘');
  }
};

// 检查是否有编辑权限
const hasEditPermission = () => {
  // 未确认记录的创建者或管理员可以编辑
  return (form.value.user_id === currentUser.id && !form.value.confirmed) || (currentUser.role_id && Number(currentUser.role_id) === 1);
};

// 确认提交
const handleConfirm = async () => {
  if (!formRef.value) return;

  // 检查是否有编辑权限
  if (!hasEditPermission()) {
    ElMessage.error("您没有权限编辑此记录");
    return;
  }

  // 先验证表单
  const valid = await formRef.value.validate().catch(() => false);
  if (valid) {
    // 确认保存，不标记为临时保存
    const saveData = {
      ...form.value,
      is_temp: false  // 不是临时保存
    };
    await submitForm(saveData);
  } else {
    ElMessage.warning("请完善必填项");
  }
};

// 临时保存函数
const handleTempSave = async () => {
  if (!formRef.value) return;

  // 检查是否有编辑权限
  if (!hasEditPermission()) {
    ElMessage.error("您没有权限编辑此记录");
    return;
  }

  // 临时保存不需要完整验证，只验证必须的字段
  const valid = await formRef.value.validateField(['title']).catch(() => false);
  if (valid || !form.value.title.trim()) {
    // 即使标题为空也允许临时保存
    const saveData = {
      ...form.value,
      is_temp: true  // 标记为临时保存
    };
    await submitForm(saveData);
  } else {
    ElMessage.warning("请至少填写标题");
  }
};

// 提交表单的通用函数
const submitForm = async (data) => {
  submitting.value = true;
  try {
    // 确保发送给后端的数据中数值字段为数字类型
    const formDataToSend = {
      ...data,
      dept_id: Number(data.dept_id),
      user_id: Number(data.user_id),
      event_id: Number(data.event_id),
      types: Number(data.types),
      classify: Number(data.classify),
      current_role_id: currentUser.role_id  // 添加当前用户角色ID用于后端权限检查
    };
    const res = await requestUtil.post("repository/save", formDataToSend);
    if (res.data.code === 200) {
      ElMessage.success("操作成功");
      // 返回列表页面
      router.push('/bsns/repository');
    } else {
      ElMessage.error(res.data.msg || "操作失败");
    }
  } catch (error) {
    ElMessage.error("提交请求失败，请重试");
    console.error("提交失败：", error);
  } finally {
    submitting.value = false;
  }
};

onMounted(async () => {
  const id = parseInt(route.params.id);
  if (id && id !== -1) {
    await initFormData(id);
  }
  await loadOptionData();
});

// 移除 beforeRouteLeave 守卫，不再需要
</script>

<style scoped>
.app-container {
  padding: 20px;
}


</style>