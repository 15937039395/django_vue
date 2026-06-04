# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers


class SysApproval(models.Model):
    """审批记录表"""
    
    # 审批类型
    TYPE_USER_DELETE = 1    # 删除用户
    TYPE_ROLE_DELETE = 2    # 删除角色
    TYPE_DATA_EXPORT = 3    # 数据导出
    
    TYPE_CHOICES = (
        (TYPE_USER_DELETE, '删除用户'),
        (TYPE_ROLE_DELETE, '删除角色'),
        (TYPE_DATA_EXPORT, '数据导出'),
    )
    
    # 审批状态
    STATUS_PENDING = 1      # 待审批
    STATUS_APPROVED = 2     # 已通过
    STATUS_REJECTED = 3     # 已拒绝
    STATUS_CANCELLED = 4    # 已撤销
    
    STATUS_CHOICES = (
        (STATUS_PENDING, '待审批'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_REJECTED, '已拒绝'),
        (STATUS_CANCELLED, '已撤销'),
    )
    
    id = models.AutoField(primary_key=True)
    approval_type = models.IntegerField(
        choices=TYPE_CHOICES,
        verbose_name="审批类型",
        db_comment="审批类型：1-删除用户 2-删除角色 3-数据导出"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="审批标题",
        db_comment="审批标题"
    )
    content = models.TextField(
        null=True,
        verbose_name="审批内容",
        db_comment="审批内容详情"
    )
    target_id = models.IntegerField(
        null=True,
        verbose_name="目标ID",
        db_comment="被操作对象的ID（如用户ID）"
    )
    target_data = models.TextField(
        null=True,
        verbose_name="目标数据",
        db_comment="被操作对象的数据快照（JSON格式）"
    )
    applicant_id = models.IntegerField(
        verbose_name="申请人ID",
        db_comment="提交审批的用户ID"
    )
    applicant_name = models.CharField(
        max_length=50,
        verbose_name="申请人姓名",
        db_comment="提交审批的用户姓名"
    )
    approver_id = models.IntegerField(
        null=True,
        verbose_name="审批人ID",
        db_comment="审批人的用户ID"
    )
    approver_name = models.CharField(
        max_length=50,
        null=True,
        verbose_name="审批人姓名",
        db_comment="审批人姓名"
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="审批状态",
        db_comment="审批状态：1-待审批 2-已通过 3-已拒绝 4-已撤销"
    )
    approve_remark = models.TextField(
        null=True,
        verbose_name="审批意见",
        db_comment="审批人的审批意见"
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="审批提交时间"
    )
    approve_time = models.DateTimeField(
        null=True,
        verbose_name="审批时间",
        db_comment="审批处理时间"
    )
    remark = models.CharField(
        max_length=500,
        null=True,
        verbose_name="备注",
        db_comment="备注"
    )
    
    class Meta:
        db_table = "sys_approval"
        verbose_name = "审批记录"
        verbose_name_plural = verbose_name


class SysApprovalSerializer(serializers.ModelSerializer):
    """审批记录序列化器"""
    
    # 添加显示字段
    approval_type_display = serializers.CharField(
        source='get_approval_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = SysApproval
        fields = '__all__'
