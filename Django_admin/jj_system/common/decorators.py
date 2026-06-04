# Copyright (c) 2025 知识库管理系统. All rights reserved.

"""
权限装饰器
提供视图函数的权限检查功能
"""
from functools import wraps
from django.http import JsonResponse
from role.models import SysUserRole
from menu.models import SysRoleMenu, SysMenu


def require_permissions(*perms):
    """
    权限检查装饰器
    检查用户是否拥有指定的按钮权限
    
    Args:
        *perms: 权限标识列表，如 'sys:user:add', 'sys:user:edit'
        
    Usage:
        @require_permissions('sys:user:add')
        def create_user(request):
            pass
            
        @require_permissions('sys:user:edit', 'sys:user:delete')
        def update_user(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # 获取用户所有权限
            user_perms = get_user_permissions(user)
            
            # 检查是否拥有所需权限
            missing_perms = []
            for perm in perms:
                if perm not in user_perms:
                    missing_perms.append(perm)
            
            if missing_perms:
                return JsonResponse({
                    'code': 403,
                    'msg': f'没有操作权限：{", ".join(missing_perms)}'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions(user):
    """
    获取用户所有权限标识
    
    Args:
        user: 用户对象
        
    Returns:
        set: 权限标识集合，如 {'sys:user:add', 'sys:user:edit', ...}
    """
    # 如果是超级管理员，返回所有权限
    if user.username == 'admin':
        from common.permissions import ALL_PERMISSIONS
        return set(ALL_PERMISSIONS)
    
    # 获取用户角色
    role_ids = SysUserRole.objects.filter(user_id=user.id).values_list('role_id', flat=True)
    
    if not role_ids:
        return set()
    
    # 获取角色对应的菜单ID
    menu_ids = SysRoleMenu.objects.filter(role_id__in=role_ids).values_list('menu_id', flat=True)
    
    if not menu_ids:
        return set()
    
    # 获取菜单权限标识
    perms = SysMenu.objects.filter(id__in=menu_ids).values_list('perms', flat=True)
    
    # 过滤空值并返回集合
    return set([p for p in perms if p])


def check_permission(user, perm):
    """
    检查用户是否拥有指定权限
    
    Args:
        user: 用户对象
        perm: 权限标识，如 'sys:user:add'
        
    Returns:
        bool: True表示有权限，False表示无权限
    """
    user_perms = get_user_permissions(user)
    return perm in user_perms
