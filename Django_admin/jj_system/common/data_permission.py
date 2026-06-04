# Copyright (c) 2025 知识库管理系统. All rights reserved.

"""
数据权限工具类
提供数据权限过滤功能，根据用户角色的数据权限范围自动过滤查询集
"""
from department.models import SysDept
from role.models import SysUserRole, SysRole


class DataPermissionUtil:
    """数据权限工具类"""
    
    @staticmethod
    def get_dept_and_children(dept_id):
        """
        递归获取部门及所有子部门ID
        
        Args:
            dept_id: 部门ID
            
        Returns:
            list: 包含该部门及所有子部门的ID列表
        """
        dept_ids = [dept_id]
        
        # 查找所有子部门
        children = SysDept.objects.filter(parent_id=dept_id)
        for child in children:
            # 递归获取子部门的子部门
            dept_ids.extend(DataPermissionUtil.get_dept_and_children(child.id))
        
        return dept_ids
    
    @staticmethod
    def get_user_data_scope(user):
        """
        获取用户的数据权限范围
        如果用户有多个角色，返回权限最大的范围（数字最小）
        
        Args:
            user: 用户对象
            
        Returns:
            int: 数据权限范围（1-全部 2-本部门及下级 3-仅本部门 4-仅本人）
        """
        # 获取用户所有角色
        user_roles = SysUserRole.objects.filter(user_id=user.id).values_list('role_id', flat=True)
        roles = SysRole.objects.filter(id__in=user_roles)
        
        # 如果用户没有角色，默认返回仅本人权限
        if not roles:
            return SysRole.DATA_SCOPE_SELF
        
        # 返回最大权限（数字最小）
        return min([role.data_scope for role in roles])
    
    @staticmethod
    def apply_data_filter(queryset, user, user_field='user_id', dept_field='dept_id'):
        """
        应用数据权限过滤到查询集
        
        Args:
            queryset: Django QuerySet 对象
            user: 当前登录用户
            user_field: 用户ID字段名（如果模型有用户字段）
            dept_field: 部门ID字段名（如果模型有部门字段）
            
        Returns:
            QuerySet: 过滤后的查询集
            
        Examples:
            # 过滤用户列表
            users = DataPermissionUtil.apply_data_filter(
                SysUser.objects.all(),
                request.user,
                user_field='id',
                dept_field='dept_id'
            )
            
            # 过滤文件列表
            files = DataPermissionUtil.apply_data_filter(
                FileManager.objects.all(),
                request.user,
                user_field='uploader_id',
                dept_field='dept_id'
            )
        """
        # 获取用户的数据权限范围
        scope = DataPermissionUtil.get_user_data_scope(user)
        
        if scope == SysRole.DATA_SCOPE_ALL:
            # 全部数据：不过滤
            return queryset
        
        elif scope == SysRole.DATA_SCOPE_DEPT_AND_SUB:
            # 本部门及下级部门：获取所有相关部门ID并过滤
            dept_ids = DataPermissionUtil.get_dept_and_children(user.dept_id)
            return queryset.filter(**{f'{dept_field}__in': dept_ids})
        
        elif scope == SysRole.DATA_SCOPE_DEPT:
            # 仅本部门：只过滤本部门数据
            return queryset.filter(**{dept_field: user.dept_id})
        
        else:  # DATA_SCOPE_SELF
            # 仅本人：只能查看自己的数据
            return queryset.filter(**{user_field: user.id})
    
    @staticmethod
    def check_data_permission(user, target_user_id=None, target_dept_id=None):
        """
        检查用户是否有权限访问指定的数据
        
        Args:
            user: 当前登录用户
            target_user_id: 目标数据的用户ID
            target_dept_id: 目标数据的部门ID
            
        Returns:
            bool: True表示有权限，False表示无权限
        """
        scope = DataPermissionUtil.get_user_data_scope(user)
        
        if scope == SysRole.DATA_SCOPE_ALL:
            return True
        
        elif scope == SysRole.DATA_SCOPE_DEPT_AND_SUB:
            if target_dept_id:
                dept_ids = DataPermissionUtil.get_dept_and_children(user.dept_id)
                return target_dept_id in dept_ids
            return False
        
        elif scope == SysRole.DATA_SCOPE_DEPT:
            if target_dept_id:
                return target_dept_id == user.dept_id
            return False
        
        else:  # DATA_SCOPE_SELF
            if target_user_id:
                return target_user_id == user.id
            return False
