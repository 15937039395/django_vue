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
      <el-form-item label="分类名称" prop="project_number">
        <el-input
          v-model="form.project_number"
          placeholder="请输入分类名称"
          :disabled="isSubmitting"
        />
      </el-form-item>
      <el-form-item label="类型" prop="types">
        <el-select
          v-model="form.types"
          placeholder="请选择类型"
          clearable
        >
          <el-option label="未分类" value="0"></el-option>
          <el-option label="分类" value="1"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button
          type="primary"
          @click="handleConfirm"
          :loading="isSubmitting"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '提交中...' : '确认' }}
        </el-button>
        <el-button @click="handleClose" :disabled="isSubmitting">取消</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { defineEmits, defineProps, ref, nextTick, unref } from "vue";
import requestUtil from "@/util/request";
import { ElMessage } from 'element-plus';

// 定义属性
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

// 表单数据
const form = ref({
  id: -1,
  project_number: ""
});

// 表单验证规则
const rules = ref({
  project_number: [
    { required: true, message: '请输入分类名称', trigger: 'blur' }
  ]
});

const formRef = ref(null);
const emits = defineEmits(['update:modelValue', 'initClassifyList']);

// 防抖相关状态
const isSubmitting = ref(false);
let submitTimeout = null;

// 防抖函数：防止重复提交
const debounceSubmit = (fn, delay = 500) => {
  return (...args) => {
    // 清除之前的定时器
    if (submitTimeout) {
      clearTimeout(submitTimeout);
    }

    // 设置新的定时器
    submitTimeout = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
};

// 对话框打开处理
const handleDialogOpen = async () => {
  await nextTick(() => {
    formRef.value?.resetFields();
  });

  const { id } = props;
  if (id !== -1) {
    try {
      const res = await requestUtil.get(`classify/action?id=${id}`);
      form.value = res.data?.item || { id: -1, project_number: "" };
    } catch (error) {
      ElMessage.error('数据加载失败，请重试');
      console.error('加载失败：', error);
    }
  } else {
    form.value = {
      id: -1,
      project_number: ""
    };
  }
};

// 关闭对话框
const handleClose = () => {
  // 清除可能存在的提交定时器
  if (submitTimeout) {
    clearTimeout(submitTimeout);
  }

  formRef.value?.resetFields();
  isSubmitting.value = false; // 重置提交状态
  emits('update:modelValue', false);
};

// 带防抖的确认处理
const handleConfirmWithDebounce = debounceSubmit(async () => {
  if (unref(isSubmitting)) {
    return; // 如果正在提交，则直接返回
  }

  try {
    isSubmitting.value = true; // 设置提交状态

    // 表单验证
    await formRef.value.validate();

    // 提交数据
    const result = await requestUtil.post("classify/save", unref(form));
    const response = result?.data;

    if (!response) {
      throw new Error('服务器响应异常');
    }

    const { code, msg } = response;

    if (code === 200) {
      ElMessage.success("执行成功！");
      // 触发父组件刷新列表
      nextTick(() => {
        emits("initClassifyList");
      });
      // 关闭对话框
      handleClose();
    } else {
      ElMessage.error(msg || '执行失败，请重试');
      isSubmitting.value = false; // 提交失败也要重置状态
    }
  } catch (error) {
    console.error('确认失败：', error);
    if (error.message !== '服务器响应异常') {
      ElMessage.error('操作失败，请检查输入或网络状态');
    }
    isSubmitting.value = false; // 发生错误时重置提交状态
  }
}, 500); // 500ms 防抖延迟

// 处理确认事件（调用防抖函数）
const handleConfirm = () => {
  handleConfirmWithDebounce();
};
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
