// Copyright (c) 2025 知识库管理系统. All rights reserved.

import { createStore } from 'vuex'

export default createStore({
  state: {
    editableTabsValue:'/index',
    editableTabs:[
      {
        title:'首页',
        name:'/index'
      }
    ],
    isCollapse: false  // 菜单折叠状态
  },
  getters: {
  },
  mutations: {
    ADD_TABS:(state,tab)=>{
      if(state.editableTabs.findIndex(e=>e.name===tab.path)===-1){
        state.editableTabs.push({
          title:tab.name,
          name:tab.path
        })
      }
      state.editableTabsValue=tab.path
    },
    RESET_TAB:(state)=>{
      state.editableTabsValue='/index'
      state.editableTabs=[
        {
          title:'首页',
          name:'/index'
        }
      ]
    },
    TOGGLE_COLLAPSE:(state)=>{
      state.isCollapse = !state.isCollapse
    }
  },
  actions: {
  },
  modules: {
  }
})
