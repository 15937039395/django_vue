# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View

from level.models import SysLevel, SysLevelSerializer

class SearchView(View):

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            page_num = int(data.get('pageNum', 1))  # 默认第一页
            page_size = int(data.get('pageSize', 10))  # 默认每页10条
            query = str(data.get('query', '')).strip()

            if not (1 <= page_num <= 99999 and 1 <= page_size <= 100):
                return JsonResponse({'code': 400, 'msg': '参数超出范围'})

            queryset = SysLevel.objects.filter(name__icontains=query)
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.page(page_num)

            levels = list(page_obj.object_list.values())
            total = paginator.count

            return JsonResponse({
                'code': 200,
                'levelList': levels,
                'total': total
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '服务器内部错误'})


class SaveView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            level_id = data.get('id')
            name = data.get('name')

            if not isinstance(name, str) or len(name.strip()) == 0:
                return JsonResponse({'code': 400, 'msg': '名称不能为空'})

            if level_id == -1:
                # 新增
                obj_sysLevel = SysLevel(name=name.strip())
                obj_sysLevel.save()
                return JsonResponse({'code': 200, 'msg': '新增成功'})
            else:
                # 更新
                try:
                    obj_sysLevel = SysLevel.objects.get(id=level_id)
                except SysLevel.DoesNotExist:
                    return JsonResponse({'code': 404, 'msg': '记录不存在'})

                obj_sysLevel.name = name.strip()
                obj_sysLevel.update_time = datetime.now()  # 直接赋值 datetime 对象
                obj_sysLevel.save()
                return JsonResponse({'code': 200, 'msg': '更新成功'})
        except ValueError:
            return JsonResponse({'code': 400, 'msg': '请求参数非法'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '操作失败，请稍后再试'})


class ActionView(View):

    def get(self, request):
        try:
            level_id = request.GET.get("id")
            if not level_id or not level_id.isdigit():
                return JsonResponse({'code': 400, 'msg': '无效的ID'})

            level_object = SysLevel.objects.get(id=int(level_id))
            serialized_data = SysLevelSerializer(level_object).data
            return JsonResponse({'code': 200, 'level': serialized_data})
        except SysLevel.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '未找到对应记录'})
        except Exception:
            return JsonResponse({'code': 500, 'msg': '系统异常'})

    def delete(self, request):
        try:
            ids = json.loads(request.body.decode("utf-8"))
            if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
                return JsonResponse({'code': 400, 'msg': '参数必须为整数列表'})

            count, _ = SysLevel.objects.filter(id__in=ids).delete()
            return JsonResponse({'code': 200, 'msg': f'成功删除 {count} 条记录'})
        except Exception:
            return JsonResponse({'code': 500, 'msg': '删除失败'})
