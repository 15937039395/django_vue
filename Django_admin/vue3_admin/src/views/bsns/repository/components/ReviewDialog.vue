<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑复盘' : '添加复盘'"
    width="80%"
    top="5vh"
    @close="handleClose"
  >
    <el-form
      ref="reviewFormRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      style="max-height: 60vh; overflow-y: auto;"
    >
      <!-- 复盘内容 -->
      <el-form-item label="发生了什么" prop="what_happened">
        <el-input
          v-model="formData.what_happened"
          type="textarea"
          :rows="4"
          placeholder="详细描述事件的实际发生情况，包括关键节点、重要决策和具体行动"
        />
      </el-form-item>

      <el-form-item label="做得好的地方" prop="what_went_well">
        <el-input
          v-model="formData.what_went_well"
          type="textarea"
          :rows="3"
          placeholder="列出本次事件中成功和表现积极的方面"
        />
      </el-form-item>

      <el-form-item label="需要改进的地方" prop="what_not_went_well">
        <el-input
          v-model="formData.what_not_went_well"
          type="textarea"
          :rows="3"
          placeholder="识别过程中遇到的问题、挑战和不足之处"
        />
      </el-form-item>

      <el-form-item label="学到的经验" prop="lessons_learned">
        <el-input
          v-model="formData.lessons_learned"
          type="textarea"
          :rows="3"
          placeholder="总结从本次事件中获得的关键经验和教训"
        />
      </el-form-item>

      <el-form-item label="行动计划与方案" prop="action_items">
        <el-input
          v-model="formData.action_items"
          type="textarea"
          :rows="4"
          placeholder="制定未来如何改进的具体措施和行动计划"
        />
      </el-form-item>

      <!-- 评分部分 -->
      <el-divider content-position="left">评分</el-divider>
      
      <el-form-item label="有效性评分" prop="effectiveness_score">
        <el-rate
          v-model="formData.effectiveness_score"
          :max="10"
          show-score
          score-template="{value}分"
          style="margin-top: 8px;"
        />
      </el-form-item>

      <el-form-item label="改进潜力评分" prop="improvement_potential">
        <el-rate
          v-model="formData.improvement_potential"
          :max="10"
          show-score
          score-template="{value}分"
          style="margin-top: 8px;"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '更新' : '保存' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getRepositoryDetail, saveReview, updateReview } from '@/views/bsns/repository/api'

const props = defineProps({
  repositoryId: {
    type: Number,
    required: true
  },
  reviewData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['success', 'close'])

const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)

const reviewFormRef = ref()

// 表单数据
const formData = reactive({
  what_happened: '',
  what_went_well: '',
  what_not_went_well: '',
  lessons_learned: '',
  action_items: '',
  effectiveness_score: 5,
  improvement_potential: 5
})

// 表单验证规则
const formRules = {
  what_happened: [
    { required: true, message: '请输入发生了什么', trigger: 'blur' }
  ],
  what_went_well: [
    { required: true, message: '请输入做得好的地方', trigger: 'blur' }
  ],
  what_not_went_well: [
    { required: true, message: '请输入需要改进的地方', trigger: 'blur' }
  ],
  lessons_learned: [
    { required: true, message: '请输入学到的经验', trigger: 'blur' }
  ],
  action_items: [
    { required: true, message: '请输入行动计划与方案', trigger: 'blur' }
  ],
  effectiveness_score: [
    { required: true, message: '请选择有效性评分', trigger: 'change' }
  ],
  improvement_potential: [
    { required: true, message: '请选择改进潜力评分', trigger: 'change' }
  ]
}

// 显示对话框
const showDialog = (review = null) => {
  dialogVisible.value = true
  isEdit.value = !!review
  
  if (review) {
    // 编辑模式
    Object.assign(formData, {
      what_happened: review.what_happened || '',
      what_went_well: review.what_went_well || '',
      what_not_went_well: review.what_not_went_well || '',
      lessons_learned: review.lessons_learned || '',
      action_items: review.action_items || '',
      effectiveness_score: review.effectiveness_score || 5,
      improvement_potential: review.improvement_potential || 5
    })
  } else {
    // 新建模式，重置表单
    resetForm()
  }
}

// 重置表单
const resetForm = () => {
  formData.what_happened = ''
  formData.what_went_well = ''
  formData.what_not_went_well = ''
  formData.lessons_learned = ''
  formData.action_items = ''
  formData.effectiveness_score = 5
  formData.improvement_potential = 5
}

// 提交表单
const handleSubmit = async () => {
  if (!reviewFormRef.value) return
  
  await reviewFormRef.value.validate((valid) => {
    if (!valid) {
      ElMessage.error('请填写完整的信息')
      return false
    }
    
    submitForm()
  })
}

// 实际提交操作
const submitForm = async () => {
  submitting.value = true
  
  try {
    // 获取当前用户ID - 从sessionStorage获取，因为登录时存储在sessionStorage中
    let userId = sessionStorage.getItem('userId')
    console.log('尝试从sessionStorage获取userId:', userId)
    
    // 如果sessionStorage中没有userId，尝试从currentUser对象中获取
    if (!userId) {
      const currentUserStr = sessionStorage.getItem('currentUser')
      console.log('尝试从sessionStorage.currentUser获取用户信息:', currentUserStr)
      if (currentUserStr) {
        try {
          const currentUser = JSON.parse(currentUserStr)
          userId = currentUser.id || currentUser.user_id
          console.log('从currentUser解析到的userId:', userId)
        } catch (e) {
          console.error('解析currentUser失败:', e)
        }
      }
    }
    
    // 如果还获取不到用户ID，尝试从localStorage获取作为备选方案
    if (!userId) {
      const localStorageUserId = localStorage.getItem('userId')
      const currentUserFromLocal = localStorage.getItem('currentUser')
      console.log('尝试从localStorage获取用户信息:', localStorageUserId, currentUserFromLocal)
      userId = localStorageUserId || (JSON.parse(currentUserFromLocal || '{}')).id
    }
    
    console.log('最终获取到的userId:', userId)
    
    // 验证用户ID是否可用
    if (!userId) {
      ElMessage.error('无法获取当前用户信息，请重新登录')
      console.error('获取用户ID失败，无法提交复盘')
      submitting.value = false
      return
    }
    
    // 准备提交参数
    const params = {
      repository_id: props.repositoryId,
      reviewer_id: userId, // 当前用户ID
      ...formData
    }
    
    console.log('准备提交的复盘数据:', params)
    
    console.log('调用API保存/更新复盘:', params)
    
    let result
    try {
      if (isEdit.value) {
        // 如果有reviewData，则使用其ID进行更新
        params.id = props.reviewData?.id
        console.log('调用更新API:', params)
        result = await updateReview(params)
      } else {
        console.log('调用保存API:', params)
        result = await saveReview(params)
      }
      
      console.log('API响应结果:', result)
      
      // 解析Axios响应，result.data包含了后端返回的实际JSON数据
      const responseJson = result.data
      
      // 从后端返回的JSON数据中提取字段
      let responseCode = responseJson.code
      let responseMsg = responseJson.msg
      let responseData = responseJson
      
      console.log('解析后的响应码:', responseCode, '消息:', responseMsg, '完整响应数据:', responseData)
    } catch (error) {
      console.error('API调用失败:', error)
      ElMessage.error('网络请求失败，请检查网络连接')
      submitting.value = false
      return
    }
    
    // 确保responseCode在错误处理块之外也可访问
    let responseCode, responseMsg, responseData
    try {
      // 解析Axios响应，result.data包含了后端返回的实际JSON数据
      const responseJson = result.data
      
      // 从后端返回的JSON数据中提取字段
      responseCode = responseJson.code
      responseMsg = responseJson.msg
      responseData = responseJson
      
      console.log('解析后的响应码:', responseCode, '消息:', responseMsg, '完整响应数据:', responseData)
    } catch (parseError) {
      console.error('解析响应数据失败:', parseError)
      responseCode = null
      responseMsg = '响应数据格式错误'
      responseData = null
    }
    
    if (responseCode === 200) {
      console.log('复盘操作成功:', responseMsg)
      ElMessage.success(responseMsg || (isEdit.value ? '复盘更新成功' : '复盘保存成功'))
      
      // 确保在成功后触发success事件，以便父组件刷新列表
      setTimeout(() => {
        emit('success')
      }, 300) // 稍微延迟一下，确保消息显示后再刷新列表
      
      handleClose()
    } else {
      console.error('复盘操作失败:', responseData)
      // 更详细的错误提示
      let errorMessage = responseMsg || responseData.msg || '操作失败'
      
      // 如果是常见的错误原因，提供更具体的提示
      if (errorMessage.includes('缺少复盘人ID')) {
        errorMessage = '无法获取当前用户信息，请重新登录后再试'
      } else if (errorMessage.includes('知识库条目不存在')) {
        errorMessage = '所选知识库条目不存在，请刷新页面后重试'
      } else if (errorMessage.includes('Token')) {
        errorMessage = '登录信息已过期，请重新登录'
      }
      
      ElMessage.error(errorMessage)
    }
  } catch (error) {
    console.error('提交复盘失败:', error)
    ElMessage.error('提交复盘失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  emit('close')
}

// 暴露方法给父组件
defineExpose({
  showDialog
})
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>