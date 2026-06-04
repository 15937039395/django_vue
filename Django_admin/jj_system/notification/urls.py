# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path
from notification.views import (
    NotificationListView,
    UnreadCountView,
    MarkAsReadView,
    DeleteNotificationView,
)

urlpatterns = [
    path('list', NotificationListView.as_view(), name='notification_list'),
    path('unread-count', UnreadCountView.as_view(), name='unread_count'),
    path('mark-read', MarkAsReadView.as_view(), name='mark_read'),
    path('delete', DeleteNotificationView.as_view(), name='delete_notification'),
]
