# Copyright (c) 2025 知识库管理系统. All rights reserved.

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
from .models import FileManager
from .serializers import FileSerializer, FileUploadSerializer
from .permissions import IsAuthenticatedCustom
from user.models import SysUser
from common.data_permission import DataPermissionUtil
import uuid


@api_view(['POST'])
@permission_classes([IsAuthenticatedCustom])
def upload_file(request):
    """
    文件上传接口
    """
    if 'file' not in request.FILES:
        return Response({'code': 400, 'msg': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    user_id = request.data.get('user_id', None)
    
    # 获取用户信息
    try:
        user = SysUser.objects.get(id=user_id) if user_id else request.user
        
        # 检查用户状态（1-正常，2-禁用）
        if user.status == 2:
            return Response({'code': 403, 'msg': '您的账号已被禁用，无法上传文件'}, status=status.HTTP_403_FORBIDDEN)
    except SysUser.DoesNotExist:
        return Response({'code': 400, 'msg': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 生成唯一文件名
    ext = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # 创建上传目录
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'user_{user.id}')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    # 保存文件信息到数据库
    file_record = FileManager.objects.create(
        filename=unique_filename,
        original_filename=uploaded_file.name,
        file_path=file_path,
        file_size=uploaded_file.size,
        file_type=uploaded_file.content_type or '',
        uploader=user,
        status="已上传"
    )
    
    serializer = FileSerializer(file_record)
    return Response({'code': 200, 'msg': '上传成功', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def list_files(request):
    """
    获取文件列表接口 - 所有用户都可以查看所有文件
    """
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # 获取所有文件
    files = FileManager.objects.all().order_by('-upload_time')
    
    # 为每个文件添加上传者的部门信息（用于前端显示）
    files_with_dept = []
    for file in files:
        try:
            uploader = SysUser.objects.get(id=file.uploader_id)
            file.dept_id = uploader.dept_id
            file.uploader_name = uploader.realname or uploader.username
            files_with_dept.append(file)
        except SysUser.DoesNotExist:
            # 如果上传者不存在，也保留文件记录
            file.dept_id = None
            file.uploader_name = '未知用户'
            files_with_dept.append(file)
    
    # 不再应用数据权限过滤，所有登录用户都能查看所有文件
    filtered_files = files_with_dept
    
    # 分页
    paginator = Paginator(filtered_files, page_size)
    current_page = paginator.get_page(page)
    
    serializer = FileSerializer(current_page, many=True)
    
    return Response({
        'code': 200,
        'msg': '获取成功',
        'file_list': serializer.data,
        'total': len(filtered_files),
        'page': page,
        'page_size': page_size
    })


@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def download_file(request, file_id):
    """
    文件下载接口 - 所有登录用户都可以下载
    """
    file_record = get_object_or_404(FileManager, id=file_id)
    
    if not os.path.exists(file_record.file_path):
        raise Http404("文件不存在")
    
    with open(file_record.file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_record.original_filename}"'
        return response


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedCustom])
def delete_file(request, file_id):
    """
    删除文件接口 - 仅管理员和文件上传者可以删除
    """
    file_record = get_object_or_404(FileManager, id=file_id)
    
    # 获取当前用户
    current_user = request.user
    
    # 权限检查：只有管理员或文件上传者本人可以删除
    if current_user.username != 'admin' and file_record.uploader_id != current_user.id:
        return Response({
            'code': 403, 
            'msg': '您没有权限删除此文件'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # 删除物理文件
    if os.path.exists(file_record.file_path):
        try:
            os.remove(file_record.file_path)
        except OSError:
            pass  # 如果物理文件不存在或无法删除，继续删除数据库记录
    
    # 删除数据库记录
    file_record.delete()
    
    return Response({'code': 200, 'msg': '删除成功'})


@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def file_detail(request, file_id):
    """
    获取文件详情接口 - 所有登录用户都可以查看
    """
    file_record = get_object_or_404(FileManager, id=file_id)
    serializer = FileSerializer(file_record)
    
    return Response({'code': 200, 'msg': '获取成功', 'data': serializer.data})