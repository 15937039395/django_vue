# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models

from rest_framework import serializers


class SysPost(models.Model):
    """
    岗位模型类
    """
    id = models.AutoField(primary_key=True, verbose_name="岗位ID",db_comment="岗位ID")
    # 岗位名称
    name = models.CharField(max_length=150, verbose_name="岗位名称", db_comment="岗位名称")
    # 排序
    sort = models.IntegerField(default=0, verbose_name="岗位顺序", db_comment="岗位顺序")
    # 状态选项
    STATUS_CHOICES = (
        (1, "正常"),
        (2, "停用"),
    )
    # 状态
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="岗位状态：1-正常 2-停用",
                                 db_comment="岗位状态：1-正常 2-停用")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")

    class Meta:
        """
           模型元数据配置
           定义模型在数据库中的表名和其他元数据信息
        """
        db_table = "sys_post"
        verbose_name = "岗位表"
        verbose_name_plural = verbose_name

class SysPostSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):

        if hasattr(obj, "children"):
            serializerPostList: list[SysPostSerializer2] = list()
            for sysPost in obj.children:
                serializerPostList.append(SysPostSerializer2(sysPost).data)
            return serializerPostList

    class Meta:
        model = SysPost
        fields = '__all__'

class SysPostSerializer2(serializers.ModelSerializer):
    class Meta:
        model = SysPost
        fields = '__all__'
