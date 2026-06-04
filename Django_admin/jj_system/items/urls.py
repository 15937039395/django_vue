# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path
from items.views import SearchView,SaveView,ActionView

urlpatterns = [
    # 示例：路径映射（根据你的实际视图调整）
    path('search', SearchView.as_view(), name='search'),  # 职级信息分页查询
    path('save', SaveView.as_view(), name='save'),  # 添加或者修改权限信息
    path('action', ActionView.as_view(), name='action'),  # 权限信息操作

]