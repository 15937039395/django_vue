# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from menu.models import SysRoleMenu
from role.models import SysRole, SysRoleSerializer, SysUserRole


# Create your views here.
# 查询所有角色信息
class ListAllView(View):

    def get(self, request):
        obj_roleList = SysRole.objects.all().values()  # 转成字典
        roleList = list(obj_roleList)  # 把外层的容器转为List
        return JsonResponse(
            {'code': 200, 'roleList': roleList})


# 角色信息查询
class SearchView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pageNum = data['pageNum']  # 当前页
        pageSize = data['pageSize']  # 每页大小
        query = data['query']  # 查询参数
        import logging
        logging.info(f'页面大小: {pageSize}, 页码: {pageNum}')
        roleListPage = Paginator(SysRole.objects.filter(name__icontains=query), pageSize).page(pageNum)
        obj_roles = roleListPage.object_list.values()  # 转成字典
        roles = list(obj_roles)  # 把外层的容器转为List
        total = SysRole.objects.filter(name__icontains=query).count()
        return JsonResponse(
            {'code': 200, 'roleList': roles, 'total': total})


class SaveView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        if data['id'] == -1:  # 添加
            obj_sysRole = SysRole(
                name=data['name'], 
                code=data['code'], 
                data_scope=data.get('data_scope', 4),  # 添加数据权限字段，默认仅本人
                remark=data['remark']
            )
            obj_sysRole.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            obj_sysRole.save()
        else:  # 修改
            obj_sysRole = SysRole.objects.get(id=data['id'])
            obj_sysRole.name = data['name']
            obj_sysRole.code = data['code']
            obj_sysRole.data_scope = data.get('data_scope', 4)  # 更新数据权限字段
            obj_sysRole.remark = data['remark']
            obj_sysRole.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            obj_sysRole.save()
        return JsonResponse({'code': 200})


# 角色基本操作
class ActionView(View):

    def get(self, request):
        """
        根据id获取角色信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        role_object = SysRole.objects.get(id=id)
        return JsonResponse({'code': 200, 'role': SysRoleSerializer(role_object).data})

    def delete(self, request):
        """
        删除操作
        :param request:
        :return:
        """
        idList = json.loads(request.body.decode("utf-8"))
        SysUserRole.objects.filter(role_id__in=idList).delete()
        SysRoleMenu.objects.filter(role_id__in=idList).delete()
        SysRole.objects.filter(id__in=idList).delete()
        return JsonResponse({'code': 200})


# 根据角色查询菜单权限
class MenusView(View):

    def get(self, request):
        id = request.GET.get("id")
        menuList = SysRoleMenu.objects.filter(role_id=id).values("menu_id")
        menuIdList = [m['menu_id'] for m in menuList]
        return JsonResponse(
            {'code': 200, 'menuIdList': menuIdList})


# # 角色权限授权
class GrantMenu(View):

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            role_id = data['id']
            menuIdList = data['menuIds']
            import logging
            logging.info(f'角色ID: {role_id}, 菜单ID列表: {menuIdList}')
            
            # 验证角色是否存在
            if not SysRole.objects.filter(id=role_id).exists():
                return JsonResponse({'code': 400, 'msg': f'角色ID {role_id} 不存在'})
            
            SysRoleMenu.objects.filter(role_id=role_id).delete()  # 删除角色菜单关联表中的指定角色数据
            for menuId in menuIdList:
                roleMenu = SysRoleMenu(role_id=role_id, menu_id=menuId)
                roleMenu.save()
            return JsonResponse({'code': 200})
        except Exception as e:
            import logging
            logging.exception(f'角色权限授权失败: {str(e)}')
            return JsonResponse({'code': 500, 'msg': f'授权失败: {str(e)}'})
