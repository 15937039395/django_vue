<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
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

      <el-form-item label="日期" prop="date_time">
        <el-date-picker
          v-model="form.date_time"
          type="date"
          placeholder="请选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width:100%"
        />
      </el-form-item>
      <el-form-item label="类型" prop="report_type">
        <el-select
          v-model="form.report_type"
          placeholder="请选择类型"
          clearable
          @change="handleTypeChange"
        >
          <el-option label="日报" value="日报"></el-option>
          <el-option label="月报" value="月报"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="编号及名称" prop="project_number">
        <el-select
          v-model="form.project_number"
          placeholder="请选择项目"
          clearable
        >
          <el-option
            v-for="item in itemList"
            :key="item.project_number"
            :label="`${item.project_number || ''} `"
            :value="item.project_number"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="工作描述" prop="job_description">
        <el-input v-model="form.job_description" type="textarea" :rows="8" />
      </el-form-item>
      <el-form-item label="存在的问题" prop="issue">
        <el-input v-model="form.issue" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item label="需协调的事项" prop="coordinate">
        <el-input v-model="form.coordinate" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item label="次日（月）工作计划" prop="work_plan">
        <el-input v-model="form.work_plan" type="textarea" :rows="6" />
      </el-form-item>

      <el-form-item label="工时" prop="man_hour">
        <el-input v-model="form.man_hour" :disabled="form.report_type === '月报'" />
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
import { defineEmits, defineProps, ref, watch, nextTick } from "vue";
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

const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser"));

const form = ref({
  id: -1,
  dept_id: "",
  user_id: "",
  date_time: "",
  report_type: "",
  project_number: "",
  job_description: "",
  man_hour: "",
  issue: "",
  coordinate: "",
  work_plan: "",
  remark: "",
});

// 类型变更时处理工时
const handleTypeChange = (val) => {
  if (val === '月报') {
    form.value.man_hour = '0'
  } else {
    form.value.man_hour = '8'
  }
}

// 选项列表（从接口获取）
const deptList = ref([]);
const userList = ref([]);
const itemList = ref([]);

let hasLoadedOptions = false;

// 获取部门列表
const getDeptList = async () => {
  try {
    const res = await requestUtil.get("manhour/dept/list");
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
    const res = await requestUtil.get("manhour/user/list");
    if (res.data.code === 200) {
      userList.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error("获取用户列表失败");
    console.error(error);
  }
};

// 获取项目列表
const getItemList = async () => {
  try {
    const res = await requestUtil.get("manhour/items/list");
    if (res.data.code === 200) {
      itemList.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error("获取项目列表失败");
    console.error(error);
  }
};

// 加载所有选项数据
const loadOptionData = async () => {
  if (!hasLoadedOptions) {
    await Promise.all([getDeptList(), getUserList(), getItemList()]);
    hasLoadedOptions = true;
  }
};

const rules = ref({
  dept_id: [{ required: true, message: "请选择部门", trigger: "change" }],
  user_id: [{ required: true, message: "请选择用户", trigger: "change" }],
  date_time: [{ required: true, message: "请选择日期", trigger: "change" }],
  report_type: [{ required: true, message: "请选择类型", trigger: "change" }],
  project_number: [{ required: true, message: "请选择项目", trigger: "change" }],
  man_hour: [{ required: true, message: "请输入工时", trigger: "blur" }],
  work_plan: [{ required: true, message: "请输入次日（月）工作计划", trigger: "blur" }],
});

const formRef = ref(null);
const submitting = ref(false); // 提交状态标志

// 防抖函数
const debounce = (func, delay) => {
  let timeoutId;
  return function (...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
};

// 原始提交函数
const submitForm = async () => {
  if (!formRef.value || submitting.value) return;

  submitting.value = true;

  try {
    const result = await requestUtil.post("manhour/save", form.value);
    const data = result.data;
    if (data.code === 200) {
      ElMessage.success("执行成功！");
      emits("initManhourList");

      // 延迟关闭以确保状态同步
      setTimeout(() => {
        handleClose();
      }, 100);
    } else {
      ElMessage.error(data.msg);
    }
  } catch (err) {
    ElMessage.error("保存失败，请稍后再试");
    console.error(err);
  } finally {
    submitting.value = false;
  }
};

// 防抖后的提交函数
const debouncedSubmit = debounce(submitForm, 1000);

const initFormData = async (id) => {
  const res = await requestUtil.get("manhour/action?id=" + id);
  form.value = res.data.manhour;
};

watch(
  () => props.dialogVisible,
  async (newVal) => {
    if (newVal) {
      await loadOptionData();
      const id = props.id;
      if (id !== -1) {
        await initFormData(id);
      } else {
        form.value = {
          id: -1,
          dept_id: currentUser?.dept_id || "",
          user_id: currentUser?.id || "",
          date_time: "",
          report_type: "",
          project_number: "",
          job_description: "",
          man_hour: "",
          issue: "",
          coordinate: "",
          work_plan: "",
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
const emits = defineEmits(["update:dialogVisible", "initManhourList"]);

// 修改 handleClose 函数
const handleClose = () => {
  // 重置提交状态
  submitting.value = false;

  // 1. 触发父组件更新弹窗状态（双向绑定核心）
  emits("update:dialogVisible", false);

  // 2. 重置表单验证状态（避免下次打开残留验证提示）
  nextTick(() => {
    if (formRef.value) {
      formRef.value.clearValidate();
    }
  });

  // 3. 如果是新增模式，重置表单数据
  if (props.id === -1) {
    nextTick(() => {
      form.value = {
        id: -1,
        dept_id: currentUser?.dept_id || "",
        user_id: currentUser?.id || "",
        date_time: "",
        report_type: "",
        project_number: "",
        job_description: "",
        man_hour: "",
        issue: "",
        coordinate: "",
        work_plan: "",
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
