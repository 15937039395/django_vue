# Copyright (c) 2025 知识库管理系统. All rights reserved.

from rest_framework import serializers
from .models import FileManager
from user.models import SysUser


class FileSerializer(serializers.ModelSerializer):
    uploader_name = serializers.SerializerMethodField()
    size_display = serializers.ReadOnlyField()
    size = serializers.IntegerField(source='file_size', read_only=True)  # 为前端添加size字段别名
    
    class Meta:
        model = FileManager
        fields = [
            'id', 'filename', 'original_filename', 'file_path', 
            'file_size', 'size', 'file_type', 'uploader', 'uploader_name', 
            'upload_time', 'status', 'description', 'size_display'
        ]
        read_only_fields = ['upload_time', 'size_display', 'size']
    
    def get_uploader_name(self, obj):
        try:
            user = SysUser.objects.get(id=obj.uploader_id)
            return user.realname
        except SysUser.DoesNotExist:
            return "未知用户"


class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = FileManager
        fields = [
            'id', 'filename', 'original_filename', 'file_path', 
            'file_size', 'file_type', 'uploader', 'upload_time', 
            'status', 'description', 'file'
        ]
        read_only_fields = [
            'filename', 'file_path', 'file_size', 'file_type', 
            'upload_time', 'status'
        ]