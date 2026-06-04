# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path

from blacklist.views import SearchView,SaveView,ActionView

urlpatterns = [
    path('search', SearchView.as_view(), name='search'),  # 企业信息分页查询
    path('save', SaveView.as_view(), name='save'),  # 添加或者修改信息
    path('action', ActionView.as_view(), name='action'),  # 信息操作

]
