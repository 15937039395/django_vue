# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
import pytz
from django.db.models import Q
from repository.models import SysRepository,SysRepositorySerializer, RepositoryLike, RepositoryHistory
from user.models import SysUser
from department.models import SysDept
from event.models import SysEvent
from classify.models import ClassifyItem


class SearchView(View):
    def post(self, request):
        try:
            # 解析请求数据
            data = json.loads(request.body.decode("utf-8"))
            page_num = data['pageNum']  # 当前页（假设�?开始）
            page_size = data['pageSize']  # 每页条数
            # 查询参数，去除首尾空�?
            query = data.get('query', '').strip()
            query_keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
            # 获取当前用户ID
            current_user_id = data.get('user_id', None)
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'code': 400, 'msg': f'参数错误：{str(e)}'})

        # ========== 核心修改：关键字查询逻辑 ==========
        # 初始查询�?
        repository_queryset = SysRepository.objects.all().order_by('-create_time')

        # 如果有关键字，按部门名称/用户名过�?
        if query_keywords:
            # 初始化总查询条件（空Q对象�?
            total_query = Q()
            for keyword in query_keywords:
                # 1. 根据当前关键词模糊匹配部门名称，获取匹配的dept_id
                match_dept_ids = SysDept.objects.filter(
                    name__icontains=keyword
                ).values_list('id', flat=True)

                # 2. 根据当前关键词模糊匹配用户名，获取匹配的user_id
                match_user_ids = SysUser.objects.filter(
                    realname__icontains=keyword  # 按实际用户名字段调整
                ).values_list('id', flat=True)

                # 构建当前关键词的匹配条件：任一字段匹配即可
                keyword_query = (
                        Q(dept_id__in=match_dept_ids) |  # 部门ID匹配
                        Q(user_id__in=match_user_ids) |  # 用户ID匹配
                        Q(types__icontains=keyword) |  # types字段模糊匹配
                        Q(classify__icontains=keyword) |  # classify字段模糊匹配
                        Q(title__icontains=keyword) |  # title字段模糊匹配
                        Q(content__icontains=keyword)  # content字段模糊匹配
                )

                # 多关键词之间用OR关联（满足任意一个关键词的匹配条件即可）
                total_query |= keyword_query

                # 应用最终的查询条件
            repository_queryset = repository_queryset.filter(total_query)
        # ===========================================

        # 分页处理
        paginator = Paginator(repository_queryset, page_size)

        try:
            repository_page = paginator.page(page_num)
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': f'分页错误：{str(e)}'})

        # 转换为字典列�?
        repositorys = list(repository_page.object_list.values())
        total = paginator.count  # 优化：使用paginator.count（已过滤后的总数�?

        # 批量提取关联ID（过滤空值，避免无效查询�?
        dept_ids = [m['dept_id'] for m in repositorys if m.get('dept_id')]
        user_ids = [m['user_id'] for m in repositorys if m.get('user_id')]
        event_ids = [m['event_id'] for m in repositorys if m.get('event_id') and m.get('event_id') != 0]
        classify_ids = [m['classify'] for m in repositorys if m.get('classify')]

        # 批量查询关联数据（一次查询所有需要的部门、用户和事件�?
        dept_map = {d.id: d.name for d in SysDept.objects.filter(id__in=dept_ids)}
        user_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=user_ids)}
        event_list = list(SysEvent.objects.filter(id__in=event_ids))
        # 查询分类名称
        classify_map = {c.id: c.project_number for c in ClassifyItem.objects.filter(id__in=classify_ids)}
        
        # 创建事件映射并处理负责人信息
        event_map = {}
        principal_ids = []  # 收集可能是用户ID的负责人ID
        for e in event_list:
            event_info = {
                'event_name': e.event_name,
                'principal': e.principal,  # 先存储原始�?
                'event_number': e.event_number
            }
            event_map[e.id] = event_info
            # 如果principal看起来像用户ID（数字），则加入查询列表
            try:
                principal_id = int(e.principal)
                principal_ids.append(principal_id)
            except (ValueError, TypeError):
                # 如果不是数字，跳�?
                pass
        
        # 批量查询负责人姓�?
        principal_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=principal_ids)}

        # 补充部门名称、用户名和事件信�?
        for repository in repositorys:
            repository['dept_name'] = dept_map.get(repository.get('dept_id'), '')
            repository['user_name'] = user_map.get(repository.get('user_id'), '')
            # 添加分类名称
            classify_id = repository.get('classify')
            if classify_id:
                repository['classify_name'] = classify_map.get(classify_id, str(classify_id))  # 如果找不到分类名称，显示ID
            else:
                repository['classify_name'] = ''
            event_info = event_map.get(repository.get('event_id'))
            if event_info:
                repository['event_name'] = event_info['event_name']
                # 如果principal是数字，则尝试从用户表获取姓�?
                try:
                    principal_id = int(event_info['principal'])
                    repository['principal'] = principal_map.get(principal_id, event_info['principal'])
                except (ValueError, TypeError):
                    # 如果不是数字，直接使用原始�?
                    repository['principal'] = event_info['principal']
                repository['event_number'] = event_info['event_number']
            else:
                repository['event_name'] = ''
                repository['principal'] = ''
                repository['event_number'] = ''
            # 将类型数字转换为文本描述
            type_map = {
                0: '未分�?,
                1: '内部事件',
                2: '外部事件',
            }
            type_value = repository.get('types', 0)
            repository['types_text'] = type_map.get(type_value, f'未知类型({type_value})')
            # 格式化事件发生时�?
            if repository.get('event_occur_time'):
                repository['event_occur_time_formatted'] = str(repository['event_occur_time'])
            else:
                repository['event_occur_time_formatted'] = ''
            
            # 设置初始未点赞状�?
            repository['user_liked'] = False
            
            # 如果提供了当前用户ID，检查用户是否已点赞
            if current_user_id:
                try:
                    user_id_int = int(current_user_id)
                    liked = RepositoryLike.objects.filter(
                        repository_id=repository['id'],
                        user_id=user_id_int
                    ).exists()
                    repository['user_liked'] = liked
                except (ValueError, TypeError):
                    # 如果用户ID不是有效整数，保持默认未点赞状�?
                    pass

        return JsonResponse({
            'code': 200,
            'repositoryList': repositorys,
            'total': total  # 此时total是关键字过滤后的总条�?
        })


class SaveView(View):
    ADD_FLAG = -1  # 新增标识�?

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            record_id = data.get('id')
            is_temp_save = data.get('is_temp', False)  # 是否为临时保�?
            
            now = timezone.localtime(timezone.now())

            if record_id == self.ADD_FLAG:  # 添加
                obj_sys_repository = SysRepository(
                    dept_id=data['dept_id'],
                    user_id=data['user_id'],
                    event_id=data.get('event_id', 0),
                    event_occur_time=data.get('event_occur_time'),
                    address=data.get('address', ''),
                    types=data['types'],
                    classify=data['classify'],
                    title=data['title'],
                    content=data['content'],
                    remark=data.get('remark', ''),
                    is_temp=is_temp_save,
                    temp_version=0 if not is_temp_save else 1,
                    create_time=now
                )
                obj_sys_repository.save()
                
                # 记录历史记录
                RepositoryHistory.objects.create(
                    repository=obj_sys_repository,
                    dept_id=obj_sys_repository.dept_id,
                    user_id=obj_sys_repository.user_id,
                    event_id=obj_sys_repository.event_id,
                    event_occur_time=obj_sys_repository.event_occur_time,
                    address=obj_sys_repository.address,
                    types=obj_sys_repository.types,
                    classify=obj_sys_repository.classify,
                    title=obj_sys_repository.title,
                    content=obj_sys_repository.content,
                    upvote=obj_sys_repository.upvote,
                    version=obj_sys_repository.temp_version,
                    remarks=f"{('临时保存' if is_temp_save else '正式创建')}，版�?{obj_sys_repository.temp_version}",
                )
            else:  # 修改
                obj_sys_repository = SysRepository.objects.get(id=record_id)
                
                # 检查是否已确认，如果已确认则不允许修改
                if obj_sys_repository.confirmed:
                    return JsonResponse({'code': 400, 'msg': '该记录已确认，无法修�?})
                
                # 保存修改前的历史记录
                if not is_temp_save and obj_sys_repository.is_temp:
                    # 从临时记录转为正式记�?
                    obj_sys_repository.temp_version += 1
                    obj_sys_repository.is_temp = False
                    obj_sys_repository.confirmed = False
                    
                    # 创建历史记录
                    RepositoryHistory.objects.create(
                        repository=obj_sys_repository,
                        dept_id=data['dept_id'],
                        user_id=data['user_id'],
                        event_id=data.get('event_id', 0),
                        event_occur_time=data.get('event_occur_time'),
                        address=data.get('address', ''),
                        types=data['types'],
                        classify=data['classify'],
                        title=data['title'],
                        content=data['content'],
                        upvote=obj_sys_repository.upvote,
                        version=obj_sys_repository.temp_version,
                        remarks=f"临时保存转正式记录，版本 {obj_sys_repository.temp_version}",
                    )
                elif not is_temp_save:
                    # 正常的正式修改，创建历史记录
                    RepositoryHistory.objects.create(
                        repository=obj_sys_repository,
                        dept_id=data['dept_id'],
                        user_id=data['user_id'],
                        event_id=data.get('event_id', 0),
                        event_occur_time=data.get('event_occur_time'),
                        address=data.get('address', ''),
                        types=data['types'],
                        classify=data['classify'],
                        title=data['title'],
                        content=data['content'],
                        upvote=obj_sys_repository.upvote,
                        version=obj_sys_repository.temp_version + 1,
                        remarks=f"正式修改，版�?{obj_sys_repository.temp_version + 1}",
                    )
                    obj_sys_repository.temp_version += 1
                elif is_temp_save:
                    # 临时保存的修改也要记录历�?
                    obj_sys_repository.temp_version += 1
                    RepositoryHistory.objects.create(
                        repository=obj_sys_repository,
                        dept_id=data['dept_id'],
                        user_id=data['user_id'],
                        event_id=data.get('event_id', 0),
                        event_occur_time=data.get('event_occur_time'),
                        address=data.get('address', ''),
                        types=data['types'],
                        classify=data['classify'],
                        title=data['title'],
                        content=data['content'],
                        upvote=obj_sys_repository.upvote,
                        version=obj_sys_repository.temp_version,
                        remarks=f"临时保存修改，版�?{obj_sys_repository.temp_version}",
                    )
                
                # 更新字段
                obj_sys_repository.dept_id = data['dept_id']
                obj_sys_repository.user_id = data['user_id']
                obj_sys_repository.event_id = data.get('event_id', 0)
                obj_sys_repository.event_occur_time = data.get('event_occur_time')
                obj_sys_repository.address = data.get('address', '')
                obj_sys_repository.types = data['types']
                obj_sys_repository.classify = data['classify']
                obj_sys_repository.title = data['title']
                obj_sys_repository.content = data['content']
                obj_sys_repository.remark = data.get('remark', '')
                obj_sys_repository.update_time = now
                
                # 如果是临时保存，标记为临时状态；否则标记为已确认
                if is_temp_save:
                    obj_sys_repository.is_temp = True
                    if obj_sys_repository.temp_version == 0:
                        obj_sys_repository.temp_version = 1
                    else:
                        obj_sys_repository.temp_version += 1
                else:
                    # 正式保存，标记为已确�?
                    obj_sys_repository.confirmed = True
                    obj_sys_repository.is_temp = False
                
                obj_sys_repository.save()

            return JsonResponse({'code': 200})
        except KeyError as e:
            return JsonResponse({'code': 400, 'msg': f'缺少必要字段: {e}'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})



class ActionView(View):
    def get(self, request):
        try:
            record_id = int(request.GET.get("id"))
            repository_object = SysRepository.objects.get(id=record_id)
            return JsonResponse({'code': 200, 'repository': SysRepositorySerializer(repository_object).data})
        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except SysRepository.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应记�?'})

    def delete(self, request):
        try:
            ids = json.loads(request.body.decode("utf-8"))
            if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
                raise TypeError("IDs must be a list of integers.")
            SysRepository.objects.filter(id__in=ids).delete()
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


# 在items/views.py中添加详情查看接�?
class ItemDetailView(View):
    def get(self, request):
        try:
            # 获取URL参数中的id

            item_id = int(request.GET.get("id"))
            # 查询对应的记�?
            item_object = SysRepository.objects.get(id=item_id)

            import logging
            logging.info(f'知识库详情结果: {item_object}')
            # # 将查询结果转换为字典（如果没有序列化器）
            # item_data = {
            #     'id': item_object.id,
            #     'project_number': item_object.project_number,
            # }
            # print('>>>',item_data)
            return JsonResponse({'code': 200, 'item_data': SysRepositorySerializer(item_object).data})

        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except SysRepository.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应记�?'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取详情失败: {str(e)}'})


class LikeView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            repository_id = data.get('id')
            user_id = data.get('user_id')  # 获取当前用户ID
            
            if not repository_id:
                return JsonResponse({'code': 400, 'msg': '缺少知识库ID'})
            if not user_id:
                return JsonResponse({'code': 400, 'msg': '缺少用户ID'})
                
            repository = SysRepository.objects.get(id=repository_id)
            
            # 检查用户是否已经点�?
            like_record, created = RepositoryLike.objects.get_or_create(
                repository_id=repository_id,
                user_id=user_id
            )
            
            if not created:  # 如果记录已存在，说明用户要点取消�?
                like_record.delete()
                repository.upvote = max(0, repository.upvote - 1)  # 点赞数减1，但不低�?
                repository.save()
                return JsonResponse({'code': 200, 'msg': '取消点赞成功', 'upvote': repository.upvote, 'liked': False})
            else:  # 如果是新记录，说明用户要点赞
                repository.upvote += 1
                repository.save()
                return JsonResponse({'code': 200, 'msg': '点赞成功', 'upvote': repository.upvote, 'liked': True})
                
        except SysRepository.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应记�?'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})


# 获取知识库历史记录的视图
class HistoryView(View):
    def get(self, request):
        try:
            repository_id = int(request.GET.get("id"))
            # 获取对应知识库的所有历史记�?
            history_records = RepositoryHistory.objects.filter(repository_id=repository_id).order_by('-modified_time')
            
            # 构建历史记录列表
            history_list = []
            for record in history_records:
                history_entry = {
                    'id': record.id,
                    'version': record.version,
                    'remarks': record.remarks,
                    'modified_time': record.modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'dept_id': record.dept_id,
                    'user_id': record.user_id,
                    'event_id': record.event_id,
                    'event_occur_time': str(record.event_occur_time) if record.event_occur_time else '',
                    'address': record.address,
                    'types': record.types,
                    'classify': record.classify,
                    'title': record.title,
                    'content': record.content[:100] + '...' if len(record.content) > 100 else record.content,  # 限制内容长度
                    'upvote': record.upvote,
                }
                history_list.append(history_entry)
            
            return JsonResponse({'code': 200, 'history_list': history_list})
        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})
