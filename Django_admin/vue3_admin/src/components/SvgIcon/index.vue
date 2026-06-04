<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿
<template>
  <svg
    class="svg-icon"
    aria-hidden="true"
    role="img"
  >
    <use :xlink:href="sanitizedIconName"></use>
  </svg>
</template>

<script setup>import { defineProps, computed } from 'vue'

const props = defineProps({
  icon: {
    type: String,
    required: false,  // 改为非必需
    default: '',      // 提供默认值
    validator: (value) => {
      // 允许空值，验证图标名称不包含危险字符
      return !value || !/[<>'"&]/.test(value)
    }
  }
})

const sanitizedIconName = computed(() => {
  // 处理空值情况
  if (!props.icon) {
    return '#icon-default'  // 返回默认图标
  }
  // 额外的安全处理，防止XSS攻击
  const cleanIcon = props.icon.replace(/[^a-zA-Z0-9-_]/g, '')
  return `#icon-${cleanIcon}`
})
</script>

<style lang="scss" scoped>.svg-icon {
  width: 1em;
  height: 1em;
  vertical-align: -0.15em;
  fill: currentColor;
  overflow: hidden;
}
</style>