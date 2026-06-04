<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <el-dialog
    :model-value="dialogVisible"
    :title="dialogTitle"
    width="30%"
    @close="handleClose"
    @open="handleDialogOpen"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="项目编号及名称" prop="project_number">
        <el-input v-model="form.project_number" placeholder="请输入项目编号及名称"/>
      </el-form-item>
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
import { defineEmits, defineProps, ref, nextTick } from "vue";
import requestUtil from "@/util/request";
import { ElMessage } from 'element-plus';

// 1. 修复props定义（确保dialogVisible双向绑定正确）
const props = defineProps({
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
});

// 2. 修复表单初始化（新增时缺少project_number字段）
const form = ref({
  id: -1,
  project_number: ""  // 确保新增时该字段存在
});

// 3. 增加表单验证（可选，但推荐，避免空提交）
const rules = ref({
  project_number: [
    { required: true, message: '请输入项目编号及名称', trigger: 'blur' }
  ]
});

const formRef = ref(null);
const emits = defineEmits(['update:modelValue', 'initItemsList']);

// 4. 优化初始化逻辑：对话框打开时执行（比watch更精准）
const handleDialogOpen = async () => {
  // 先重置表单（关键：避免残留上次数据）
  await nextTick(() => {
    formRef.value?.resetFields();
  });

  const { id } = props;
  if (id !== -1) {
    // 编辑：加载数据
    try {
      const res = await requestUtil.get(`items/action?id=${id}`);
      form.value = res.data.item || { id: -1, project_number: "" };
    } catch (error) {
      ElMessage.error('数据加载失败，请重试');
      console.error('加载失败：', error);
    }
  } else {
    // 新增：获取当前用户ID并初始化
    const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {};
    form.value = {
      id: -1,
      project_number: "",
      user_id: currentUser.id || 0
    };
  }
};

// 5. 修复关闭逻辑（确保表单重置）
const handleClose = () => {
  // 关闭时重置表单，避免下次打开有残留
  formRef.value?.resetFields();
  emits('update:modelValue', false);
};

// 6. 优化确认逻辑（确保异步刷新时序正确）
const handleConfirm = async () => {
  try {
    // 先验证表单
    await formRef.value.validate();

    // 提交数据
    const result = await requestUtil.post("items/save", form.value);
    const { code, msg } = result.data || {};

    if (code === 200) {
      ElMessage.success("执行成功！");
      // 关键：重置表单（避免下次打开有残留）
      formRef.value.resetFields();
      // 触发父组件刷新列表（使用nextTick确保DOM更新完成）
      nextTick(() => {
        emits("initItemsList");
      });
      // 关闭对话框
      handleClose();
    } else {
      ElMessage.error(msg || '执行失败，请重试');
    }
  } catch (error) {
    // 表单验证失败或请求异常
    console.error('确认失败：', error);
    ElMessage.error('操作失败，请检查输入或网络状态');
  }
};
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>