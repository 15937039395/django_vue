# Copyright (c) 2025 知识库管理系统. All rights reserved.

"""
URL configuration for jj_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include,re_path
from django.views.static import serve
from jj_system import settings




urlpatterns = [

    path('user/', include('user.urls')),  # 用户模块
    path('role/', include('role.urls')),  # 角色模块
    path('menu/', include('menu.urls')),  # 权限模块
    path('level/', include('level.urls')),#职级模块
    path('post/', include('post.urls')),#岗位模块
    path('department/', include('department.urls')),#部门模块
    path('manhour/', include('manhour.urls')),  # 工时模块
    path('blacklist/', include('blacklist.urls')),  # 逾期名单模块
    path('repository/', include('repository.urls')),  # 知识库模块
    path('items/', include('items.urls')),  # 工时统计模块
    path('classify/', include('classify.urls')),  # 分类模块
    path('event/', include('event.urls')),  # 事件管理模块
    path('files/', include('file_manager.urls')),  # 文件管理模块
    path('approval/', include('approval.urls')),  # 审批流程模块
    path('log/', include('log.urls')),  # 日志模块
    path('notification/', include('notification.urls')),  # 消息通知模块
    # 配置媒体文件的路由地址
    re_path('media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}, name='media')
]
