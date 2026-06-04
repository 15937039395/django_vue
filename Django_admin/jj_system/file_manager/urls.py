# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('list/', views.list_files, name='list_files'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('detail/<int:file_id>/', views.file_detail, name='file_detail'),
]