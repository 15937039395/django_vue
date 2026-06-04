# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models

# Create your models here.

from django.db import models
from rest_framework import serializers
from user.models import SysUser
# Create your models here.


#系统角色类
class SysEvent(models.Model):
    id = models.AutoField(primary_key=True)
    dept_id = models.CharField(max_length=100, verbose_name="部门id", db_comment="部门id")  # 部门
    user_id = models.CharField(max_length=100, verbose_name="用户id", db_comment="用户id")  # 用户名
    event_number = models.CharField(max_length=250, null=True,verbose_name="事件编号",db_comment="事件编号")
    event_name = models.CharField(max_length=250, null=True, verbose_name="事件名称", db_comment="事件名称")
    principal = models.CharField(max_length=250, null=True, verbose_name="负责人", db_comment="负责人")
    # 事件状态
    STATUS_CHOICES = (
        (1, '正常'),
        (2, '停用')
    )
    status = models.IntegerField(null=False, choices=STATUS_CHOICES, default=1, verbose_name="事件状态：1-正常 2-停用",db_comment="事件状态：1-正常 2-停用")

    # 项目起始时间
    start_date = models.DateField(null=True, blank=True, verbose_name="项目起始时间", db_comment="项目起始时间")
    # 项目终止时间
    end_date = models.DateField(null=True, blank=True, verbose_name="项目终止时间", db_comment="项目终止时间")
    # 配置通知时间（用于监控消息通知的时间，精确到秒）
    notification_time = models.DateTimeField(null=True, blank=True, verbose_name="配置通知时间", db_comment="配置通知时间，格式：YYYY-MM-DD HH:MM:SS，用于监控什么时间段去发送消息通知")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    # 备注
    remark = models.CharField(null=True, max_length=255, verbose_name="备注", db_comment="备注")

    class Meta:
        db_table = 'sys_event'


class SysEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysEvent
        fields = '__all__'


# 系统事件角色关联类
class SysEventRole(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(SysEvent, on_delete=models.PROTECT)
    user = models.ForeignKey(SysUser, on_delete=models.PROTECT)

    class Meta:
        db_table = "sys_event_role"


class SysEventRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysEventRole
        fields = '__all__'


# 事件人员分配操作记录类
class SysEventAssignmentHistory(models.Model):
    ACTION_ADD = 1
    ACTION_REMOVE = 2
    
    ACTION_CHOICES = (
        (ACTION_ADD, '分配'),
        (ACTION_REMOVE, '取消分配')
    )

    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(SysEvent, on_delete=models.CASCADE, verbose_name="关联事件")
    user = models.ForeignKey(SysUser, on_delete=models.CASCADE, verbose_name="关联用户", related_name="assignment_user")
    operator = models.ForeignKey(SysUser, on_delete=models.SET_NULL, null=True, verbose_name="操作人", related_name="assignment_operator")
    action = models.IntegerField(choices=ACTION_CHOICES, verbose_name="操作类型")
    operate_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    remark = models.CharField(max_length=500, null=True, blank=True, verbose_name="备注")

    class Meta:
        db_table = "sys_event_assignment_history"
        ordering = ['-operate_time']

class SysEventAssignmentHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.realname', read_only=True)
    operator_name = serializers.CharField(source='operator.realname', read_only=True)
    event_name = serializers.CharField(source='event.event_name', read_only=True)
    event_number = serializers.CharField(source='event.event_number', read_only=True)
    action_text = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = SysEventAssignmentHistory
        fields = '__all__'
