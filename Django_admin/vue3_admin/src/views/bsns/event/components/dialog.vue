<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿
<template>
  <!-- 保持原有模板不变 -->
  <el-dialog
    :model-value="dialogVisible"
    :title="dialogTitle"
    width="600"
    @close="handleClose"
    @closed="onDialogClosed"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="150px"
      style="height: 600px;overflow-y: auto"
    >
      <!-- 表单内容保持不变 -->
      <el-form-item label="部门" prop="dept_id">
        <el-select v-model="form.dept_id" placeholder="请选择部门">
          <el-option
            v-for="dept in deptList"
            :key="dept.id"
            :label="dept.name"
            :value="dept.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="用户名" prop="user_id">
        <el-select v-model="form.user_id" placeholder="请选择用户名">
          <el-option
            v-for="user in userList"
            :key="user.id"
            :label="user.realname"
            :value="user.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="事件名称" prop="event_name">
        <el-input v-model="form.event_name" type="textarea" :rows="8" />
      </el-form-item>
      <el-form-item label="负责人" prop="principal">
        <el-select v-model="form.principal" placeholder="请选择负责人">
          <el-option
            v-for="user in userList"
            :key="user.id"
            :label="user.realname"
            :value="user.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="项目起始时间" prop="start_date">
        <el-date-picker
          v-model="form.start_date"
          type="date"
          placeholder="选择项目起始时间"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD">
        </el-date-picker>
      </el-form-item>

      <el-form-item label="项目终止时间" prop="end_date">
        <el-date-picker
          v-model="form.end_date"
          type="date"
          placeholder="选择项目终止时间"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD">
        </el-date-picker>
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="4"/>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleConfirm"
        >
          {{ submitting ? '提交中...' : '确认' }}
        </el-button>
        <el-button @click="handleClose">取消</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { defineEmits, defineProps, ref, watch, nextTick, onUnmounted } from "vue";
import requestUtil from "@/util/request";
import { ElMessage } from "element-plus";

const props = defineProps({
  id: {
    type: Number,
    default: -1,
    required: true,
  },
  dialogTitle: {
    type: String,
    default: "",
    required: true,
  },
  dialogVisible: {
    type: Boolean,
    default: false,
    required: true,
  },
});




// 安全地获取当前用户信息
const getCurrentUser = () => {
  try {
    const userStr = window.sessionStorage.getItem("currentUser");
    if (userStr) {
      const parsed = JSON.parse(userStr);
      // 验证用户对象的基本结构
      if (parsed && typeof parsed === 'object' &&
          (typeof parsed.id !== 'undefined') &&
          (typeof parsed.dept_id !== 'undefined')) {
        return parsed;
      }
    }
  } catch (e) {
    console.error("解析当前用户信息失败:", e);
  }
  return null;
};

const currentUser = getCurrentUser();

const form = ref({
  id: -1,
  dept_id: "",
  user_id: "",
  event_name: "",
  principal: "",
  start_date: "",
  end_date: "",
  remark: "",
});

// 选项列表（从接口获取）
const deptList = ref([]);
const userList = ref([]);

let hasLoadedOptions = false;

// 获取部门列表
const getDeptList = async () => {
  try {
    const res = await requestUtil.get("event/dept/list");
    if (res && res.data && res.data.code === 200) {
      deptList.value = Array.isArray(res.data.data) ? res.data.data : [];
    } else {
      console.warn("获取部门列表响应格式异常");
      deptList.value = [];
    }
  } catch (error) {
    ElMessage.error("获取部门列表失败");
    console.error(error);
    deptList.value = [];
  }
};

// 获取用户列表
const getUserList = async () => {
  try {
    const res = await requestUtil.get("event/user/list");
    if (res && res.data && res.data.code === 200) {
      userList.value = Array.isArray(res.data.data) ? res.data.data : [];
    } else {
      console.warn("获取用户列表响应格式异常");
      userList.value = [];
    }
  } catch (error) {
    ElMessage.error("获取用户列表失败");
    console.error(error);
    userList.value = [];
  }
};

// 加载所有选项数据
const loadOptionData = async () => {
  if (!hasLoadedOptions) {
    await Promise.all([getDeptList(), getUserList()]);
    hasLoadedOptions = true;
  }
};

const rules = ref({
  dept_id: [{ required: true, message: "请选择部门", trigger: "change" }],
  user_id: [{ required: true, message: "请选择用户", trigger: "change" }],
});

const formRef = ref(null);
const submitting = ref(false); // 提交状态标志

// 防抖函数 - 改进版本，支持异步操作
let submitTimeoutId = null;
let lastSubmitTime = 0;

// 清理定时器函数
const clearSubmitTimeout = () => {
  if (submitTimeoutId) {
    clearTimeout(submitTimeoutId);
    submitTimeoutId = null;
  }
};

// 组件卸载时清理定时器
onUnmounted(() => {
  clearSubmitTimeout();
});

const submitForm = async () => {
  if (!formRef.value || submitting.value) return;

  submitting.value = true;

  try {
    const result = await requestUtil.post("event/save", form.value);
    const data = result.data;
    if (data && data.code === 200) {
      ElMessage.success("执行成功！");
      emits("initEventList");
      // 直接关闭弹窗，不再使用延迟
      handleClose();
    } else {
      ElMessage.error(data?.msg || "保存失败");
    }
  } catch (err) {
    ElMessage.error("保存失败，请稍后再试");
    console.error(err);
  } finally {
    submitting.value = false;
  }
};

// 防抖提交函数 - 改进版本
const debouncedSubmit = () => {
  const now = Date.now();
  const timeSinceLastSubmit = now - lastSubmitTime;

  if (timeSinceLastSubmit < 1000 && submitting.value) {
    return; // 如果上次提交还在进行中且时间间隔小于1秒，则不执行
  }

  clearSubmitTimeout();

  submitTimeoutId = setTimeout(() => {
    lastSubmitTime = Date.now();
    submitForm();
  }, 1000);
};

const initFormData = async (id) => {
  // 验证ID参数
  if (typeof id !== 'number' || id <= 0) {
    throw new Error('无效的ID参数');
  }

  const res = await requestUtil.get(`event/action?id=${encodeURIComponent(id)}`);
  if (res && res.data && res.data.event) {
    // 对返回的数据进行基本验证，防止XSS
    const eventData = res.data.event;
    form.value = {
      id: eventData.id || -1,
      dept_id: eventData.dept_id || "",
      user_id: eventData.user_id || "",
      event_name: eventData.event_name || "", // 这里应该由后端处理XSS，前端也可以进一步处理
      principal: eventData.principal || "",
      start_date: eventData.start_date || "",
      end_date: eventData.end_date || "",
      remark: eventData.remark || "",
    };
  } else {
    console.warn("初始化表单数据响应格式异常");
    // 重置表单为默认值
    form.value = {
      id: -1,
      dept_id: currentUser?.dept_id || "",
      user_id: currentUser?.id || "",
      event_name: "",
      principal: "",
      start_date: "",
      end_date: "",
      remark: "",
    };
  }
};

watch(
  () => props.dialogVisible,
  async (newVal) => {
    if (newVal) {
      await loadOptionData();
      const id = props.id;
      if (id !== -1) {
        try {
          await initFormData(id);
        } catch (error) {
          console.error("初始化表单数据失败:", error);
          ElMessage.error("加载数据失败");
          // 在加载失败时也重置表单
          form.value = {
            id: -1,
            dept_id: currentUser?.dept_id || "",
            user_id: currentUser?.id || "",
            event_name: "",
            principal: "",
            remark: "",
          };
        }
      } else {
        form.value = {
          id: -1,
          dept_id: currentUser?.dept_id || "",
          user_id: currentUser?.id || "",
          event_name: "",
          principal: "",
          remark: "",
        };
      }
      // 重置表单验证状态
      nextTick(() => {
        if (formRef.value) {
          formRef.value.clearValidate();
        }
      });
    }
  }
);

// 定义emit事件，明确类型（增强可读性）
const emits = defineEmits(["update:dialogVisible", "initEventList"]);



// 修改 handleClose 函数 - 保持原有的关闭逻辑
const handleClose = () => {
  console.log("关闭对话框"); // 调试日志

  // 清理防抖定时器
  clearSubmitTimeout();

  // 重置提交状态
  submitting.value = false;

  // 触发父组件更新弹窗状态
  emits("update:dialogVisible", false);

  // 重置表单验证状态（避免下次打开残留验证提示）
  nextTick(() => {
    if (formRef.value) {
      formRef.value.clearValidate();
    }
  });

  // 如果是新增模式，重置表单数据
  if (props.id === -1) {
    nextTick(() => {
      form.value = {
        id: -1,
        dept_id: currentUser?.dept_id || "",
        user_id: currentUser?.id || "",
        event_name: "",
        principal: "",
        remark: "",
      };
    });
  }
};

// 修改 onDialogClosed 函数
const onDialogClosed = () => {
  // 清理工作已完成在 handleClose 中，此处可留空或做其他清理工作
  console.log('Dialog closed');
};

// 优化 handleConfirm 函数 - 使用防抖
const handleConfirm = async () => {
  if (!formRef.value) return;

  // 先验证表单
  const valid = await formRef.value.validate().catch(() => false);
  if (valid) {
    debouncedSubmit();
  } else {
    ElMessage.warning("请完善必填项");
  }
};
</script>

<style scoped></style>
