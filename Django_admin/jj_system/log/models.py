# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from user.models import SysUser


# Create your models here.


class SysOperLog(models.Model):
    """系统操作日志"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(SysUser, on_delete=models.SET_NULL, null=True, verbose_name="操作用户", db_comment="操作用户")
    operation = models.CharField(max_length=200, verbose_name="操作内容", db_comment="操作内容")
    method = models.CharField(max_length=10, verbose_name="请求方法", db_comment="请求方法")
    path = models.CharField(max_length=255, verbose_name="请求路径", db_comment="请求路径")
    ip = models.CharField(max_length=50, verbose_name="客户端IP", db_comment="客户端IP")
    params = models.TextField(null=True, verbose_name="请求参数", db_comment="请求参数")
    status = models.IntegerField(default=0, verbose_name="操作状态(0成功1失败)", db_comment="操作状态(0成功1失败)")
    error_msg = models.TextField(null=True, verbose_name="错误信息", db_comment="错误信息")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")

    class Meta:
        db_table = "sys_oper_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
