# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers


class SysNotification(models.Model):
    """系统消息通知"""
    
    STATUS_UNREAD = 0
    STATUS_READ = 1
    
    STATUS_CHOICES = (
        (STATUS_UNREAD, '未读'),
        (STATUS_READ, '已读'),
    )
    
    TYPE_CHOICES = (
        ('event', '事件通知'),
        ('system', '系统通知'),
        ('approval', '审批通知'),
    )

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name="接收用户ID", db_comment="接收用户ID")
    title = models.CharField(max_length=255, verbose_name="消息标题", db_comment="消息标题")
    content = models.TextField(verbose_name="消息内容", db_comment="消息内容")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='system', verbose_name="消息类型", db_comment="消息类型")
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_UNREAD, verbose_name="消息状态", db_comment="消息状态：0-未读 1-已读")
    related_id = models.IntegerField(null=True, blank=True, verbose_name="关联ID", db_comment="关联的业务ID")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    read_time = models.DateTimeField(null=True, blank=True, verbose_name="阅读时间", db_comment="阅读时间")

    class Meta:
        db_table = 'sys_notification'
        ordering = ['-create_time']

    def __str__(self):
        return f"{self.title} - {self.user_id}"


class SysNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysNotification
        fields = '__all__'
