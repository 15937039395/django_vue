<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <el-dialog
      model-value="dialogVisible"
      :title="dialogTitle"
      width="30%"
      @close="handleClose"
  >

    <el-form
        v-if="form"
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
    >

      <el-form-item label="企业名称" prop="name">
        <el-input v-model="form.name"/>
      </el-form-item>
      <el-form-item label="合同履约日期" prop="contract_time">
        <el-date-picker
          v-model="form.contract_time"
          type="date"
          placeholder="请选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"          style="width: 100%"
        />
      </el-form-item>
       <el-form-item label="逾期日期" prop="deadline_time">
        <el-date-picker
          v-model="form.deadline_time"
          type="date"
          placeholder="请选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="类型" prop="types">
        <el-input v-model="form.types"/>
      </el-form-item>

      <el-form-item label="状态" prop="status">
        <el-input v-model="form.status"  />
      </el-form-item>
      <el-form-item label="金额类型" prop="amount_type">
        <el-select v-model="form.amount_type" placeholder="请选择金额类型">
          <el-option label="合同金额" value="1"></el-option>
          <el-option label="订单金额" value="2"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="金额" prop="amount">
        <el-input v-model="form.amount" />
      </el-form-item>

      <el-form-item label="备案信息" prop="archival_information">
        <el-select
          v-model="form.archival_information"
          placeholder="请选择备案状态"
        >
          <el-option label="有备案" value="有备案"></el-option>
          <el-option label="无备案" value="无备案"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="实际日期" prop="actual_time">
        <el-date-picker
          v-model="form.actual_time"
          type="date"
          placeholder="请选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" />
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

import {defineEmits, defineProps, ref, watch,reactive} from "vue";
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


const form = ref({
  id: -1,
  name: "",
  contract_time: null,
  deadline_time: null,
  types: "",
  status: "",
  amount_type: "",
  amount: "",
  archival_information: "",
  actual_time: null,
  remark: ""
})




const rules = ref({

})

const formRef = ref(null)

const initFormData = async (id) => {
  const res = await requestUtil.get("blacklist/action?id=" + id);
  form.value = res.data.blacklist;

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
          contract_time: null,
          deadline_time: null,
          types: null,
          status: null,
          amount_type: null,
          amount: null,
          archival_information: null,
          actual_time: null,
          remark: null
        }

      }
    }
)


const emits = defineEmits(['update:modelValue', 'initBacklistList'])

const handleClose = () => {
  emits('update:modelValue', false)
}

const handleConfirm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      let result = await requestUtil.post("blacklist/save", form.value);
      let data = result.data;
      if (data.code == 200) {
        ElMessage.success("执行成功！")
        formRef.value.resetFields();
        emits("initBacklistList")
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
