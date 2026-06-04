# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path

from manhour.views import SearchView,SaveView,ActionView,DeptListView,UserListView,ItemListView

urlpatterns = [
    path('search', SearchView.as_view(), name='search'),  # 职级信息分页查询
    path('save', SaveView.as_view(), name='save'),  # 添加或者修改权限信息
    path('action', ActionView.as_view(), name='action'),  # 角色信息操作
    path('dept/list', DeptListView.as_view()),  # 部门列表接口
    path('user/list', UserListView.as_view()),  # 用户列表接口
    path('items/list', ItemListView.as_view()),  # 用户列表接口
]
