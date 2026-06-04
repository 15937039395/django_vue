# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path

from user.views import TestView,JwtTestView,LoginView,SaveView,PwdView,ImageView,AvatarView,SearchView,\
    ActionView,CheckView,PasswordView,StatusView,GrantRole,DeptListView,PostListView,LevelListView,UserListView,TreeListView,CheckAdminUserView,ResetAdminPasswordView

urlpatterns = [

    path('login', LoginView.as_view(), name='login'),  # 登录
    path('save', SaveView.as_view(), name='save'),  #用户添加或者修改
    path('test', TestView.as_view(), name='test'),# 测试
    path('jwt_test', JwtTestView.as_view(), name='jwt_test'),  # jwt测试
    path('updateUserPwd', PwdView.as_view(), name='updateUserPwd'),  # 修改密码
    path('uploadImage', ImageView.as_view(), name='uploadImage'),  # 头像上传
    path('updateAvatar', AvatarView.as_view(), name='updateAvatar'),  # 更新头像
    path('search', SearchView.as_view(), name='search'),  # 用户信息分页查询
    path('action', ActionView.as_view(), name='action'),  # 用户信息操作
    path('check', CheckView.as_view(), name='check'),  # 用户名查重
    path('resetPassword', PasswordView.as_view(), name='resetPassword'),  # 重置密码
    path('status', StatusView.as_view(), name='status'),  # 状态修改
    path('grantRole', GrantRole.as_view(), name='grant'),  # 角色授权
    path('dept/list', DeptListView.as_view(), name='dept_list'),# 部门列表
    path('post/list', PostListView.as_view(), name='post_list'),# 岗位列表
    path('level/list', LevelListView.as_view(), name='level_list'),# 职级列表
    path('list', UserListView.as_view(), name='userList'),# 用户列表
    path('treeList', TreeListView.as_view(), name='treeList'),  # 查询权限菜单树信息
    path('check-admin', CheckAdminUserView.as_view(), name='check_admin'),  # 检查admin用户状态
    path('reset-admin-password', ResetAdminPasswordView.as_view(), name='reset_admin_password'),  # 重置admin用户密码

]
