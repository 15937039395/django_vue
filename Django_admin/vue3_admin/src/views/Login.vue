<!-- Copyright (c) 2025 知识库管理系统. All rights reserved. -->

﻿<template>
  <div class="login">
    <div class="login-container">
      <!-- 品牌装饰元素 -->
      <div class="brand-decor brand-decor-1"></div>
      <div class="brand-decor brand-decor-2"></div>
      <div class="brand-decor brand-decor-3"></div>
      <div class="brand-decor brand-decor-4"></div>

      <el-form ref="loginRef" :model="loginForm" :rules="loginRules" class="login-form">
        <h3 class="title">知识库管理系统</h3>

        <el-form-item prop="username">

          <el-input
              v-model="loginForm.username"
              type="text"
              size="large"
              auto-complete="off"
              placeholder="账号"
          >
            <template #prefix><svg-icon icon="user" /></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
              v-model="loginForm.password"
              type="password"
              size="large"
              auto-complete="off"
              placeholder="密码"
          >
            <template #prefix><svg-icon icon="password" /></template>
          </el-input>
        </el-form-item>


        <el-checkbox v-model="loginForm.rememberMe" style="margin:0px 0px 25px 0px;">记住密码</el-checkbox>
        <el-form-item style="width:100%;">
          <el-button
              size="large"
              type="primary"
              style="width:100%;"
              @click.prevent="handleLogin"
          >
            <span>登 录</span>

          </el-button>

        </el-form-item>
      </el-form>
      <!--  底部  -->
<!--      <div class="el-login-footer">-->
<!--        <span>Copyright © 2013-2025 <a href="http://www.python222.com" target="_blank">python222.com</a> 版权所有.</span>-->
<!--      </div>-->
    </div>
  </div>
</template>

<script setup>
  import {ref} from 'vue'
  import requestUtil from '@/util/request'
  import qs from 'qs'
  import {ElMessage} from 'element-plus'
  import Cookies from "js-cookie";
  import { encrypt, decrypt } from "@/util/jsencrypt";
  import router from '@/router'


  const loginForm=ref({
    username:'',
    password:'',
    rememberMe:false
  })

  const loginRef=ref(null)

  const loginRules = {
    username: [{required: true, trigger: "blur", message: "请输入您的账号"}],
    password: [{required: true, trigger: "blur", message: "请输入您的密码"}]
  };

  const handleLogin=()=>{
    loginRef.value.validate(async (valid)=>{
      if(valid){
        let result=await requestUtil.post("user/login?"+qs.stringify(loginForm.value))
        let data=result.data
        if(data.code==200){
          ElMessage.success(data.info)
          window.sessionStorage.setItem("token",data.token)
          const currentUser=data.user
          currentUser.roles=data.roles
          window.sessionStorage.setItem("currentUser",JSON.stringify(currentUser))
          window.sessionStorage.setItem("menuList",JSON.stringify(data.menuList))
          // 保存用户权限列表
          window.sessionStorage.setItem("permissions",JSON.stringify(data.permissions || []))
          // 勾选了需要记住密码设置在 cookie 中设置记住用户名和密码
          if (loginForm.value.rememberMe) {
            Cookies.set("username", loginForm.value.username, { expires: 30 });
            Cookies.set("password", encrypt(loginForm.value.password), { expires: 30 });
            Cookies.set("rememberMe", loginForm.value.rememberMe, { expires: 30 });
          } else {
            // 否则移除
            Cookies.remove("username");
            Cookies.remove("password");
            Cookies.remove("rememberMe");
          }
          router.replace("/")
        }else{
          ElMessage.error(data.info)
        }
      }else{
        console.log("验证失败")
      }
    })
  }

  function getCookie() {
    const username = Cookies.get("username");
    const password = Cookies.get("password");
    const rememberMe = Cookies.get("rememberMe");
    loginForm.value = {
      username: username === undefined ? loginForm.value.username : username,
      password: password === undefined ? loginForm.value.password : decrypt(password),
      rememberMe: rememberMe === undefined ? false : Boolean(rememberMe)
    };
  }

  getCookie();


</script>

<style lang="scss" scoped>
a{
  color: var(--brand-blue);
}
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-green) 30%, var(--brand-gold) 70%, var(--brand-red) 100%);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
  position: relative;
  overflow: hidden;
}

.login-container {
  position: relative;
  z-index: 10;
}

@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.title {
  margin: 0px auto 30px auto;
  text-align: center;
  color: var(--brand-blue);
  font-size: 24px;
  font-weight: 600;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.login-form {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  width: 400px;
  padding: 35px 30px 25px 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);

  .el-input {
    height: 46px;
    margin-bottom: 20px;

    .el-input__wrapper {
      border-radius: 8px;
      border: 1px solid #e4e7ed;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) inset;
      
      &:hover {
        box-shadow: 0 0 0 1px var(--brand-blue) inset;
      }
      
      &:focus {
        box-shadow: 0 0 0 1px var(--brand-blue) inset;
      }
    }

    input {
      display: inline-block;
      height: 46px;
      padding: 0 15px;
      font-size: 16px;
    }
  }
  .input-icon {
    height: 45px;
    width: 16px;
    margin-left: 5px;
  }

}

.el-form-item {
  margin-bottom: 24px;
}

.el-checkbox {
  margin: 5px 0 25px 0;
  
  :deep(.el-checkbox__input.is-checked+.el-checkbox__label) {
    color: var(--brand-blue);
  }
  
  :deep(.el-checkbox__inner:hover) {
    border-color: var(--brand-blue);
  }
  
  :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: var(--brand-blue);
    border-color: var(--brand-blue);
  }
}

.el-button--primary {
  background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-gold) 100%);
  border-color: var(--brand-blue);
  border-radius: 8px;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  
  &:hover {
    background: linear-gradient(135deg, var(--brand-blue-dark) 0%, var(--brand-gold-dark) 100%);
    border-color: var(--brand-blue-dark);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(24, 144, 255, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.login-tip {
  font-size: 13px;
  text-align: center;
  color: #999;
}

.login-code {
  width: 33%;
  height: 40px;
  float: right;
  img {
    cursor: pointer;
    vertical-align: middle;
  }
}

:deep(.el-login-footer) {
  height: 40px !important;
  position: fixed !important;
  bottom: 0 !important;
  left: 0 !important;
  width: 100% !important;
  color: rgba(255, 255, 255, 0.8) !important;
  font-family: Arial !important;
  font-size: 12px !important;
  letter-spacing: 1px !important;
  background: rgba(0, 0, 0, 0.2) !important;
  backdrop-filter: blur(5px) !important;
  z-index: 1000 !important;
  
  /* 使用 Flexbox 确保内容居中 */
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  text-align: center !important;
  
  a {
    color: var(--brand-gold) !important;
    text-decoration: none !important;
    
    &:hover {
      color: var(--brand-gold-light) !important;
      text-decoration: underline !important;
    }
  }
  
  span {
    text-align: center !important;
    width: 100% !important;
    display: block !important;
  }
}

.login-code-img {
  height: 40px;
  padding-left: 12px;
}

/* 添加品牌色彩元素 */
.login-form::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, var(--brand-green), var(--brand-blue), var(--brand-red), var(--brand-gold), var(--brand-green));
  z-index: -1;
  border-radius: 14px;
  background-size: 400%;
  animation: glowing-border 20s linear infinite;
  opacity: 0.5;
}

@keyframes glowing-border {
  0% {
    background-position: 0 0;
  }
  50% {
    background-position: 400% 0;
  }
  100% {
    background-position: 0 0;
  }
}

/* SVG 图标颜色 */
:deep(.svg-icon) {
  color: var(--brand-blue);
  width: 1.2em;
  height: 1.2em;
  margin-right: 8px;
}

/* 品牌装饰元素 */
.brand-decor {
  position: absolute;
  border-radius: 50%;
  z-index: 0;
  opacity: 0.1;
  filter: blur(20px);
}

.brand-decor-1 {
  width: 200px;
  height: 200px;
  background: var(--brand-green);
  top: 10%;
  left: 10%;
  animation: float 8s ease-in-out infinite;
}

.brand-decor-2 {
  width: 150px;
  height: 150px;
  background: var(--brand-blue);
  top: 60%;
  right: 15%;
  animation: float 10s ease-in-out infinite;
  animation-delay: 1s;
}

.brand-decor-3 {
  width: 120px;
  height: 120px;
  background: var(--brand-red);
  bottom: 20%;
  left: 20%;
  animation: float 12s ease-in-out infinite;
  animation-delay: 2s;
}

.brand-decor-4 {
  width: 180px;
  height: 180px;
  background: var(--brand-gold);
  top: 30%;
  right: 25%;
  animation: float 9s ease-in-out infinite;
  animation-delay: 0.5s;
}

@keyframes float {
  0% {
    transform: translate(0, 0) rotate(0deg);
  }
  50% {
    transform: translate(-20px, 20px) rotate(10deg);
  }
  100% {
    transform: translate(0, 0) rotate(0deg);
  }
}
</style>
