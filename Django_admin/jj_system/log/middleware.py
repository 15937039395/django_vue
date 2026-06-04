# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from django.utils.deprecation import MiddlewareMixin
from log.models import SysOperLog
from user.models import SysUser
from jwt import decode
from jj_system import settings


class OperLogMiddleware(MiddlewareMixin):
    """操作日志中间件"""

    def process_response(self, request, response):
        # 排除白名单路径
        white_list = ["/user/login", "/media/"]
        path = request.path
        if any(path.startswith(item) for item in white_list):
            return response

        # 创建日志记录
        log = SysOperLog()
        log.method = request.method
        log.path = path
        log.ip = self.get_client_ip(request)

        # 记录请求参数
        try:
            if request.method == "GET":
                log.params = json.dumps(dict(request.GET))
            else:
                log.params = request.body.decode("utf-8")
        except:
            log.params = "无法解析的参数"

        # 获取操作用户
        try:
            # 优先使用request.user（JwtAuthenticationMiddleware已设置）
            if hasattr(request, 'user') and request.user and request.user.is_authenticated:
                log.user = request.user
            else:
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    # 移除 'Bearer ' 前缀（如果存在）
                    if auth_header.startswith('Bearer '):
                        token = auth_header.replace('Bearer ', '')
                    elif auth_header.startswith('JWT '):
                        token = auth_header.replace('JWT ', '')
                    else:
                        token = auth_header
                    payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                    user_id = payload.get('user_id')
                    log.user = SysUser.objects.get(id=user_id)
        except:
            pass

        # 记录操作状态
        if 200 <= response.status_code < 300:
            log.status = 0
        else:
            log.status = 1
            log.error_msg = response.content.decode("utf-8")[:500]

        # 记录操作内容
        log.operation = self.get_operation_desc(path, request.method)
        
        # 过滤掉纯访问类日志（未在operation_map中定义的GET请求）
        if log.operation.startswith('访问') and request.method == 'GET':
            return response
        
        log.save()

        return response

    def get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def get_operation_desc(self, path, method):
        """根据路径和方法生成操作描述"""
        operation_map = {
            # 用户模块
            ('/user/save', 'POST'): '新增/修改用户',
            ('/user/action', 'DELETE'): '删除用户',
            ('/user/pwd', 'POST'): '修改密码',
            # 部门模块
            ('/department/save', 'POST'): '新增/修改部门',
            # 菜单模块
            ('/menu/save', 'POST'): '新增/修改菜单',
            ('/menu/action', 'DELETE'): '删除菜单',
            # 角色模块
            ('/role/save', 'POST'): '新增/修改角色',
            ('/role/action', 'DELETE'): '删除角色',
            ('/role/grant-menu', 'POST'): '角色授权',
            # 工时模块
            ('/manhour/save', 'POST'): '新增/修改工时',
            ('/manhour/action', 'DELETE'): '删除工时',
        }
        return operation_map.get((path, method), f"访问{path}")
