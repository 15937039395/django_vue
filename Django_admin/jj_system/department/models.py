# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers



# 部门模型
class SysDept(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="部门ID", db_comment="部门ID")
    # 部门名称
    name = models.CharField(null=False, max_length=150, verbose_name="部门名称", db_comment="部门名称")
    # 部门编码
    code = models.CharField(null=False, max_length=150, verbose_name="部门编码", db_comment="部门编码")
    # 部门类型：1-公司 2-子公司 3-部门 4-小组
    type = models.IntegerField(null=False, default=0, verbose_name="部门类型：1-公司 2-子公司 3-部门 4-小组",
                               help_text="部门类型：1-公司 2-子公司 3-部门 4-小组")
    #上级部门ID
    pid = models.IntegerField(default=0, verbose_name="上级部门ID", db_comment="上级部门ID")
    # 部门负责人
    leader = models.CharField(max_length=150, null=True, blank=True, verbose_name="部门负责人", db_comment="部门负责人")

    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    # 备注
    remark = models.CharField(max_length=500, verbose_name="备注", db_comment="备注")
    # 排序
    sort = models.IntegerField(default=0, verbose_name="排序", db_comment="排序")

    class Meta:
        """
           模型元数据配置
           定义模型在数据库中的表名和其他元数据信息
        """
        db_table = "sys_Dept"
        verbose_name = "部门表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '部门{}'.format(self.name)


class SysPostSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):

        if hasattr(obj, "children"):
            serializerPostList: list[SysPostSerializer2] = list()
            for sysPost in obj.children:
                serializerPostList.append(SysPostSerializer2(sysPost).data)
            return serializerPostList

    class Meta:
        model = SysDept
        fields = '__all__'


class SysPostSerializer2(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        if hasattr(obj, "children") and obj.children:
            return [SysPostSerializer2(child).data for child in obj.children]
        return []

    class Meta:
        model = SysDept
        fields = '__all__'