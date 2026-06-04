# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers
from user.models import SysUser
# Create your models here.


#系统角色类
class SysRole(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=True,verbose_name="角色名称",db_comment="角色名称")
    code = models.CharField(max_length=100, null=True,verbose_name="角色权限字符串",db_comment="角色权限字符串")
    # 角色状态
    STATUS_CHOICES = (
        (1, '正常'),
        (2, '停用')
    )
    status = models.IntegerField(null=False, choices=STATUS_CHOICES, default=1, verbose_name="角色状态：1-正常 2-停用",db_comment="角色状态：1-正常 2-停用")
    # 角色排序
    sort = models.IntegerField(null=False, default=0, verbose_name="角色排序", db_comment="角色排序")
    
    # 数据权限范围
    DATA_SCOPE_ALL = 1           # 全部数据
    DATA_SCOPE_DEPT_AND_SUB = 2  # 本部门及下级部门
    DATA_SCOPE_DEPT = 3          # 仅本部门
    DATA_SCOPE_SELF = 4          # 仅本人
    
    DATA_SCOPE_CHOICES = (
        (DATA_SCOPE_ALL, '全部数据'),
        (DATA_SCOPE_DEPT_AND_SUB, '本部门及下级部门'),
        (DATA_SCOPE_DEPT, '仅本部门'),
        (DATA_SCOPE_SELF, '仅本人'),
    )
    data_scope = models.IntegerField(
        null=False, 
        choices=DATA_SCOPE_CHOICES, 
        default=DATA_SCOPE_SELF, 
        verbose_name="数据权限范围",
        db_comment="数据权限范围：1-全部数据 2-本部门及下级部门 3-仅本部门 4-仅本人"
    )

    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    # 备注
    remark = models.CharField(null=True, max_length=255, verbose_name="备注", db_comment="备注")

    class Meta:
        db_table = 'sys_role'


class SysRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysRole
        fields = '__all__'


# 系统用户角色关联类
class SysUserRole(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.PROTECT)
    user = models.ForeignKey(SysUser, on_delete=models.PROTECT)

    class Meta:
        db_table = "sys_user_role"


class SysUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUserRole
        fields = '__amll__'
