# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.shortcuts import render

from django.shortcuts import render
import json
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View

from manhour.models import SysManhour, SysManhourSerializer
from user.models import SysUser
from items.models import SysItem,SysPostSerializer


class SearchView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pageNum = data['pageNum']  # 当前页
        pageSize = data['pageSize']  # 每页大小
        query = data['query']  # 查询参数
        # 关键修复：添加 order_by('-id') 按ID倒序，新增数据排在前面
        item_queryset = SysItem.objects.filter(project_number__icontains=query).order_by('-id')
        itemsListPage = Paginator(item_queryset, pageSize).page(pageNum)

        obj_itemss = itemsListPage.object_list.values()  # 转成字典
        itemss = list(obj_itemss)  # 把外层的容器转成List
        total = item_queryset.count()

        # 查询用户名
        user_ids = [item['user_id'] for item in itemss if item.get('user_id')]
        user_map = {u.id: u.realname for u in SysUser.objects.filter(id__in=user_ids)}
        for item in itemss:
            item['user_name'] = user_map.get(item.get('user_id'), '')

        return JsonResponse({'code': 200, 'itemsList': itemss, 'total': total})

class SaveView(View):
    def post(self, request):

        try:
            data = json.loads(request.body.decode("utf-8"))
            if data['id'] == -1:  # 添加
                # 创建新记录
                obj_sysItem = SysItem(
                    project_number=data['project_number'],
                    user_id=data.get('user_id', 0),
                )
                obj_sysItem.save()
                return JsonResponse({'code': 200, 'msg': '新增成功'})
            else:
                # 先查询再更新
                obj_sysItem = SysItem(id=data['id'], project_number=data['project_number'])
                obj_sysItem.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                obj_sysItem.save()
                return JsonResponse({'code': 200, 'msg': '更新成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'操作失败：{str(e)}'})

class ActionView(View):

    def get(self, request):
        """
        根据id获取权限信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        items_object = SysItem.objects.get(id=id)
        return JsonResponse({'code': 200, 'item': SysPostSerializer(items_object).data})

        # 删除功能

    def delete(self, request):
        try:
            # 解析前端传递的id数组（如[1,2,3]）
            ids = json.loads(request.body.decode("utf-8"))
            # 使用id__in批量删除
            SysItem.objects.filter(id__in=ids).delete()  # 关键：用id__in
            return JsonResponse({'code': 200, 'msg': '删除成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})  # 这里会返回具体错误