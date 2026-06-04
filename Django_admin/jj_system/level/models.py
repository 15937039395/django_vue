# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers
# Create your models here.

# 职级模型
class SysLevel(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="职级ID", db_comment="职级ID")
    # 职级名称
    name = models.CharField(max_length=150, verbose_name="职级名称", db_comment="职级名称")
    # 排序
    sort = models.IntegerField(default=0, verbose_name="职级顺序", db_comment="职级顺序")
    # 状态选项
    STATUS_CHOICES = (
        (1, "正常"),
        (2, "停用"),
    )
    # 状态
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="职级状态：1-正常 2-停用",
                                 db_comment="职级状态：1-正常 2-停用")

    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间", db_comment="更新时间")

    class Meta:
        """
           模型元数据配置
           定义模型在数据库中的表名和其他元数据信息
        """
        db_table = "sys_level"
        verbose_name = "职级表"
        verbose_name_plural = verbose_name



class SysLevelSerializer(serializers.ModelSerializer):
    """
        系统用户序列化器类

        用于将SysUser模型实例序列化为JSON格式数据，或将JSON数据反序列化为SysUser模型实例。
        继承自ModelSerializer，自动处理模型字段的序列化和验证。

        Attributes:
            Meta: 配置序列化器的元数据信息

        Note:
            该序列化器会自动包含SysUser模型的所有字段
        """
    # 格式化日期字段
    birthday = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    login_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = SysLevel
        #exclude = ['password']  # 显式排除敏感字段 password
        fields = '__all__'
