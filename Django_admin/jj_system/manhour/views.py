# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from manhour.models import SysManhour,SysManhourSerializer
from user.models import SysUser
from department.models import SysDept
from items.models import SysItem

# class SearchView(View):
#     def post(self, request):
#         try:
#             # 解析请求数据
#             data = json.loads(request.body.decode("utf-8"))
#             page_num = data['pageNum']  # 当前页（假设从1开始）
#             page_size = data['pageSize']  # 每页条数
#             query = data.get('query', '').strip()
#         except (KeyError, json.JSONDecodeError) as e:
#             return JsonResponse({'code': 400, 'msg': f'参数错误：{str(e)}'})
#
#         # 获取当前登录用户的ID
#         current_user_id = request.user.id
#         print('用户id>>>', current_user_id)
#         # 查询工时数据并分页
#         # 查询工时数据并分页，只获取当前用户的数据
#         manhour_queryset = SysManhour.objects.filter(user_id=current_user_id).order_by('-create_time')
#
#         # 如果有查询关键词，添加多字段模糊过滤（数据库层面高效过滤）
#         if query:
#             # 2. 根据关键字模糊匹配用户名，获取所有匹配的user_id
#             match_user_ids = SysUser.objects.filter(
#                 realname__icontains=query  # 假设用户名字段是realname，可根据实际调整
#             ).values_list('id', flat=True)
#             # 3. 过滤工时数据：部门ID匹配 或 用户ID匹配
#             manhour_queryset = manhour_queryset.filter(
#                Q(user_id__in=match_user_ids)
#             )
#
#         # 分页处理
#         paginator = Paginator(manhour_queryset, page_size)
#
#         try:
#             manhour_page = paginator.page(page_num)
#         except Exception as e:
#             return JsonResponse({'code': 400, 'msg': f'分页错误：{str(e)}'})
#
#         # 转换为字典列表
#         manhours = list(manhour_page.object_list.values())
#         total = manhour_queryset.count()
#
#         # 批量提取关联ID（过滤空值，避免无效查询）
#         dept_ids = [m['dept_id'] for m in manhours if m.get('dept_id')]
#         user_ids = [m['user_id'] for m in manhours if m.get('user_id')]
#
#         # 批量查询关联数据（一次查询所有需要的部门和用户）
#         dept_map = {d.id: d.name for d in SysDept.objects.filter(id__in=dept_ids)}
#         user_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=user_ids)}  # 假设需要用户名，可根据实际需求调整字段
#
#         # 给每条工时数据补充部门名称和用户名
#         for manhour in manhours:
#             # 补充部门名称（默认空字符串）
#             manhour['dept_name'] = dept_map.get(manhour.get('dept_id'), '')
#             # 补充用户名（默认空字符串）
#             manhour['user_name'] = user_map.get(manhour.get('user_id'), '')
#
#         return JsonResponse({
#             'code': 200,
#             'manhourList': manhours,
#             'total': total
#         })

class SearchView(View):
    def post(self, request):
        try:
            # 解析请求数据
            data = json.loads(request.body.decode("utf-8"))
            page_num = data['pageNum']  # 当前页（假设从1开始）
            page_size = data['pageSize']  # 每页条数
            query = data.get('query', '').strip()
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'code': 400, 'msg': f'参数错误：{str(e)}'})

        # 获取当前登录用户的信息
        current_user = request.user
        current_user_id = current_user.id
        current_dept_id = getattr(current_user, 'dept_id', None)
        current_level_id = getattr(current_user, 'level_id', 0)  # 职级ID
        
        # 获取用户角色列表
        from role.models import SysUserRole, SysRole
        user_roles = SysUserRole.objects.filter(user_id=current_user_id).values_list('role__name', flat=True)
        user_role_names = list(user_roles)
        
        # 检查是否是超级管理员（ID=1）
        is_super_admin = current_user_id == 1
        
        # 检查是否是管理员（角色名包含"管理员"）
        is_admin = '管理员' in user_role_names or any('管理员' in r for r in user_role_names)
        
        # 检查是否是经理角色（产品经理、技术经理、经理等）
        manager_keywords = ['经理', '主管', '总监', '负责人']
        is_manager = any(any(kw in r for kw in manager_keywords) for r in user_role_names)
        
        # 职级权限判断（按职级划分）
        # level_id: 1=总经理, 2=经理, 3=主管, 4=员工
        if is_super_admin or is_admin:
            # 超级管理员和管理员：获取全部数据（包括所有人的工时）
            manhour_queryset = SysManhour.objects.all().order_by('-create_time')
        elif current_level_id == 1:
            # 总经理：可以看到所有人（除了超级管理员和管理员自己）
            manhour_queryset = SysManhour.objects.all().order_by('-create_time')
        elif current_level_id in [2, 3] and current_dept_id:
            # 经理和主管：看自己部门所有人的工时
            manhour_queryset = SysManhour.objects.filter(dept_id=current_dept_id).order_by('-create_time')
        else:
            # 员工和其他：只能看自己的数据
            manhour_queryset = SysManhour.objects.filter(user_id=current_user_id).order_by('-create_time')

        # 如果有查询关键词，添加多字段模糊过滤（数据库层面高效过滤）
        if query:
            # 根据关键字模糊匹配用户名，获取所有匹配的user_id
            match_user_ids = SysUser.objects.filter(
                realname__icontains=query
            ).values_list('id', flat=True)
            # 过滤工时数据
            manhour_queryset = manhour_queryset.filter(
                Q(user_id__in=match_user_ids)
            )

        # 分页处理
        paginator = Paginator(manhour_queryset, page_size)

        try:
            manhour_page = paginator.page(page_num)
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': f'分页错误：{str(e)}'})

        # 转换为字典列表
        manhours = list(manhour_page.object_list.values())
        total = manhour_queryset.count()

        # 批量提取关联ID（过滤空值，避免无效查询）
        dept_ids = [m['dept_id'] for m in manhours if m.get('dept_id')]
        user_ids = [m['user_id'] for m in manhours if m.get('user_id')]

        # 批量查询关联数据（一次查询所有需要的部门和用户）
        dept_map = {d.id: d.name for d in SysDept.objects.filter(id__in=dept_ids)}
        user_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=user_ids)}

        # 给每条工时数据补充部门名称和用户名
        for manhour in manhours:
            # 补充部门名称（默认空字符串）
            manhour['dept_name'] = dept_map.get(manhour.get('dept_id'), '')
            # 补充用户名（默认空字符串）
            manhour['user_name'] = user_map.get(manhour.get('user_id'), '')

        return JsonResponse({
            'code': 200,
            'manhourList': manhours,
            'total': total
        })
class SaveView(View):
    ADD_FLAG = -1  # 新增标识符

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            record_id = data.get('id')

            now = timezone.localtime(timezone.now())

            if record_id == self.ADD_FLAG:  # 添加
                obj_sys_manhour = SysManhour(
                    dept_id=data['dept_id'],
                    user_id=data['user_id'],
                    date_time=data['date_time'],
                    report_type=data['report_type'],
                    project_number=data['project_number'],
                    job_description=data['job_description'],
                    man_hour=data['man_hour'],
                    issue=data['issue'],
                    coordinate=data['coordinate'],
                    work_plan=data['work_plan'],
                    remark=data.get('remark', ''),
                    create_time=now
                )
                obj_sys_manhour.save()
            else:  # 修改
                obj_sys_manhour = SysManhour.objects.get(id=record_id)
                obj_sys_manhour.dept_id = data['dept_id']
                obj_sys_manhour.user_id = data['user_id']
                obj_sys_manhour.date_time = data['date_time']
                obj_sys_manhour.report_type = data['report_type']
                obj_sys_manhour.project_number = data['project_number']
                obj_sys_manhour.job_description = data['job_description']
                obj_sys_manhour.man_hour = data['man_hour']
                obj_sys_manhour.issue = data['issue']
                obj_sys_manhour.coordinate = data['coordinate']
                obj_sys_manhour.work_plan = data['work_plan']
                obj_sys_manhour.remark = data.get('remark', '')
                obj_sys_manhour.update_time = now
                obj_sys_manhour.save()

            return JsonResponse({'code': 200})
        except KeyError as e:
            return JsonResponse({'code': 400, 'msg': f'缺少必要字段: {e}'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})


class ActionView(View):
    def get(self, request):
        try:
            record_id = int(request.GET.get("id"))
            manhour_object = SysManhour.objects.get(id=record_id)
            return JsonResponse({'code': 200, 'manhour': SysManhourSerializer(manhour_object).data})
        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except SysManhour.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应记录'})

    def delete(self, request):
        try:
            ids = json.loads(request.body.decode("utf-8"))
            if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
                raise TypeError("IDs must be a list of integers.")
            SysManhour.objects.filter(id__in=ids).delete()
            return JsonResponse({'code': 200, 'msg': '删除成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})


class DeptListView(View):
    def get(self, request):
        dept_list = list(SysDept.objects.all().values('id', 'name'))
        return JsonResponse({'code': 200, 'data': dept_list})


class UserListView(View):
    def get(self, request):
        user_list = list(SysUser.objects.all().values('id', 'realname'))
        return JsonResponse({'code': 200, 'data': user_list})

class ItemListView(View):
    def get(self, request):
        item_list = list(SysItem.objects.all().values('id', 'project_number'))
        return JsonResponse({'code': 200, 'data': item_list})