# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'
    verbose_name = '消息通知'
