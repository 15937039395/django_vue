<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="wangeditor-wrapper">
    <Toolbar
      :editor="editorRef"
      :defaultConfig="toolbarConfig"
      mode="default"
      style="border-bottom: 1px solid #ccc"
    />
    <Editor
      v-model="content"
      :defaultConfig="editorConfig"
      mode="default"
      @onCreated="handleCreated"
      style="height: 400px"
    />
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onUnmounted } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import requestUtil from '@/util/request'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  }
})

const emit = defineEmits(['update:modelValue'])

const content = ref(props.modelValue || '')
// 使用 shallowRef 存储编辑器实例
const editorRef = shallowRef(null)

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== content.value) {
    content.value = newVal || ''
  }
})

// 监听内容变化
watch(content, (newVal) => {
  emit('update:modelValue', newVal)
})

// 工具栏配置
const toolbarConfig = {
  excludeKeys: ['emotion', 'group-video', 'fullScreen']
}

// 编辑器配置
const editorConfig = {
  placeholder: props.placeholder,
  MENU_CONF: {
    uploadImage: {
      // 隐藏网络图片选项
      showLink: false,
      // 自定义上传
      customUpload: async (file, insertFn) => {
        // 验证文件类型
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if (!allowedTypes.includes(file.type)) {
          ElMessage.error('不支持的图片格式，请上传jpg、png、gif或webp格式的图片')
          return
        }

        // 验证文件大小 (5MB)
        const maxSize = 5 * 1024 * 1024
        if (file.size > maxSize) {
          ElMessage.error('图片大小不能超过5MB')
          return
        }

        // 创建FormData
        const formData = new FormData()
        formData.append('image', file)

        try {
          const res = await requestUtil.post('repository/upload/image', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })

          if (res.data.code === 200) {
            console.log('图片上传成功，URL:', res.data.url)
            insertFn(res.data.url, file.name, file.name)
            ElMessage.success('图片上传成功')
          } else {
            ElMessage.error(res.data.msg || '图片上传失败')
          }
        } catch (error) {
          console.error('图片上传错误:', error)
          ElMessage.error('图片上传失败，请稍后再试')
        }
      }
    }
  }
}

// 编辑器创建完成
const handleCreated = (editor) => {
  editorRef.value = editor
}

// 组件销毁时清理
onUnmounted(() => {
  if (editorRef.value) {
    editorRef.value.destroy()
    editorRef.value = null
  }
})
</script>

<style scoped>
.wangeditor-wrapper {
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden;
}

:deep(.w-e-text-container) {
  background-color: #fff;
}

/* 确保图片正确显示 */
:deep(.w-e-text-container img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 10px 0;
}
</style>
