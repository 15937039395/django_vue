# Copyright (c) 2025 知识库管理系统. All rights reserved.


from django.shortcuts import render
from django.db.models import Q
import json
from datetime import datetime, date
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from event.models import SysEventSerializer,SysEvent,SysEventRole,SysEventAssignmentHistory,SysEventAssignmentHistorySerializer
from user.models import SysUser
from department.models import SysDept
from classify.models import ClassifyItem





class SearchView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'message': 'Invalid JSON format'})
        except UnicodeDecodeError:
            return JsonResponse({'code': 400, 'message': 'Invalid encoding'})

        # 输入验证
        try:
            pageNum = int(data['pageNum'])
            pageSize = int(data['pageSize'])
            query = str(data['query'])
        except (KeyError, ValueError, TypeError):
            return JsonResponse({'code': 400, 'message': 'Invalid parameters'})

        # 参数范围验证
        if pageNum < 1 or pageSize < 1 or pageSize > 100:  # 限制最大页面大小
            return JsonResponse({'code': 400, 'message': 'Invalid pagination parameters'})

        # 限制查询长度防止DOS攻击
        if len(query) > 50:
            return JsonResponse({'code': 400, 'message': 'Query too long'})

        try:
            # 查询所有需要的关联数据 - 使用in批量查询减少数据库访问
            event_queryset = SysEvent.objects.filter(event_name__icontains=query).order_by('-id')

            # 获取总数量（复用查询结果）
            total = event_queryset.count()

            # 分页
            paginator = Paginator(event_queryset, pageSize)
            if pageNum > paginator.num_pages and total > 0:
                return JsonResponse({'code': 400, 'message': 'Page number exceeds total pages'})

            eventListPage = paginator.page(pageNum)
            obj_events = eventListPage.object_list.values('id', 'dept_id', 'user_id', 'event_number', 'event_name', 'principal', 'status', 'start_date', 'end_date', 'notification_time', 'create_time', 'update_time', 'remark')
            events = list(obj_events)
            
            # 格式化时间字段为字符串（年月日时分秒格式：YYYY-MM-DD HH:MM:SS）
            for event in events:
                if event.get('notification_time'):
                    if isinstance(event['notification_time'], str):
                        # 如果已经是字符串，保持原样
                        event['notification_time'] = event['notification_time']
                    else:
                        # datetime对象格式化为 YYYY-MM-DD HH:MM:SS
                        event['notification_time'] = event['notification_time'].strftime('%Y-%m-%d %H:%M:%S')

            # 批量获取相关的dept_id和user_id
            dept_ids = set()
            user_ids = set()
            principal_ids = set()

            for event in events:
                dept_id = event.get('dept_id')
                user_id = event.get('user_id')
                principal = event.get('principal')

                if dept_id:
                    dept_ids.add(dept_id)
                if user_id:
                    user_ids.add(user_id)
                if principal:
                    principal_ids.add(principal)

            # 批量查询关联数据
            dept_map = {d.id: d.name for d in SysDept.objects.filter(id__in=dept_ids)}
            all_user_ids = user_ids | principal_ids
            user_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=all_user_ids)}

            # 填充关联数据
            for event in events:
                event['dept_name'] = dept_map.get(event.get('dept_id'), '')
                event['user_name'] = user_map.get(event.get('user_id'), '')
                event['principal'] = user_map.get(event.get('principal'), '')

            return JsonResponse(
                {'code': 200, 'eventList': events, 'total': total})

        except Exception as e:

            return JsonResponse({'code': 500, 'message': 'Internal server error'})

class SaveView(View):

    def post(self, request):
        try:
            import logging
            logging.info('开始处理事件保存请求')
            data = json.loads(request.body.decode("utf-8"))
            logging.info(f'收到的数据: {data}')
            
            # 提取数据
            event_id = data.get('id', -1)
            dept_id = str(data.get('dept_id', ''))
            user_id = str(data.get('user_id', ''))
            event_name = data.get('event_name', '')
            principal_input = data.get('principal', '')
            start_date_str = data.get('start_date', None)
            end_date_str = data.get('end_date', None)
            notification_time_str = data.get('notification_time', None)
            remark = data.get('remark', '')
            
            # 获取当前登录用户信息（用于权限检查）
            current_user = request.user
            current_user_id = str(current_user.id) if hasattr(current_user, 'id') else None
            current_role_id = data.get('current_role_id')  # 从前端传递
            
            # 如果是修改操作，进行权限检查
            if event_id != -1:
                try:
                    existing_event = SysEvent.objects.get(id=event_id)
                    # 非管理员只能修改自己创建的事件
                    if current_role_id != 1 and str(existing_event.user_id) != str(user_id):
                        return JsonResponse({'code': 403, 'message': '您没有权限修改此事件'})
                except SysEvent.DoesNotExist:
                    return JsonResponse({'code': 404, 'message': '事件不存在'})
            
            # 处理日期
            from datetime import datetime, time
            def parse_date(date_str):
                if not date_str or date_str == "":
                    return None
                try:
                    return datetime.strptime(str(date_str), '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    return None
            
            def parse_time(time_str):
                """解析时间字符串，支持 YYYY-MM-DD HH:MM:SS 格式"""
                if not time_str or time_str == "":
                    return None
                try:
                    time_str = str(time_str).strip()
                    # 支持完整的日期时间格式 YYYY-MM-DD HH:MM:SS
                    if ' ' in time_str:
                        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        return None
                except (ValueError, TypeError):
                    return None
            
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            notification_time = parse_time(notification_time_str)
            
            # 处理负责人字段
            # 如果是数字ID，我们保留ID存储，但获取真实姓名用于显示
            principal = str(principal_input)
            principal_display = principal  # 用于存储到数据库的值
            
            try:
                principal_int = int(principal_input)
                # 如果是数字，只用于显示目的获取用户名
                from user.models import SysUser
                user_obj = SysUser.objects.filter(id=principal_int).first()
                if user_obj:
                    principal_display = str(principal_int)  # 存储ID而不是姓名到数据库
            except (ValueError, TypeError):
                # 不是有效整数，保持原值
                principal_display = principal

            
            import logging
            logging.info(f'处理后的数据: id={event_id}, dept_id={dept_id}, user_id={user_id}, event_name={event_name}')
            
            created_id = event_id
            if event_id == -1:  # 新增
                obj_sysEvent = SysEvent(
                    dept_id=dept_id,
                    user_id=user_id,
                    event_name=event_name,
                    principal=principal_display,
                    start_date=start_date,
                    end_date=end_date,
                    notification_time=notification_time,
                    remark=remark
                )
                # 生成事件编号
                obj_sysEvent.event_number = 'JJ-'+datetime.now().strftime("%Y-%m%d-%H%M%S")
                obj_sysEvent.save()
                created_id = obj_sysEvent.id
                import logging
                logging.info('新增事件成功')
            else:  # 更新
                obj_sysEvent = SysEvent.objects.get(id=event_id)
                obj_sysEvent.dept_id = dept_id
                obj_sysEvent.user_id = user_id
                obj_sysEvent.event_name = event_name
                obj_sysEvent.principal = principal_display
                obj_sysEvent.start_date = start_date
                obj_sysEvent.end_date = end_date
                obj_sysEvent.notification_time = notification_time
                obj_sysEvent.remark = remark
                obj_sysEvent.save()
                import logging
                logging.info('更新事件成功')
            
            return JsonResponse({'code': 200, 'id': created_id})
            
        except json.JSONDecodeError:
            import logging
            logging.error('JSON解码错误')
            return JsonResponse({'code': 400, 'message': '无效的JSON格式'})
        except SysEvent.DoesNotExist:
            import logging
            logging.error('事件不存在')
            return JsonResponse({'code': 400, 'message': '事件不存在'})
        except Exception as e:
            import logging
            logging.exception(f'保存事件时发生错误: {str(e)}')
            import traceback
            traceback.print_exc()
            return JsonResponse({'code': 500, 'message': f'服务器内部错误: {str(e)}'})
            



# 角色基本操作
class ActionView(View):

    def get(self, request):
        """
        根据id获取角色信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        event_object = SysEvent.objects.get(id=id)
        
        # 获取关联的部门和用户信息
        from department.models import SysDept
        from user.models import SysUser
        
        event_data = {
            'id': event_object.id,
            'dept_id': event_object.dept_id,
            'user_id': event_object.user_id,
            'event_number': event_object.event_number,
            'event_name': event_object.event_name,
            'principal': event_object.principal,
            'status': event_object.status,
            'start_date': event_object.start_date,
            'end_date': event_object.end_date,
            'notification_time': event_object.notification_time.strftime('%Y-%m-%d %H:%M:%S') if event_object.notification_time else None,
            'create_time': event_object.create_time,
            'update_time': event_object.update_time,
            'remark': event_object.remark,
            # 添加关联的名称
            'dept_name': '',
            'user_name': '',
            'principal_name': event_object.principal,  # 默认为原始值
        }
        
        # 尝试获取部门名称
        try:
            dept = SysDept.objects.get(id=event_object.dept_id)
            event_data['dept_name'] = dept.name
        except SysDept.DoesNotExist:
            event_data['dept_name'] = '部门不存在'
        
        # 尝试获取用户名
        try:
            user = SysUser.objects.get(id=event_object.user_id)
            event_data['user_name'] = user.realname
        except SysUser.DoesNotExist:
            event_data['user_name'] = '用户不存在'
        
        # 尝试获取负责人名称
        try:
            principal_id = int(event_object.principal)
            principal_user = SysUser.objects.get(id=principal_id)
            event_data['principal_name'] = principal_user.realname
        except (ValueError, SysUser.DoesNotExist, TypeError):
            # 如果principal不是有效ID或用户不存在，保持原始值
            event_data['principal_name'] = event_object.principal
        
        return JsonResponse({'code': 200, 'event': event_data})

    def delete(self, request):
        """
        删除操作 - 添加权限控制
        :param request:
        :return:
        """
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            # 解析请求数据
            if isinstance(data, dict):
                idList = data.get('ids', [])
                current_role_id = data.get('role_id')  # 当前用户角色ID
                current_user_id = data.get('user_id')  # 当前用户ID
            elif isinstance(data, list):
                # 兼容旧的请求格式（直接传递IDs数组）
                idList = data
                current_role_id = None
                current_user_id = None
            else:
                return JsonResponse({'code': 400, 'message': '请求数据格式错误'})
            
            # 如果提供了用户信息，进行权限检查
            if current_role_id is not None and current_user_id is not None:
                # 管理员（role_id=1）可以删除任何记录
                if current_role_id != 1:
                    # 非管理员只能删除自己创建的事件
                    events = SysEvent.objects.filter(id__in=idList)
                    for event in events:
                        if str(event.user_id) != str(current_user_id):
                            return JsonResponse({'code': 403, 'message': f'您没有权限删除他人的事件（ID: {event.id}）'})
            
            # 执行删除
            SysEventRole.objects.filter(event_id__in=idList).delete()
            SysEvent.objects.filter(id__in=idList).delete()
            return JsonResponse({'code': 200})
        except Exception as e:
            import logging
            logging.exception(f'删除事件失败: {str(e)}')
            return JsonResponse({'code': 500, 'message': f'删除失败: {str(e)}'})


#根据角色查询菜单权限
class EventView(View):

    def get(self, request):
        try:
            id = request.GET.get("id")
            if not id:
                return JsonResponse({'code': 400, 'msg': '缺少事件ID参数'})
            
            # 验证事件是否存在
            if not SysEvent.objects.filter(id=id).exists():
                return JsonResponse({'code': 404, 'msg': f'事件ID {id} 不存在'})
            
            eventList = SysEventRole.objects.filter(event_id=id).values("user_id")
            eventIdList = [m['user_id'] for m in eventList]
            return JsonResponse(
                {'code': 200, 'eventIdList': eventIdList})
        except Exception as e:
            import logging
            logging.exception(f'查询事件用户列表失败: {str(e)}')
            return JsonResponse({'code': 500, 'msg': f'查询失败: {str(e)}', 'eventIdList': []})


# 角色权限授权 - 添加权限控制
class GrantUser(View):

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            import logging
            logging.info(f'事件数据: {data}')
            event_id = data['id']
            logging.info(f'事件ID: {event_id}')
            userIdList = data.get('menuIds', []) # 这里的 menuIds 其实是用户 ID 列表
            import logging
            logging.info(f'事件ID: {event_id}, 用户ID列表: {userIdList}')
            
            # 获取当前用户信息（用于权限检查）
            current_role_id = data.get('current_role_id')  # 从前端传递
            current_user_id = data.get('current_user_id')  # 从前端传递
            
            # 验证事件是否存在
            try:
                event = SysEvent.objects.get(id=event_id)
            except SysEvent.DoesNotExist:
                return JsonResponse({'code': 400, 'msg': f'事件ID {event_id} 不存在'})
            
            # 权限检查：非管理员只能修改自己创建的事件的参与人员
            if current_role_id is not None and current_role_id != 1:
                if str(event.user_id) != str(current_user_id):
                    return JsonResponse({'code': 403, 'msg': '您没有权限修改此事件的参与人员'})
            
            # 验证用户ID列表中的用户是否存在
            if userIdList:
                existing_users = set(SysUser.objects.filter(id__in=userIdList).values_list('id', flat=True))
                invalid_users = set(userIdList) - existing_users
                if invalid_users:
                    return JsonResponse({'code': 400, 'msg': f'以下用户ID不存在: {list(invalid_users)}'})
            
            # 获取当前操作人（如果有登录信息）
            operator = request.user if hasattr(request, 'user') and not request.user.is_anonymous else None

            # 获取旧的参与者列表
            old_userIdList = set(SysEventRole.objects.filter(event_id=event_id).values_list('user_id', flat=True))
            new_userIdList = set(userIdList)

            # 计算新增和删除的人员
            added_users = new_userIdList - old_userIdList
            removed_users = old_userIdList - new_userIdList

            # 记录历史：移除人员
            for uid in removed_users:
                SysEventAssignmentHistory.objects.create(
                    event=event,
                    user_id=uid,
                    operator=operator if isinstance(operator, SysUser) else None,
                    action=SysEventAssignmentHistory.ACTION_REMOVE,
                    remark="系统自动记录：人员调整取消分配"
                )

            # 记录历史：新增人员
            for uid in added_users:
                SysEventAssignmentHistory.objects.create(
                    event=event,
                    user_id=uid,
                    operator=operator if isinstance(operator, SysUser) else None,
                    action=SysEventAssignmentHistory.ACTION_ADD,
                    remark="系统自动记录：人员调整新增分配"
                )

            # 更新参与者表
            SysEventRole.objects.filter(event_id=event_id).delete()
            for userId in userIdList:
                userMenu = SysEventRole(event_id=event_id, user_id=userId)
                userMenu.save()
            return JsonResponse({'code': 200})
        except Exception as e:
            import logging
            logging.exception(f'事件用户授权失败: {str(e)}')
            return JsonResponse({'code': 500, 'msg': f'授权失败: {str(e)}'})


class DeptListView(View):
    def get(self, request):
        dept_list = list(SysDept.objects.all().values('id', 'name'))
        return JsonResponse({'code': 200, 'data': dept_list})


class UserListView(View):
    def get(self, request):
        user_list = list(SysUser.objects.all().values('id', 'realname'))
        return JsonResponse({'code': 200, 'data': user_list})


class EventListView(View):
    def get(self, request):
        try:
            event_list = list(SysEvent.objects.all().values('id', 'event_name', 'event_number', 'principal', 'start_date', 'end_date'))
            return JsonResponse({'code': 200, 'data': event_list})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})

class ClassifyItemListView(View):
    def get(self, request):
        Classify_list = list(ClassifyItem.objects.all().values('id','project_number'))
        return JsonResponse({'code': 200, 'data': Classify_list})


class EventDetailView(View):
    def get(self, request):
        try:
            event_id = int(request.GET.get("id"))
            
            # 获取事件基本信息
            event = SysEvent.objects.get(id=event_id)
            
            # 获取关联的部门和用户信息
            from department.models import SysDept
            from user.models import SysUser
            
            event_data = {
                'id': event.id,
                'dept_id': event.dept_id,
                'user_id': event.user_id,
                'event_number': event.event_number,
                'event_name': event.event_name,
                'principal': event.principal,
                'status': '正常' if event.status == 1 else '停用',
                'start_date': str(event.start_date) if event.start_date else '',
                'end_date': str(event.end_date) if event.end_date else '',
                'notification_time': event.notification_time.strftime('%Y-%m-%d %H:%M:%S') if event.notification_time else None,
                'create_time': event.create_time.strftime('%Y-%m-%d %H:%M:%S') if event.create_time else '',
                'update_time': event.update_time.strftime('%Y-%m-%d %H:%M:%S') if event.update_time else '',
                'remark': event.remark,
                # 添加关联的名称
                'dept_name': '',
                'user_name': '',
                'principal_name': event.principal,  # 默认为原始值
            }
            
            # 尝试获取部门名称
            try:
                dept = SysDept.objects.get(id=event.dept_id)
                event_data['dept_name'] = dept.name
            except (SysDept.DoesNotExist, ValueError):
                event_data['dept_name'] = '部门不存在'
            
            # 尝试获取用户名
            try:
                user = SysUser.objects.get(id=event.user_id)
                event_data['user_name'] = user.realname
            except (SysUser.DoesNotExist, ValueError):
                event_data['user_name'] = '用户不存在'
            
            # 尝试获取负责人名称
            try:
                principal_id = int(event.principal)
                principal_user = SysUser.objects.get(id=principal_id)
                event_data['principal_name'] = principal_user.realname
            except (ValueError, SysUser.DoesNotExist, TypeError):
                # 如果principal不是有效ID或用户不存在，保持原始值
                event_data['principal_name'] = event.principal
            
            # 获取事件关联的参与人员
            event_roles = SysEventRole.objects.filter(event_id=event_id).select_related('user')
            participants = []
            for role in event_roles:
                participants.append({
                    'id': role.user.id,
                    'realname': role.user.realname,
                    'username': role.user.username
                })
            
            return JsonResponse({'code': 200, 'event': event_data, 'participants': participants})
        
        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except SysEvent.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应的事件'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取详情失败: {str(e)}'})

class AssignmentHistoryListView(View):
    """获取事件分配记录列表"""
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            page_num = data.get('pageNum', 1)
            page_size = data.get('pageSize', 10)
            query = data.get('query', '')
            event_id = data.get('event_id')

            history_queryset = SysEventAssignmentHistory.objects.all()

            if event_id:
                history_queryset = history_queryset.filter(event_id=event_id)
            
            if query:
                # 按事件名称、编号、人员姓名搜索
                history_queryset = history_queryset.filter(
                    Q(event__event_name__icontains=query) |
                    Q(event__event_number__icontains=query) |
                    Q(user__realname__icontains=query)
                )

            paginator = Paginator(history_queryset, page_size)
            page_obj = paginator.get_page(page_num)
            
            serializer = SysEventAssignmentHistorySerializer(page_obj, many=True)
            
            return JsonResponse({
                'code': 200,
                'historyList': serializer.data,
                'total': paginator.count
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})

