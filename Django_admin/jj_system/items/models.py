# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models

from rest_framework import serializers

class SysItem(models.Model):
    id = models.AutoField(primary_key=True)
    project_number = models.CharField(max_length=100,  verbose_name="项目编号及名称", db_comment="项目编号及名称")  # 分类
    user_id = models.IntegerField(default=0, verbose_name="用户ID", db_comment="用户ID")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")

    class Meta:
        db_table = "sys_item"


class SysPostSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):

        if hasattr(obj, "children"):
            serializerPostList: list[SysPostSerializer2] = list()
            for sysPost in obj.children:
                serializerPostList.append(SysPostSerializer2(sysPost).data)
            return serializerPostList

    class Meta:
        model = SysItem
        fields = '__all__'

class SysPostSerializer2(serializers.ModelSerializer):
    class Meta:
        model = SysItem
        fields = '__all__'