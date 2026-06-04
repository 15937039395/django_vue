<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <el-dialog
      model-value="dialogVisible"
      :title="dialogTitle"
      width="30%"
      @close="handleClose"
  >

    <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
    >
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="form.name"/>
      </el-form-item>

      <el-form-item label="权限字符" prop="code">
        <el-input v-model="form.code"/>
      </el-form-item>

      <el-form-item label="数据权限" prop="data_scope">
        <el-select v-model="form.data_scope" placeholder="请选择数据权限范围" style="width: 100%">
          <el-option label="全部数据" :value="1"></el-option>
          <el-option label="本部门及下级部门" :value="2"></el-option>
          <el-option label="仅本部门" :value="3"></el-option>
          <el-option label="仅本人" :value="4"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="4"/>
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

import {defineEmits, defineProps, ref, watch} from "vue";
import requestUtil, {getServerUrl} from "@/util/request";
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


const form = ref({
  id: -1,
  name: "",
  code: "",
  data_scope: 4,  // 默认值：仅本人
  remark: ""
})


const rules = ref({
  name: [
    {required: true, message: '请输入角色名称'}
  ],
  code: [
    {required: true, message: '请输入权限字符'}
  ]
})

const formRef = ref(null)

const initFormData = async (id) => {
  const res = await requestUtil.get("role/action?id=" + id);
  const roleData = res.data.role;
  // 确保 data_scope 是数字类型
  form.value = {
    ...roleData,
    data_scope: Number(roleData.data_scope) || 4  // 转换为数字，默认仅本人
  };
}


watch(
    () => props.dialogVisible,
    () => {
      let id = props.id;
      if (id != -1) {
        initFormData(id)
      } else {
        form.value = {
          id: -1,
          name: "",
          code: "",
          data_scope: 4,  // 默认值：仅本人
          remark: ""
        }

      }
    }
)


const emits = defineEmits(['update:modelValue', 'initRoleList'])

const handleClose = () => {
  emits('update:modelValue', false)
}

const handleConfirm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      let result = await requestUtil.post("role/save", form.value);
      let data = result.data;
      if (data.code == 200) {
        ElMessage.success("执行成功！")
        formRef.value.resetFields();
        emits("initRoleList")
        handleClose();
      } else {
        ElMessage.error(data.msg);
      }
    } else {
      console.log("fail")
    }
  })
}

</script>

<style scoped>

</style>
