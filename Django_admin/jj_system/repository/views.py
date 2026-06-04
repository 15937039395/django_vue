# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
import pytz
from django.db.models import Q
from repository.models import SysRepository,SysRepositorySerializer, RepositoryLike, RepositoryHistory, SysRepositoryComment, SysRepositoryCommentSerializer, RepositoryImage
from user.models import SysUser
from department.models import SysDept
from event.models import SysEvent, SysEventRole
from classify.models import ClassifyItem
import os
from django.conf import settings
from django.core.files.storage import default_storage
import re


class SearchView(View):
    def post(self, request):
        try:
            # 解析请求数据
            data = json.loads(request.body.decode("utf-8"))
            page_num = data['pageNum']  # 当前页（从1开始）
            page_size = data['pageSize']  # 每页条数
            # 查询参数，去除首尾空格
            query = data.get('query', '').strip()
            query_keywords = [kw.strip() for kw in query.split(',') if kw.strip()]
            # 获取当前用户ID和角色ID
            current_user_id = data.get('user_id', None)
            current_role_id = data.get('role_id', None)
            # 获取当前用户的部门ID
            current_user = request.user
            current_dept_id = current_user.dept_id if hasattr(current_user, 'dept_id') else None
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'code': 400, 'msg': f'参数错误：{str(e)}'})

        # ========== 核心修改：关键字查询逻辑与权限控制 ==========
        # 初始查询集
        repository_queryset = SysRepository.objects.all().order_by('-create_time')
        
        # 可见性权限控制：根据visibility字段过滤
        visibility_query = Q()
        if current_user_id:
            # 1. 仅自己可见的：只能看到自己创建的
            visibility_query |= (Q(visibility=1) & Q(user_id=current_user_id))
            # 2. 部门可见的：能看到同部门的
            if current_dept_id:
                visibility_query |= (Q(visibility=2) & Q(dept_id=current_dept_id))
            # 3. 全员可见的：所有人都能看
            visibility_query |= Q(visibility=3)
        else:
            # 未登录用户只能看全员可见的
            visibility_query = Q(visibility=3)
        
        repository_queryset = repository_queryset.filter(visibility_query)
        
        # 权限控制：非管理员用户只能看到自己的临时数据和所有确认的数据
        if current_role_id and current_role_id != 1:  # 非管理员用户
            # 对于非管理员用户，只查询他们自己的临时数据和所有确认的数据
            repository_queryset = repository_queryset.filter(
                Q(confirmed=True) |  # 所有确认的数据
                (Q(is_temp=True) & Q(user_id=current_user_id))  # 自己的临时数据
            )
        # 如果没有提供角色ID，假定为普通用户，应用同样限制
        elif not current_role_id:
            # 对于未提供角色ID的用户，只查询他们自己的临时数据和所有确认的数据
            repository_queryset = repository_queryset.filter(
                Q(confirmed=True) |  # 所有确认的数据
                (Q(is_temp=True) & Q(user_id=current_user_id))  # 自己的临时数据
            )

        # 如果有关键字，按部门名称/用户名过滤
        if query_keywords:
            # 初始化总查询条件（空Q对象）
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

        # 转换为字典列表
        repositorys = list(repository_page.object_list.values())
        total = paginator.count  # 优化：使用paginator.count（已过滤后的总数）

        # 批量提取关联ID（过滤空值，避免无效查询）
        dept_ids = [m['dept_id'] for m in repositorys if m.get('dept_id')]
        user_ids = [m['user_id'] for m in repositorys if m.get('user_id')]
        event_ids = [m['event_id'] for m in repositorys if m.get('event_id') and m.get('event_id') != 0]
        classify_ids = [m['classify'] for m in repositorys if m.get('classify')]

        # 批量查询关联数据（一次查询所有需要的部门、用户和事件）
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
                'principal': e.principal,  # 先存储原始值
                'event_number': e.event_number
            }
            event_map[e.id] = event_info
            # 如果principal看起来像用户ID（数字），则加入查询列表
            try:
                principal_id = int(e.principal)
                principal_ids.append(principal_id)
            except (ValueError, TypeError):
                # 如果不是数字，跳过
                pass
        
        # 批量查询负责人姓名
        principal_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=principal_ids)}

        # 补充部门名称、用户名和事件信息
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
                # 如果 principal 是数字，则尝试从用户表获取姓名
                try:
                    principal_id = int(event_info['principal'])
                    repository['principal'] = principal_map.get(principal_id, event_info['principal'])
                except (ValueError, TypeError):
                    # 如果不是数字，直接使用原始值
                    repository['principal'] = event_info['principal']
                repository['event_number'] = event_info['event_number']
            else:
                repository['event_name'] = ''
                repository['principal'] = ''
                repository['event_number'] = ''
            # 将类型数字转换为文本描述
            type_map = {
                0: '未分类',
                1: '内部事件',
                2: '外部事件',
            }
            type_value = repository.get('types', 0)
            repository['types_text'] = type_map.get(type_value, f'未知类型({type_value})')
            # 格式化事件发生时间
            if repository.get('event_occur_time'):
                repository['event_occur_time_formatted'] = str(repository['event_occur_time'])
            else:
                repository['event_occur_time_formatted'] = ''
            
            # 设置初始未点赞状态
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
                    # 如果用户ID不是有效整数，保持默认未点赞状态
                    pass

        return JsonResponse({
            'code': 200,
            'repositoryList': repositorys,
            'total': total  # 此时total是关键字过滤后的总条数
        })


# 图片上传视图
class UploadImageView(View):
    def post(self, request):
        try:
            image_file = request.FILES.get('image')
            
            if not image_file:
                return JsonResponse({'code': 400, 'msg': '没有找到上传的图片'})
            
            # 验证文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return JsonResponse({'code': 400, 'msg': '不支持的图片格式'})
            
            # 限制文件大小 (例如: 5MB)
            max_size = 5 * 1024 * 1024
            if image_file.size > max_size:
                return JsonResponse({'code': 400, 'msg': '图片大小不能超过5MB'})
            
            # 生成唯一文件名
            import uuid
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # 保存到媒体文件夹
            file_path = os.path.join('images', unique_filename)
            saved_path = default_storage.save(file_path, image_file)
            
            # 返回图片URL - 统一返回相对路径，前端自动拼接
            image_url = f"{settings.MEDIA_URL}{saved_path}"
            
            return JsonResponse({'code': 200, 'msg': '上传成功', 'url': image_url})
            
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'上传失败: {str(e)}'})




class SaveView(View):
    ADD_FLAG = -1  # 新增标识符

    def extract_images_from_content(self, content):
        """从HTML内容中提取图片URL"""
        # 匹配img标签中的src属性
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        images = re.findall(img_pattern, content)
        return images

    def save_repository_images(self, repository, content):
        """保存知识库中的图片信息到数据库"""
        try:
            # 提取内容中的所有图片URL
            image_urls = self.extract_images_from_content(content)
            
            # 删除该知识库之前的所有图片记录
            RepositoryImage.objects.filter(repository=repository).delete()
            
            # 保存新的图片记录
            for image_url in image_urls:
                try:
                    # 从URL中提取路径
                    # 假设URL格式为: http://domain/media/images/filename.ext
                    if '/media/' in image_url:
                        image_path = image_url.split('/media/')[-1]
                    else:
                        image_path = image_url
                    
                    # 获取文件大小
                    file_size = 0
                    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    if os.path.exists(full_path):
                        file_size = os.path.getsize(full_path)
                    
                    # 创建图片记录
                    RepositoryImage.objects.create(
                        repository=repository,
                        image_url=image_url,
                        image_path=image_path,
                        file_size=file_size
                    )
                except Exception as e:
                    # 记录错误但不中断流程
                    print(f"保存图片记录失败: {image_url}, 错误: {str(e)}")
                    
        except Exception as e:
            print(f"提取图片失败: {str(e)}")

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            record_id = data.get('id')
            is_temp_save = data.get('is_temp', False)  # 是否为临时保存
            
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
                    visibility=data.get('visibility', 3),  # 可见性字段，默认全员可见
                    remark=data.get('remark', ''),
                    is_temp=is_temp_save,
                    temp_version=0 if not is_temp_save else 1,
                    confirmed=False if is_temp_save else True,
                    create_time=now
                )
                obj_sys_repository.save()
                
                # 保存图片信息到数据库
                self.save_repository_images(obj_sys_repository, data['content'])
                
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
                    remarks=f"{('临时保存' if is_temp_save else '正式创建')}，版本{obj_sys_repository.temp_version}",
                )
            else:  # 修改
                obj_sys_repository = SysRepository.objects.get(id=record_id)
                
                # 获取当前操作用户信息（从请求中获取）
                current_user_id = data.get('user_id')
                # 注意：这里需要从 session 或 token 中获取当前登录用户的 role_id
                # 为了简化，我们假设前端会传递 current_role_id 字段
                current_role_id = int(data.get('current_role_id', 0))  # 转换为整数
                
                # 权限检查：
                # 1. 如果记录已确认，只有管理员可以修改
                # 2. 如果记录未确认，创建者和管理员可以修改
                if obj_sys_repository.confirmed:
                    if current_role_id != 1:
                        return JsonResponse({'code': 403, 'msg': '该记录已确认，只有管理员可以修改'})
                else:
                    # 未确认记录，检查是否为创建者或管理员
                    if current_role_id != 1 and obj_sys_repository.user_id != current_user_id:
                        return JsonResponse({'code': 403, 'msg': '您没有权限修改他人的记录'})
                
                # 保存修改前的历史记录
                if not is_temp_save and obj_sys_repository.is_temp:
                    # 从临时记录转为正式记录
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
                        remarks=f"正式修改，版本{obj_sys_repository.temp_version + 1}",
                    )
                    obj_sys_repository.temp_version += 1
                elif is_temp_save:
                    # 临时保存的修改也要记录历史
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
                        remarks=f"临时保存修改，版本{obj_sys_repository.temp_version}",
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
                obj_sys_repository.visibility = data.get('visibility', 3)  # 更新可见性
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
                    # 正式保存，标记为已确认
                    # 注意：如果记录已经确认，不要改变其状态（管理员编辑已确认记录时）
                    if not obj_sys_repository.confirmed:
                        obj_sys_repository.confirmed = True
                    obj_sys_repository.is_temp = False
                
                obj_sys_repository.save()
                
                # 保存图片信息到数据库
                self.save_repository_images(obj_sys_repository, data['content'])

            # 返回更新后的完整记录数据，避免前端重新请求列表
            return JsonResponse({
                'code': 200,
                'repository': SysRepositorySerializer(obj_sys_repository).data
            })
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
            return JsonResponse({'code': 404, 'msg': '未找到对应记录'})

    def delete(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            # 解析请求数据
            if isinstance(data, dict):
                ids = data.get('ids', [])
                user_id = data.get('user_id')  # 当前用户ID
                role_id = data.get('role_id')  # 当前用户角色ID
            elif isinstance(data, list):
                # 兼容旧的请求格式（直接传递IDs数组）
                ids = data
                user_id = None
                role_id = None
            else:
                return JsonResponse({'code': 400, 'msg': '请求数据格式错误'})
            
            if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
                raise TypeError("IDs must be a list of integers.")
            
            # 如果提供了用户信息，进行权限检查
            if user_id is not None and role_id is not None:
                # 管理员（role_id=1）可以删除任何记录
                role_id = int(role_id)  # 转换为整数
                if role_id != 1:
                    # 非管理员只能删除自己创建的未确认记录
                    records = SysRepository.objects.filter(id__in=ids)
                    for record in records:
                        if record.user_id != user_id:
                            return JsonResponse({'code': 403, 'msg': f'您没有权限删除他人的记录（ID: {record.id}）'})
                        if record.confirmed:
                            return JsonResponse({'code': 403, 'msg': f'不能删除已确认的记录（ID: {record.id}）'})
            
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


# 知识库详情查看接口
class ItemDetailView(View):
    def get(self, request):
        try:
            # 获取URL参数中的id
            item_id = int(request.GET.get("id"))
            # 查询对应的记录
            item_object = SysRepository.objects.get(id=item_id)

            # 序列化基本数据
            item_data = SysRepositorySerializer(item_object).data
            
            # 添加关联数据（部门、用户、事件、分类名称）
            # 部门名称
            dept = SysDept.objects.filter(id=item_object.dept_id).first()
            item_data['dept_name'] = dept.name if dept else ''
            
            # 用户名称
            user = SysUser.objects.filter(id=item_object.user_id).first()
            item_data['user_name'] = user.realname if user else ''
            
            # 事件信息
            if item_object.event_id and item_object.event_id != 0:
                event = SysEvent.objects.filter(id=item_object.event_id).first()
                if event:
                    item_data['event_name'] = event.event_name
                    item_data['event_number'] = event.event_number
                    # 解析负责人
                    try:
                        principal_id = int(event.principal)
                        principal_user = SysUser.objects.filter(id=principal_id).first()
                        item_data['principal'] = principal_user.realname if principal_user else event.principal
                    except (ValueError, TypeError):
                        item_data['principal'] = event.principal
                else:
                    item_data['event_name'] = ''
                    item_data['event_number'] = ''
                    item_data['principal'] = ''
            else:
                item_data['event_name'] = ''
                item_data['event_number'] = ''
                item_data['principal'] = ''
            
            # 分类名称
            if item_object.classify:
                classify = ClassifyItem.objects.filter(id=item_object.classify).first()
                item_data['classify_name'] = classify.project_number if classify else str(item_object.classify)
            else:
                item_data['classify_name'] = ''
            
            # 类型文本
            type_map = {
                0: '未分类',
                1: '内部事件',
                2: '外部事件',
            }
            item_data['types_text'] = type_map.get(item_object.types, f'未知类型({item_object.types})')
            
            # 格式化事件发生时间
            if item_object.event_occur_time:
                item_data['event_occur_time_formatted'] = str(item_object.event_occur_time)
            else:
                item_data['event_occur_time_formatted'] = ''
            
            # 状态文本
            if item_object.is_temp:
                item_data['status_text'] = '临时'
            elif item_object.confirmed:
                item_data['status_text'] = '已确认'
            else:
                item_data['status_text'] = '正常'
            
            return JsonResponse({'code': 200, 'item_data': item_data})

        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except SysRepository.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应记录'})
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
            
            # 检查用户是否已经点?
            like_record, created = RepositoryLike.objects.get_or_create(
                repository_id=repository_id,
                user_id=user_id
            )
            
            if not created:  # 如果记录已存在，说明用户要点取消?
                like_record.delete()
                repository.upvote = max(0, repository.upvote - 1)  # 点赞数减1，但不低?
                repository.save()
                return JsonResponse({'code': 200, 'msg': '取消点赞成功', 'upvote': repository.upvote, 'liked': False})
            else:  # 如果是新记录，说明用户要点赞
                repository.upvote += 1
                repository.save()
                return JsonResponse({'code': 200, 'msg': '点赞成功', 'upvote': repository.upvote, 'liked': True})
                
        except SysRepository.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应记录'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})


# 获取知识库历史记录的视图
class HistoryView(View):
    def get(self, request):
        try:
            repository_id = int(request.GET.get("id"))
            # 获取对应知识库的所有历史记?
            history_records = RepositoryHistory.objects.filter(repository_id=repository_id).order_by('-modified_time')
            
            # 构建历史记录列表
            history_list = []
            for record in history_records:
                history_entry = {
                    'id': record.id,
                    'version': record.version,
                    'remarks': record.remarks,
                    'modified_time': timezone.localtime(record.modified_time).strftime('%Y-%m-%d %H:%M:%S'),
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


# 获取知识库关联事件的视图
class AssociatedEventsView(View):
    def get(self, request):
        try:
            repository_id = int(request.GET.get("id"))
            
            # 获取知识库记录
            repository = SysRepository.objects.get(id=repository_id)
            
            # 获取关联的事件信息
            associated_events = []
            if repository.event_id and repository.event_id != 0:
                try:
                    event = SysEvent.objects.get(id=repository.event_id)
                    
                    # 获取事件负责人姓名
                    principal_name = event.principal
                    try:
                        principal_id = int(event.principal)
                        principal_user = SysUser.objects.filter(id=principal_id).first()
                        if principal_user:
                            principal_name = principal_user.realname
                    except (ValueError, TypeError):
                        # 如果principal不是数字ID，保持原始值
                        pass
                    
                    event_data = {
                        'id': event.id,
                        'event_number': event.event_number,
                        'event_name': event.event_name,
                        'principal': principal_name,
                        'start_date': str(event.start_date) if event.start_date else '',
                        'end_date': str(event.end_date) if event.end_date else '',
                        'status': '正常' if event.status == 1 else '停用',
                        'create_time': timezone.localtime(event.create_time).strftime('%Y-%m-%d %H:%M:%S') if event.create_time else '',
                    }
                    
                    # 获取事件关联的角色信息
                    event_roles = SysEventRole.objects.filter(event_id=event.id).select_related('user')
                    participants = []
                    for role in event_roles:
                        participants.append({
                            'id': role.user.id,
                            'realname': role.user.realname,
                            'username': role.user.username
                        })
                    
                    event_data['participants'] = participants
                    
                    # 获取与相同事件关联的其他知识库条目
                    related_repositories = SysRepository.objects.filter(
                        event_id=repository.event_id
                    ).exclude(id=repository_id)
                    
                    # 排除事件编号为"JJ-2026-0113-131710"（其他）的事件关联的知识库
                    try:
                        other_event = SysEvent.objects.filter(event_number='JJ-2026-0113-131710').first()
                        if other_event:
                            related_repositories = related_repositories.exclude(event_id=other_event.id)
                    except Exception:
                        pass
                    
                    related_entries = []
                    for repo in related_repositories:
                        # 通过 user_id 获取用户信息
                        try:
                            user = SysUser.objects.get(id=repo.user_id)
                            maintainer_name = user.realname
                        except SysUser.DoesNotExist:
                            maintainer_name = '未知维护人'
                        
                        related_entries.append({
                            'id': repo.id,
                            'title': repo.title,
                            'maintainer': maintainer_name,
                            'create_time': timezone.localtime(repo.create_time).strftime('%Y-%m-%d %H:%M:%S') if repo.create_time else '',
                        })
                    
                    event_data['related_entries'] = related_entries
                    associated_events.append(event_data)
                except SysEvent.DoesNotExist:
                    pass
            
            return JsonResponse({'code': 200, 'associated_events': associated_events})
        
        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except SysRepository.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应的知识库记录'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取关联事件失败: {str(e)}'})


# 评论列表视图
class CommentListView(View):
    def get(self, request):
        try:
            repository_id = request.GET.get('id')
            current_role_id = request.GET.get('role_id')
            current_user_id = request.GET.get('user_id')
            page = int(request.GET.get('page', 1))  # 页码，默认为1
            page_size = int(request.GET.get('page_size', 10))  # 每页大小，默认为10

            if not repository_id:
                return JsonResponse({'code': 400, 'msg': '缺少知识库ID'})

            # 转换为整数处理
            try:
                repository_id = int(repository_id)
                current_role_id = int(current_role_id) if current_role_id else 0
                current_user_id = int(current_user_id) if current_user_id else 0
            except (ValueError, TypeError):
                current_role_id = 0
                current_user_id = 0

            comments = SysRepositoryComment.objects.filter(repository_id=repository_id).order_by('-create_time')
            
            # 计算总数
            total_count = comments.count()
            
            # 分页处理
            paginator = Paginator(comments, page_size)
            try:
                paginated_comments = paginator.page(page)
            except Exception:
                # 页码超出范围时，返回第一页
                paginated_comments = paginator.page(1)

            # 获取该知识库条目的维护人（创建人）ID
            try:
                repo = SysRepository.objects.get(id=repository_id)
                maintainer_id = repo.user_id
            except SysRepository.DoesNotExist:
                maintainer_id = None

            # 检查当前用户是否有权查看所有评论人
            can_view_all = False
            if current_role_id == 1:
                can_view_all = True
            elif current_user_id:
                try:
                    current_user = SysUser.objects.get(id=current_user_id)
                    if current_user.can_view_commenter == 1:
                        can_view_all = True
                except SysUser.DoesNotExist:
                    pass

            # 批量获取所有涉及的用户姓名（评论人和被回复人）
            user_ids = set()
            for c in paginated_comments:
                user_ids.add(c.user_id)
                if c.reply_to_user_id:
                    user_ids.add(c.reply_to_user_id)
            
            user_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=list(user_ids))}

            comment_list = []
            for comment in paginated_comments:
                data = SysRepositoryCommentSerializer(comment).data
                
                # 处理评论人姓名
                realname = user_map.get(comment.user_id, '未知用户')
                # 显示全名的条件：
                # 1. 管理员 或 被授权人员 (can_view_all)
                # 2. 评论者本人
                # 3. 维护人（创建者）给当前用户回复时，当前用户可以看到维护人的名字
                is_maintainer_reply = (maintainer_id and comment.user_id == maintainer_id and comment.reply_to_user_id == current_user_id)
                
                if can_view_all or comment.user_id == current_user_id or is_maintainer_reply:
                    data['user_name'] = realname
                else:
                    data['user_name'] = "***"
                
                # 处理被回复人姓名
                if comment.reply_to_user_id:
                    reply_realname = user_map.get(comment.reply_to_user_id, '未知用户')
                    # 显示被回复人全名的条件：
                    # 1. 管理员 或 被授权人员 (can_view_all)
                    # 2. 被回复者本人
                    # 3. 当前用户正在给维护人回复时，可以看到维护人的名字
                    is_reply_to_maintainer = (maintainer_id and comment.reply_to_user_id == maintainer_id and comment.user_id == current_user_id)
                    
                    if can_view_all or comment.reply_to_user_id == current_user_id or is_reply_to_maintainer:
                        data['reply_to_user_name'] = reply_realname
                    else:
                        data['reply_to_user_name'] = "***"
                else:
                    data['reply_to_user_name'] = None

                comment_list.append(data)

            return JsonResponse({
                'code': 200, 
                'comment_list': comment_list,
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})


# 提交评论视图
class CommentSubmitView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            repository_id = data.get('id')
            user_id = data.get('user_id')
            content = data.get('content')
            parent_id = data.get('parent_id')
            reply_to_user_id = data.get('reply_to_user_id')

            if not all([repository_id, user_id, content]):
                return JsonResponse({'code': 400, 'msg': '缺少必要字段'})

            comment = SysRepositoryComment.objects.create(
                repository_id=repository_id,
                user_id=user_id,
                content=content,
                parent_id=parent_id,
                reply_to_user_id=reply_to_user_id
            )

            return JsonResponse({
                'code': 200,
                'msg': '评论成功',
                'comment': SysRepositoryCommentSerializer(comment).data
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})


# 获取知识库图片列表视图
class RepositoryImagesView(View):
    def get(self, request):
        """获取指定知识库的所有图片信息"""
        try:
            repository_id = int(request.GET.get("id"))
            
            # 查询该知识库的所有图片
            images = RepositoryImage.objects.filter(repository_id=repository_id).order_by('-upload_time')
            
            image_list = []
            for img in images:
                image_list.append({
                    'id': img.id,
                    'image_url': img.image_url,
                    'image_path': img.image_path,
                    'file_size': img.file_size,
                    'file_size_mb': round(img.file_size / (1024 * 1024), 2),  # 转换为MB
                    'upload_time': timezone.localtime(img.upload_time).strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return JsonResponse({
                'code': 200,
                'images': image_list,
                'total': len(image_list)
            })
        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'msg': '无效的ID'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})
