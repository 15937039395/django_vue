# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from jj_system import settings
from user.models import SysUser
from django.contrib.auth.models import AnonymousUser

class JwtAuthenticationMiddleware(MiddlewareMixin):
    """JWT认证中间件（示例实现）"""
    def process_request(self, request):
        # 定义不需要认证的路径
        excluded_paths = [
            '/api/login',  # 登录接口
            '/api/logout',  # 登出接口
            '/api/register',  # 注册接口
        ]
        
        # 检查是否为不需要认证的路径
        if request.path in excluded_paths or request.path.startswith('/admin/'):
            return None
        
        # 从请求头获取token
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        # 检查是否为公共路径
        if self.is_public_path(request.path):
            # 公共路径，如果有token则验证，没有则继续
            if auth_header:
                # 移除 'Bearer ' 前缀（如果存在）
                if auth_header.startswith('Bearer '):
                    token = auth_header.replace('Bearer ', '')
                elif auth_header.startswith('JWT '):
                    token = auth_header.replace('JWT ', '')
                else:
                    token = auth_header
                
                try:
                    # 使用SimpleJWT的AccessToken来解析
                    validated_token = AccessToken(token)
                    user_id = validated_token.get('user_id')
                    # 获取用户对象
                    user = SysUser.objects.get(id=user_id)
                    # 将用户信息存入request
                    request.user = user
                    request._user = user
                    request._cached_user = user
                except Exception as e:
                    return JsonResponse({'code': 401, 'msg': 'Token无效或已过期'})
        else:
            # 非公共路径，需要token认证
            if not auth_header:
                return JsonResponse({'code': 401, 'msg': '缺少认证token'})
            
            # 移除 'Bearer ' 前缀（如果存在）
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
            elif auth_header.startswith('JWT '):
                token = auth_header.replace('JWT ', '')
            else:
                token = auth_header
            
            try:
                # 使用SimpleJWT的AccessToken来解析
                validated_token = AccessToken(token)
                user_id = validated_token.get('user_id')
                # 获取用户对象
                user = SysUser.objects.get(id=user_id)
                # 将用户信息存入request（Django原生request）
                request.user = user
                # 同时设置 _user 属性（DRF 使用）
                request._user = user
                # 标记为已认证
                request._cached_user = user
            except Exception as e:
                return JsonResponse({'code': 401, 'msg': f'Token无效或已过期: {str(e)}'})
        
        return None
    
    def is_public_path(self, path):
        """判断是否为公共路径"""
        public_paths = [
            '/api/login',
            '/api/logout',
            '/api/register',
            '/api/auth/',
            '/static/',
            '/media/',
            # 包含用户登录相关的路径
            '/api/user/login',
            '/api/auth/token',
            # 包含用户检查和重置密码相关的路径
            '/user/check-admin',
            '/user/reset-admin-password',
            # 地图接口（免认证）
            '/map/',
        ]
        
        for public_path in public_paths:
            if path.startswith(public_path):
                return True
        
        # 特别处理前端静态资源路径
        if path.startswith('/static/') or path.startswith('/media/'):
            return True
        
        # 特别处理用户登录接口
        if path.startswith('/user/login'):
            return True
        
        # 文件管理接口需要认证
        if path.startswith('/files/'):
            return False
        
        # 事件管理接口需要认证
        if path.startswith('/api/event') or path.startswith('/event'):
            return False
        
        # 默认情况下，假设需要认证
        # 但为了兼容性，我们检查是否是API接口
        if path.startswith('/api/'):
            # 检查是否是其他公开API接口
            if path.startswith('/api/public/'):
                return True
            else:
                return False  # 大多数API接口需要认证
        
        # 非API路径，如页面访问，通常需要认证
        return False

