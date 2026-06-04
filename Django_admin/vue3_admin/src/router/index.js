// Copyright (c) 2025 知识库管理系统. All rights reserved.

import {createRouter, createWebHashHistory } from 'vue-router'
import { touch } from '@/util/auth' // 引入认证管理器的touch方法


const routes = [

  {
    path: '/',
    name: '主页',
    component: () => import('../layout/index'),
    redirect:'/sys/user',
    children: [
      {
        path: '/sys/user',
        name: '用户管理',
        component: () => import('../views/sys/user/index.vue')
      },
      {
        path: '/sys/role',
        name: '角色管理',
        component: () => import('../views/sys/role/index.vue')
      },
      {
        path: '/sys/menu',
        name: '菜单管理',
        component: () => import('../views/sys/menu/index.vue')
      },
      {
        path: '/sys/dept',
        name: '部门管理',
        component: () => import('../views/sys/dept/index')
      },
      {
        path: '/sys/post',
        name: '岗位管理',
        component: () => import('../views/sys/post/index')
      },
      {
        path: '/sys/notification',
        name: '消息通知',
        component: () => import('../views/sys/notification/index.vue'),
        meta: { title: '消息通知' }
      },
      {
        path: '/sys/level',
        name: '职级管理',
        component: () => import('../views/sys/level/index.vue')
      },
      {
        path: '/log',
        name: '日志管理',
        component: () => import('../views/sys/log/index.vue')
      },
      {
        path: '/bsns/blacklist',
        name: '逾期管理',
        component: () => import('../views/bsns/blacklist/index.vue')
      },
      {
        path: '/bsns/manhour',
        name: '工时填报',
        component: () => import('../views/bsns/manhour/index.vue')
      },
      {
        path: '/bsns/repository',
        name: '知识库管理',
        component: () => import('../views/bsns/repository/index.vue')
      },
      {
        path: '/bsns/repository/add',
        name: 'RepositoryAdd',
        component: () => import('../views/bsns/repository/add.vue'),
        meta: { title: '新增知识库' }
      },
      {
        path: '/bsns/repository/edit/:id',
        name: 'RepositoryEdit',
        component: () => import('../views/bsns/repository/edit.vue'),
        meta: { title: '编辑知识库' }
      },
      {
        path: '/bsns/repository/detail/:id',
        name: 'RepositoryDetail',
        component: () => import('../views/bsns/repository/detail.vue'),
        meta: { title: '知识库详情' }
      },
      {
        path: '/bsns/items',
        name: '项目管理',
        component: () => import('../views/bsns/items/index.vue')
      },
        {
        path: '/bsns/classify',
        name: '分类管理',
        component: () => import('../views/bsns/classify/index.vue')
      },
        {
        path: '/bsns/event',
        name: '事件管理',
        component: () => import('../views/bsns/event/index.vue')
      },
      {
        path: '/bsns/files',
        name: '文件管理',
        component: () => import('../views/bsns/files/index.vue')
      },
      {
        path: '/sys/approval',
        name: '审批管理',
        component: () => import('../views/sys/approval/index.vue')
      },
      {
        path: '/bsns/event/add',
        name: 'EventAdd',
        component: () => import('../views/bsns/event/add.vue'),
        meta: { title: '新增事件' }
      },
      {
        path: '/bsns/event/edit/:id',
        name: 'EventEdit',
        component: () => import('../views/bsns/event/edit.vue'),
        meta: { title: '编辑事件' }
      },
      {
        path: '/bsns/event/assignment-history',
        name: 'EventAssignmentHistory',
        component: () => import('../views/bsns/event/AssignmentHistory.vue'),
        meta: { title: '分配记录' }
      },
      {
        path: '/userCenter',
        name: '个人中心',
        component: () => import('../views/userCenter/index.vue')
      },

    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫，更新用户活动时间
router.beforeEach((to, from, next) => {
  // 更新最后活动时间
  touch();
  next();
});

export default router
