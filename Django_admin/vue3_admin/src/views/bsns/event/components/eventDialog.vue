<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <el-dialog

      v-model="props.eventDialogVisible"
      title="分配人员"
      width="30%"
      @close="handleClose"
  >
    <el-form
        ref="formRef"
        :model="form"
        label-width="100px"
    >
      <el-tree
          ref="treeRef"
          :data="treeData"
          :props="defaultProps"
          show-checkbox
          :default-expand-all="true"
          node-key="id"
          :check-strictly="true"
      >
        <!-- 修正2：自定义树节点渲染（关键！解决两种节点标签字段不统一问题） -->
        <template #default="{ node, data }">
          <!-- 区分节点类型：部门节点显示 dept_name，用户节点显示 realname -->
          <span v-if="data.node_type === 'dept'">
            {{ data.dept_name }}  <!-- 匹配后端部门节点的 dept_name 字段 -->
          </span>
          <span v-else-if="data.node_type === 'user'">
            {{ data.realname }}  <!-- 匹配后端用户节点的 realname 字段 -->
          </span>
        </template>
      </el-tree>
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
import { defineEmits, defineProps, ref, watch } from "vue";
import requestUtil from "@/util/request";
import { ElMessage } from 'element-plus'

// 修正3：defaultProps 仅保留 children 配置（label 由自定义 slot 处理，无需统一配置）
const defaultProps = {
  children: 'children'
}

const props = defineProps({
  id: {
    type: Number,
    default: -1,
    required: true
  },
  eventDialogVisible: {
    type: Boolean,
    default: false,
    required: true
  }
})

// 获取当前登录用户信息
const currentUser = JSON.parse(window.sessionStorage.getItem("currentUser")) || {}

const form = ref({
  id: -1
})

const treeData = ref([]);
const formRef = ref(null);
const treeRef = ref(null);

const initFormData = async (id) => {
  try {
    const res = await requestUtil.get("user/treeList");
    if (res.data.code === 200) {
      treeData.value = res.data.treeList;  // 确保后端返回数据正常赋值
    } else {
      ElMessage.error("获取树结构失败：" + res.data.msg);
    }

    form.value.id = id;
    const res2 = await requestUtil.get("event/menus?id=" + id);
    if (res2.data.code === 200) {
      treeRef.value?.setCheckedKeys(res2.data.eventIdList);  // 可选链避免空指针
    }
  } catch (e) {
    ElMessage.error("初始化数据失败：" + e.message);
  }
}

watch(
  () => props.eventDialogVisible,
  (newVal) => {  // 监听新值，只有弹窗显示时才初始化
    if (newVal && props.id !== -1) {
      initFormData(props.id);
    }
  }
)

const emits = defineEmits(['update:modelValue', 'initEventList'])

const handleClose = () => {
  emits('update:modelValue', false)
}

const handleConfirm = async () => {
  try {
    const menuIds = treeRef.value?.getCheckedKeys() || [];
    
    // 添加当前用户信息用于权限验证
    const result = await requestUtil.post("event/grant", {
      "id": form.value.id,
      "menuIds": menuIds,
      "current_role_id": currentUser.role_id,
      "current_user_id": currentUser.id
    });
    
    const data = result.data;
    if (data.code === 200) {
      ElMessage.success("执行成功！");
      emits("initEventList");
      handleClose();
    } else {
      ElMessage.error(data.msg);
    }
  } catch (e) {
    ElMessage.error("提交失败：" + e.message);
  }
}
</script>

<style scoped>
</style>