# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path
from approval import views

urlpatterns = [
    path('list', views.ApprovalListView.as_view(), name='approval_list'),
    path('submit', views.ApprovalSubmitView.as_view(), name='approval_submit'),
    path('process', views.ApprovalProcessView.as_view(), name='approval_process'),
    path('cancel', views.ApprovalCancelView.as_view(), name='approval_cancel'),
]
