# Copyright (c) 2025 知识库管理系统. All rights reserved.

"""
权限标识常量定义
格式：模块:功能:操作
"""

# 用户管理权限
class UserPermissions:
    """用户管理权限标识"""
    VIEW = 'sys:user:view'      # 查看用户
    ADD = 'sys:user:add'        # 新增用户
    EDIT = 'sys:user:edit'      # 编辑用户
    DELETE = 'sys:user:delete'  # 删除用户
    RESET_PWD = 'sys:user:resetPwd'  # 重置密码
    GRANT_ROLE = 'sys:user:grant'    # 分配角色
    EXPORT = 'sys:user:export'  # 导出用户

# 角色管理权限
class RolePermissions:
    """角色管理权限标识"""
    VIEW = 'sys:role:view'      # 查看角色
    ADD = 'sys:role:add'        # 新增角色
    EDIT = 'sys:role:edit'      # 编辑角色
    DELETE = 'sys:role:delete'  # 删除角色
    GRANT = 'sys:role:grant'    # 分配权限

# 菜单管理权限
class MenuPermissions:
    """菜单管理权限标识"""
    VIEW = 'sys:menu:view'      # 查看菜单
    ADD = 'sys:menu:add'        # 新增菜单
    EDIT = 'sys:menu:edit'      # 编辑菜单
    DELETE = 'sys:menu:delete'  # 删除菜单

# 部门管理权限
class DeptPermissions:
    """部门管理权限标识"""
    VIEW = 'sys:dept:view'      # 查看部门
    ADD = 'sys:dept:add'        # 新增部门
    EDIT = 'sys:dept:edit'      # 编辑部门
    DELETE = 'sys:dept:delete'  # 删除部门

# 文件管理权限
class FilePermissions:
    """文件管理权限标识"""
    VIEW = 'sys:file:view'       # 查看文件
    UPLOAD = 'sys:file:upload'   # 上传文件
    DOWNLOAD = 'sys:file:download'  # 下载文件
    DELETE = 'sys:file:delete'   # 删除文件

# 知识库管理权限
class RepositoryPermissions:
    """知识库管理权限标识"""
    VIEW = 'sys:repository:view'      # 查看知识库
    ADD = 'sys:repository:add'        # 新增知识库
    EDIT = 'sys:repository:edit'      # 编辑知识库
    DELETE = 'sys:repository:delete'  # 删除知识库
    REVIEW = 'sys:repository:review'  # 审核知识库

# 事件管理权限
class EventPermissions:
    """事件管理权限标识"""
    VIEW = 'sys:event:view'      # 查看事件
    ADD = 'sys:event:add'        # 新增事件
    EDIT = 'sys:event:edit'      # 编辑事件
    DELETE = 'sys:event:delete'  # 删除事件

# 审批管理权限
class ApprovalPermissions:
    """审批管理权限标识"""
    VIEW = 'sys:approval:view'       # 查看审批
    APPROVE = 'sys:approval:approve' # 审批通过
    REJECT = 'sys:approval:reject'   # 审批拒绝
    CANCEL = 'sys:approval:cancel'   # 撤销审批


# 所有权限集合（用于管理员角色）
ALL_PERMISSIONS = [
    # 用户管理
    UserPermissions.VIEW, UserPermissions.ADD, UserPermissions.EDIT,
    UserPermissions.DELETE, UserPermissions.RESET_PWD, UserPermissions.GRANT_ROLE,
    UserPermissions.EXPORT,
    
    # 角色管理
    RolePermissions.VIEW, RolePermissions.ADD, RolePermissions.EDIT,
    RolePermissions.DELETE, RolePermissions.GRANT,
    
    # 菜单管理
    MenuPermissions.VIEW, MenuPermissions.ADD, MenuPermissions.EDIT,
    MenuPermissions.DELETE,
    
    # 部门管理
    DeptPermissions.VIEW, DeptPermissions.ADD, DeptPermissions.EDIT,
    DeptPermissions.DELETE,
    
    # 文件管理
    FilePermissions.VIEW, FilePermissions.UPLOAD, FilePermissions.DOWNLOAD,
    FilePermissions.DELETE,
    
    # 知识库管理
    RepositoryPermissions.VIEW, RepositoryPermissions.ADD, RepositoryPermissions.EDIT,
    RepositoryPermissions.DELETE, RepositoryPermissions.REVIEW,
    
    # 事件管理
    EventPermissions.VIEW, EventPermissions.ADD, EventPermissions.EDIT,
    EventPermissions.DELETE,
    
    # 审批管理
    ApprovalPermissions.VIEW, ApprovalPermissions.APPROVE, ApprovalPermissions.REJECT,
    ApprovalPermissions.CANCEL,
]
