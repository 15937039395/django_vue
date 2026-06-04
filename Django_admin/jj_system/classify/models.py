# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers
from django.views import View
from django.http import JsonResponse


# 优化模型：显式指定 editable=False 强化约束，规范表名（全小写）
class ClassifyItem(models.Model):
    id = models.AutoField(primary_key=True)
    dept_id = models.IntegerField(default=0, verbose_name="部门id", db_comment="部门id")  # 部门
    user_id = models.IntegerField(default=0, verbose_name="用户名id", db_comment="用户名id")  # 用户名
    types = models.IntegerField(default=0, verbose_name="分类id ：0-未分类，1-分类", db_comment="分类id ：0-类型，1-分类")
    project_number = models.CharField(max_length=100, verbose_name="分类名称", db_comment="分类名称")  # 分类
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")

    class Meta:
        db_table = "sys_Classify_item"



class SysPostSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ClassifyItem
        fields = ['id', 'dept_id', 'user_id', 'types', 'project_number', 'update_time']

class SysPostSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):

        if hasattr(obj, "children"):
            serializerPostList: list[SysPostSerializer2] = list()
            for sysPost in obj.children:
                serializerPostList.append(SysPostSerializer2(sysPost).data)
            return serializerPostList

    class Meta:
        model = ClassifyItem
        fields = ['id', 'dept_id', 'user_id', 'types', 'project_number', 'create_time', 'update_time', 'children']





