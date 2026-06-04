# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers

from role.models import SysRole


class SysMenu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name="菜单名称", db_comment="菜单名称")
    icon = models.CharField(max_length=100, null=True, verbose_name="菜单图标", db_comment="菜单图标")
    parent_id = models.IntegerField(null=True, verbose_name="父菜单ID", db_comment="父菜单ID")
    order_num = models.IntegerField(null=True, verbose_name="显示顺序", db_comment="显示顺序")
    path = models.CharField(max_length=200, null=True, verbose_name="路由地址", db_comment="路由地址")
    component = models.CharField(max_length=255, null=True, verbose_name="组件路径", db_comment="组件路径")
    menu_type = models.CharField(max_length=1, null=True, verbose_name="菜单类型（M目录 C菜单 F按钮）", db_comment="菜单类型（M目录 C菜单 F按钮）")
    perms = models.CharField(max_length=100, null=True, verbose_name="权限标识", db_comment="权限标识")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    remark = models.CharField(max_length=500, null=True, verbose_name="备注",db_comment="备注")

    def __lt__(self, other):
        # Handle case where order_num might be None
        self_order = self.order_num if self.order_num is not None else 9999
        other_order = other.order_num if other.order_num is not None else 9999
        return self_order < other_order

    class Meta:
        db_table = "sys_menu"


class SysMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):

        if hasattr(obj, "children"):
            serializerMenuList: list[SysMenuSerializer2] = list()
            for sysMenu in obj.children:
                serializerMenuList.append(SysMenuSerializer2(sysMenu).data)
            return serializerMenuList

    class Meta:
        model = SysMenu
        fields = '__all__'


class SysMenuSerializer2(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    def get_children(self, obj):
        if hasattr(obj, "children"):
            serializerMenuList: list[SysMenuSerializer2] = list()
            for sysMenu in obj.children:
                serializerMenuList.append(SysMenuSerializer2(sysMenu).data)
            return serializerMenuList

    class Meta:
        model = SysMenu
        fields = '__all__'


# 系统角色菜单关联类
class SysRoleMenu(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.PROTECT)
    menu = models.ForeignKey(SysMenu, on_delete=models.PROTECT)

    class Meta:
        db_table = "sys_role_menu"


class SysRoleMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysRoleMenu
        fields = '__all__'

