<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<!--新增/编辑弹窗-->
<template>
  <el-dialog
    :model-value="dialogVisible"
    :title="dialogTitle"
    width="80%"
    top="5vh"
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
          <!-- 注意：以下字段名已和form定义对齐，若需保留原名称需同步修改form -->
          <el-form-item label="所属事件" prop="event_id">
            <el-select v-model="form.event_id" placeholder="请根据事件选择，如果没有请选择其他" style="width: 100%">
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
            <el-select v-model="form.types" placeholder="请选择类型" style="width: 100%">
              <el-option label="内部事件" :value="1" />
              <el-option label="外部事件" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="分类" prop="classify">
            <el-select v-model="form.classify" placeholder="请选择分类" style="width: 100%" filterable>
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
      </el-row>

      <el-form-item label="内容" prop="content">
        <QuillEditor v-model="form.content" placeholder="请输入内容..." />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <!-- 临时保存按钮：仅在有编辑权限或新增记录时显示 -->
        <el-button 
          v-if="hasEditPermission || props.id === -1"
          type="primary" 
          :loading="submitting" 
          @click="handleTempSave">
          临时保存
        </el-button>
        <!-- 确认按钮：仅在有编辑权限时显示 -->
        <el-button
          v-if="hasEditPermission"
          type="success"
          :loading="submitting"
          @click="handleConfirm">
          确认
        </el-button>
        <el-button @click="handleClose">取消</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { defineEmits, defineProps, ref, watch, reactive, nextTick, computed } from "vue";
import requestUtil from "@/util/request";
import { ElMessage } from "element-plus";

// 引入 Quill 编辑器组件
import QuillEditor from '@/components/QuillEditor/index.vue';

// 1. 定义props
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

// 2. 定义emit事件（明确类型）
const emits = defineEmits(["update:dialogVisible", "initRepositoryList", "updateSingleRecord"]);
const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {};

// 3. 表单数据（字段名和模板prop对齐）
const form = ref({
  id: -1,
  dept_id: 0,
  user_id: 0,
  event_id: 0,
  event_occur_time: "",
  address: "",
  types: 0,
  classify: 0,
  title: "",
  content: "",
  remark: "",
});

// 选项列表（从接口获取）
const deptList = ref([]);
const userList = ref([]);
const eventList = ref([]);
const classifyList = ref([]);
let hasLoadedOptions = false;

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
  if (!hasLoadedOptions) {
    await Promise.all([getDeptList(), getUserList(), getEventList(), getClassifyList()]);
    hasLoadedOptions = true;
  }
};

// 表单验证规则
const rules = ref({
  dept_id: [{ required: true, message: "请选择部门", trigger: "change" }],
  user_id: [{ required: true, message: "请选择用户", trigger: "change" }],
});

const formRef = ref(null);

// 初始化表单数据（编辑场景）
const initFormData = async (id) => {
  try {
    const res = await requestUtil.get("repository/action?id=" + id);
    const repositoryData = res.data.repository;
    // 确保数值字段为数字类型
    form.value = {
      ...repositoryData,
      types: Number(repositoryData.types) || 0,
      classify: Number(repositoryData.classify) || 0,
      dept_id: Number(repositoryData.dept_id) || 0,
      user_id: Number(repositoryData.user_id) || 0,
      event_id: Number(repositoryData.event_id) || 0,
      is_temp: repositoryData.is_temp || false,
    };
  } catch (error) {
    ElMessage.error("获取详情失败");
    console.error(error);
  }
};

// 监听弹窗显隐，初始化数据
watch(
  () => props.dialogVisible,
  async (newVal) => {
    if (newVal) {
      await loadOptionData();
      const id = props.id;
      if (id !== -1) {
        await initFormData(id);
      } else {
        // 新增场景：默认填充当前用户信息
        form.value = {
          id: -1,
          dept_id: Number(currentUser.dept_id) || 0,
          user_id: Number(currentUser.id) || 0,
          event_id: 0,
          event_occur_time: "",
          address: "",
          types: 0,
          classify: 0,
          title: "",
          content: "",
          remark: "",
        };
      }
      // 重置表单验证状态
      nextTick(() => {
        formRef.value?.clearValidate();
      });
    }
  },
  { immediate: false }
);

// 关闭弹窗（核心修正：通过emit通知父组件更新）
const handleClose = () => {
  emits("update:dialogVisible", false);
};

// 检查是否有编辑权限
const hasEditPermission = computed(() => {
  // 如果是新增记录，当前用户可以编辑
  if (props.id === -1) {
    return true;
  }
  // 如果是编辑记录：
  // 1. 未确认记录：创建者可以编辑
  // 2. 管理员可以编辑任何记录（包括已确认的）
  return (form.value.user_id === currentUser.id && !form.value.confirmed) || (currentUser.role_id && Number(currentUser.role_id) === 1);
});

// 确认提交（优化版本）
const handleConfirm = async () => {
  if (!formRef.value) return;

  // 检查是否有权限确认
  if (props.id !== -1 && form.value.user_id !== currentUser.id && (!currentUser.role_id || Number(currentUser.role_id) !== 1)) {
    ElMessage.error("您没有权限确认他人的记录");
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

  // 检查是否有权限临时保存
  if (props.id !== -1 && form.value.user_id !== currentUser.id && (!currentUser.role_id || Number(currentUser.role_id) !== 1)) {
    ElMessage.error("您没有权限编辑他人的记录");
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

      // 判断是新增还是编辑
      const isNew = props.id === -1;
      
      if (isNew) {
        // 新增：需要刷新列表以获取关联数据（部门、用户、事件名称等）
        emits("initRepositoryList");
        
        // 重置表单数据
        form.value = {
          id: -1,
          dept_id: Number(currentUser.dept_id) || 0,
          user_id: Number(currentUser.id) || 0,
          event_id: 0,
          event_occur_time: "",
          address: "",
          types: 0,
          classify: 0,
          title: "",
          content: "",
          remark: "",
        };
      } else {
        // 编辑：通知父组件局部更新单条记录，避免刷新整个列表
        if (res.data.repository) {
          emits("updateSingleRecord", res.data.repository);
        } else {
          // 如果后端没有返回记录，则刷新列表
          emits("initRepositoryList");
        }
      }

      // 关闭弹窗
      emits("update:dialogVisible", false);
    } else {
      ElMessage.error(res.data.msg || "操作失败");
    }
  } catch (error) {
    ElMessage.error("提交请求失败，请重试");
    console.error("提交失败：", error);
  }
};
</script>

<style scoped>
/* 防止编辑器选择时出现异常样式 */
.w-e-text-container ::selection {
  background-color: #b3d7ff;
  color: #000;
}

.w-e-text-container ::-moz-selection {
  background-color: #b3d7ff;
  color: #000;
}

/* 针对表格选择的特殊处理 */
.w-e-text-container table ::selection {
  background: transparent;
}

.w-e-text-container table ::-moz-selection {
  background: transparent;
}

.w-e-text-container td::selection,
.w-e-text-container th::selection {
  background: transparent;
}

.w-e-text-container td::-moz-selection,
.w-e-text-container th::-moz-selection {
  background: transparent;
}

/* 确保编辑器内所有元素的选择样式正常 */
.w-e-text-container *::selection {
  background: transparent;
}

.w-e-text-container *::-moz-selection {
  background: transparent;
}
</style>