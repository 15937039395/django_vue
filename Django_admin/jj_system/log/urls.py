# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path

from log.views import OperLogView

urlpatterns = [
    path('log/', OperLogView.as_view(), name='log_search'),
]
