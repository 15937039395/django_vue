# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from django.http import JsonResponse
from django.views import View
from notification.models import SysNotification
from django.utils import timezone


class NotificationListView(View):
    """获取通知列表"""

    def get(self, request):
        try:
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            if not user_id:
                return JsonResponse({'code': 401, 'msg': '未登录'})

            # 获取分页参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('pageSize', 10))
            
            # 获取筛选参数
            status = request.GET.get('status')
            n_type = request.GET.get('type')
            
            # 查询通知
            notifications = SysNotification.objects.filter(user_id=user_id)
            
            if status is not None:
                notifications = notifications.filter(status=int(status))
            if n_type:
                notifications = notifications.filter(type=n_type)
            
            total = notifications.count()
            start = (page - 1) * page_size
            end = start + page_size
            notifications = notifications[start:end]
            
            data = []
            for n in notifications:
                data.append({
                    'id': n.id,
                    'title': n.title,
                    'content': n.content,
                    'type': n.type,
                    'status': n.status,
                    'status_text': n.get_status_display(),
                    'related_id': n.related_id,
                    'create_time': n.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'read_time': n.read_time.strftime('%Y-%m-%d %H:%M:%S') if n.read_time else '-',
                })
            
            return JsonResponse({
                'code': 200,
                'data': data,
                'total': total,
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取通知失败: {str(e)}'})


class UnreadCountView(View):
    """获取未读通知数量"""

    def get(self, request):
        try:
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            if not user_id:
                return JsonResponse({'code': 401, 'msg': '未登录'})

            count = SysNotification.objects.filter(
                user_id=user_id, 
                status=SysNotification.STATUS_UNREAD
            ).count()
            
            return JsonResponse({
                'code': 200,
                'data': {'count': count},
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取未读数量失败: {str(e)}'})


class MarkAsReadView(View):
    """标记通知为已读"""

    def post(self, request):
        try:
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            if not user_id:
                return JsonResponse({'code': 401, 'msg': '未登录'})

            data = json.loads(request.body.decode('utf-8'))
            notification_id = data.get('id')
            
            if notification_id:
                # 标记单条
                notification = SysNotification.objects.filter(
                    id=notification_id, 
                    user_id=user_id
                ).first()
                if notification:
                    notification.status = SysNotification.STATUS_READ
                    notification.read_time = timezone.now()
                    notification.save()
            else:
                # 标记全部已读
                SysNotification.objects.filter(
                    user_id=user_id, 
                    status=SysNotification.STATUS_UNREAD
                ).update(
                    status=SysNotification.STATUS_READ,
                    read_time=timezone.now()
                )
            
            return JsonResponse({'code': 200, 'msg': '操作成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'操作失败: {str(e)}'})


class DeleteNotificationView(View):
    """删除通知"""

    def post(self, request):
        try:
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            if not user_id:
                return JsonResponse({'code': 401, 'msg': '未登录'})

            data = json.loads(request.body.decode('utf-8'))
            notification_id = data.get('id')
            
            if notification_id:
                SysNotification.objects.filter(
                    id=notification_id, 
                    user_id=user_id
                ).delete()
            
            return JsonResponse({'code': 200, 'msg': '删除成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'删除失败: {str(e)}'})
