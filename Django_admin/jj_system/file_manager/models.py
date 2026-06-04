# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from user.models import SysUser  # 引用用户表
import os


def upload_to(instance, filename):
    """定义文件上传路径"""
    # 可以根据用户ID创建子目录
    user_id = getattr(instance, 'uploader_id', 'unknown')
    return f'uploads/user_{user_id}/{filename}'


class FileManager(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=255, verbose_name="文件名")
    original_filename = models.CharField(max_length=255, verbose_name="原始文件名")
    file_path = models.CharField(max_length=500, verbose_name="文件路径")
    file_size = models.BigIntegerField(verbose_name="文件大小")
    file_type = models.CharField(max_length=100, verbose_name="文件类型")
    uploader = models.ForeignKey(SysUser, on_delete=models.CASCADE, verbose_name="上传者")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    status = models.CharField(max_length=20, default="已上传", choices=[
        ("已上传", "已上传"),
        ("处理中", "处理中"),
        ("已删除", "已删除")
    ], verbose_name="状态")
    description = models.TextField(null=True, blank=True, verbose_name="描述")
    
    class Meta:
        db_table = "sys_file_manager"
        ordering = ['-upload_time']
        verbose_name = "文件管理"
        verbose_name_plural = "文件管理"

    def __str__(self):
        return self.filename
    
    @property
    def size_display(self):
        """返回友好的文件大小显示"""
        if self.file_size == 0:
            return "0 B"
        
        size_units = ['B', 'KB', 'MB', 'GB']
        size = self.file_size
        unit_index = 0
        
        while size >= 1024 and unit_index < len(size_units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{size:.2f} {size_units[unit_index]}"