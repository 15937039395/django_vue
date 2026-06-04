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

      <el-form-item label="上级部门" prop="parent_id">
        <el-select v-model="form.parent_id" placeholder="请选择上级部门">
          <template v-for="item in tableData">
            <el-option :label="item.name" :value="item.id"></el-option>
            <template v-for="child in item.children">
              <el-option :label="child.name" :value="child.id">
                <span>{{ "    -- " + child.name }}</span>
              </el-option>
            </template>
          </template>
        </el-select>
      </el-form-item>
      <el-form-item label="部门名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="部门类型" prop="type">
        <el-select v-model="form.type" placeholder="请选择部门类型">
          <el-option label="待分配" value="0" />
          <el-option label="公司" value="1" />
          <el-option label="子公司" value="2" />
          <el-option label="部门" value="3" />
          <el-option label="小组" value="4" />
        </el-select>
      </el-form-item>



      <el-form-item label="上级部门ID" prop="pid">
        <el-input v-model="form.pid" />
      </el-form-item>

      <el-form-item label="排序" prop="sort" >
        <el-input-number v-model="form.sort" :min="1" label="排序"></el-input-number>
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" />
      </el-form-item>



    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="handleConfirm">确认</el-button>
        <el-button  @click="handleClose">取消</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>

import {defineEmits, defineProps, ref, watch} from "vue";
import requestUtil,{getServerUrl} from "@/util/request";
import { ElMessage } from 'element-plus'


const tableData=ref([])


const props=defineProps(
    {
      id:{
        type:Number,
        default:-1,
        required:true
      },
      dialogTitle:{
        type:String,
        default:'',
        required:true
      },
      dialogVisible:{
        type:Boolean,
        default:false,
        required:true
      },
      tableData:{
        type:Array,
        default:[],
        required:true
      }
    }
)


const form=ref({
  id:-1,
  name:'',
  type:'',
  pid:'',
  sort:1,
  remark:''
})

const rules=ref({
  parentId:[
    { required: true, message: '请选择上级部门'}
  ],
  name: [{ required: true, message: "部门名称不能为空", trigger: "blur" }]
})

const formRef=ref(null)

const initFormData=async(id)=>{
  const res=await requestUtil.get("department/action?id="+id);
  form.value=res.data.menu;
}



watch(
    ()=>props.dialogVisible,
    ()=>{
      let id=props.id;
      tableData.value=props.tableData;
      if(id!=-1){
        initFormData(id)
      }else{
        form.value={
          id:-1,
          name:'',
          type:'',
          pid:'',
          sort:1,
          remark:''
        }
      }
    }
)


const emits=defineEmits(['update:modelValue','initMenuList'])

const handleClose=()=>{
  emits('update:modelValue',false)
}

const handleConfirm=()=>{
  formRef.value.validate(async(valid)=>{
    if(valid){
      let result=await requestUtil.post("department/save",form.value);
      let data=result.data;
      if(data.code==200){
        ElMessage.success("执行成功！")
        formRef.value.resetFields();
        emits("initMenuList")
        handleClose();
      }else{
        ElMessage.error(data.msg);
      }
    }else{
      console.log("fail")
    }
  })
}

</script>

<style scoped>

</style>
