# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path
from event.views import SearchView,SaveView,ActionView,DeptListView,UserListView,ClassifyItemListView,EventView,GrantUser,EventListView,EventDetailView,AssignmentHistoryListView

urlpatterns = [
    # 示例：路径映射（根据你的实际视图调整）
    path('search', SearchView.as_view(), name='search'),  # 职级信息分页查询
    path('save', SaveView.as_view(), name='save'),  # 添加或者修改权限信息
    path('action', ActionView.as_view(), name='action'),  # 权限信息操作
    path('dept/list', DeptListView.as_view()),  # 部门列表接口
    path('user/list', UserListView.as_view()),  # 用户列表接口
    path('Classify/list', ClassifyItemListView.as_view()),  # 用户列表接口
    path('event/list', EventListView.as_view()),  # 事件列表接口
    path('menus', EventView.as_view(), name='menus'),  # 根据角色查询菜单权限
    path('grant', GrantUser.as_view(), name='grant'),  #角色权限授权
    path('detail', EventDetailView.as_view(), name='detail'),  # 事件详情
    path('assignment/history', AssignmentHistoryListView.as_view(), name='assignment_history'), # 分配记录
]