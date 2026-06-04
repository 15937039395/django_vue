# Copyright (c) 2025 知识库管理系统. All rights reserved.

from rest_framework import permissions


class IsAuthenticatedCustom(permissions.BasePermission):
    """
    自定义认证权限类
    适配自定义的 SysUser 模型
    """
    def has_permission(self, request, view):
        # 检查 request.user 是否存在且不是 AnonymousUser
        return (
            hasattr(request, 'user') and 
            request.user is not None and 
            hasattr(request.user, 'id') and 
            request.user.id is not None
        )
