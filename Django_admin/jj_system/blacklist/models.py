# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers
from django.utils import timezone

class SysBlackList(models.Model):
    id = models.AutoField(primary_key=True)
    #用户名单
    name = models.CharField(max_length=100,  verbose_name="企业名称", db_comment="企业名称")
    # 用户名单
    contract_time = models.DateField( null=True,blank=True,verbose_name="合同履约日期", db_comment="合同履约日期")
    deadline_time = models.DateField( null=True,blank=True,verbose_name="逾期日期", db_comment="逾期日期")
    #类型
    types = models.CharField(null=True,blank=True,max_length=100, verbose_name="类型", db_comment="类型")
    #状态
    status = models.IntegerField(null=True,blank=True,verbose_name="状态", db_comment="状态")
    #金额
    amount_type = models.IntegerField(null=True,blank=True,verbose_name="金额类型 1、合同金额 2、订单金额", db_comment="金额类型 1、合同金额 2、订单金额")
    # 金额
    amount = models.IntegerField(null=True,blank=True,verbose_name="金额", db_comment="金额")
    #备案信息
    archival_information = models.CharField(null=True,blank=True,max_length=100,verbose_name="备案信息 0、未备案 1、已备案", db_comment="备案信息 0、未备案 1、已备案")
    #实际日期
    actual_time = models.DateField(null=True,blank=True, verbose_name="实际日期", db_comment="实际日期")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    remark = models.CharField(max_length=500, null=True,blank=True, verbose_name="备注", db_comment="分类")

    class Meta:
        db_table = "sys_BlackList"
        verbose_name = "各种名单表"
        verbose_name_plural = verbose_name

class SysBlacklistSerializer(serializers.ModelSerializer):
    # 自定义时间字段序列化（转换为北京时间）
    create_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        default_timezone=timezone.get_fixed_timezone(8)  # 东八区
    )
    update_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        default_timezone=timezone.get_fixed_timezone(8)
    )

    class Meta:
        model = SysBlackList
        fields = '__all__'
