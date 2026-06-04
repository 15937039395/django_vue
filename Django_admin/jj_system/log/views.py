# Copyright (c) 2025 知识库管理系统. All rights reserved.


import json
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from log.models import SysOperLog
from django.db.models import Q


# user/views.py (添加以下代码)
class OperLogView(View):
    """操作日志查询"""

    def post(self, request):
        try:
            # 只有超级管理员（ID=1）可以查看日志
            if not request.user.is_authenticated or request.user.id != 1:
                return JsonResponse({'code': 403, 'msg': '无权限访问'})
            
            data = json.loads(request.body.decode("utf-8"))
            pageNum = data.get('pageNum', 1)
            pageSize = data.get('pageSize', 10)
            query = data.get('query', '')

            queryset = SysOperLog.objects.select_related('user').exclude(operation__startswith='访问').order_by('-create_time')

            if query:
                queryset = queryset.filter(
                    Q(user__username__icontains=query) |
                    Q(operation__icontains=query) |
                    Q(path__icontains=query) |
                    Q(ip__icontains=query)
                )

            paginator = Paginator(queryset, pageSize)
            logPage = paginator.page(pageNum)
            logs = []
            for log in logPage.object_list:
                logs.append({
                    'id': log.id,
                    'user_id': log.user.id if log.user else None,
                    'user_name': (log.user.realname or log.user.username) if log.user else '匿名',
                    'operation': log.operation,
                    'method': log.method,
                    'path': log.path,
                    'ip': log.ip,
                    'status': log.status,
                    'error_msg': log.error_msg,
                    'create_time': log.create_time.strftime('%Y-%m-%dT%H:%M:%S')
                })

            return JsonResponse({
                'code': 200,
                'logList': logs,
                'total': paginator.count
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'查询失败：{str(e)}'})


# 在适当的views.py中添加
class OperationLogView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            pageNum = data.get('pageNum', 1)
            pageSize = data.get('pageSize', 10)

            # 查询数据库中的操作日志
            logs = SysOperLog.objects.all()

            # 处理查询条件（根据前端参数添加过滤）
            if data.get('status'):
                logs = logs.filter(status=data.get('status'))
            # 更多条件...

            # 分页处理
            paginator = Paginator(logs, pageSize)
            logPage = paginator.page(pageNum)
            logList = list(logPage.object_list.values())

            return JsonResponse({
                'code': 200,
                'logList': logList,
                'total': paginator.count
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})
