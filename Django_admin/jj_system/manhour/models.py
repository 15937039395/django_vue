# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers

class SysManhour(models.Model):
    id = models.AutoField(primary_key=True)
    dept_id = models.CharField(max_length=100, verbose_name="部门id", db_comment="部门id")  # 部门
    user_id = models.CharField(max_length=100, verbose_name="用户id", db_comment="用户id")  # 用户名
    date_time = models.DateField(verbose_name="时间", db_comment="时间")  # 时间
    report_type = models.CharField(max_length=100, verbose_name="类型", db_comment="类型")  # 时间
    project_number = models.CharField(max_length=100,  verbose_name="项目编号及名称", db_comment="项目编号及名称")  #
    job_description = models.TextField(verbose_name="工作描述", db_comment="工作描述")  # 标题
    man_hour = models.IntegerField(verbose_name="工时", db_comment="工时")  # 内容
    issue = models.CharField(max_length=100, verbose_name="存在的问题", db_comment="存在的问题")  # 时间
    coordinate = models.CharField(max_length=100, verbose_name="需协调的事项", db_comment="需协调的事项")  # 时间
    work_plan = models.CharField(max_length=500, verbose_name="次日工作计划", db_comment="次日工作计划")  # 时间
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    remark = models.CharField(max_length=500, null=True, verbose_name="备注", db_comment="备注")

    class Meta:
        db_table = "sys_manhour"


class SysManhourSerializer(serializers.ModelSerializer):
    """SysManhour模型序列化器"""
    # 格式化日期时间字段为本地时区（北京时间），不带UTC标识
    # date_time = serializers.DateField(format="%Y-%m-%d", required=False)  # 仅日期
    # 关键：使用format指定本地时间格式，去除Z标识
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = SysManhour
        fields = '__all__'