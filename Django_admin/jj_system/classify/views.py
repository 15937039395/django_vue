# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.shortcuts import render
import json
from datetime import datetime
from io import BytesIO
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views import View
from classify.models import ClassifyItem,SysPostSerializer


class SearchView(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pageNum = data['pageNum']  # 当前页
        pageSize = data['pageSize']  # 每页大小
        query = data['query']  # 查询参数
        # 关键修复：添加 order_by('-id') 按ID倒序，新增数据排在前面
        classify_queryset = ClassifyItem.objects.filter(project_number__icontains=query).order_by('-id')
        ClassifyListPage = Paginator(classify_queryset, pageSize).page(pageNum)
        obj_Classifys = ClassifyListPage.object_list.values()  # 转成字典
        Classifys = list(obj_Classifys)  # 把外层的容器转成List
        total = classify_queryset.count()

        return JsonResponse({'code': 200, 'classify_List': Classifys, 'total': total})

class SaveView(View):
    def post(self, request):

        try:
            data = json.loads(request.body.decode("utf-8"))
            if data['id'] == -1:  # 添加
                # 创建新记录
                obj_ClassifyItem = ClassifyItem(
                    project_number=data['project_number'],
                    types=data['types'],
                )
                obj_ClassifyItem.save()
                return JsonResponse({'code': 200, 'msg': '新增成功'})
            else:
                # 先查询再更新，保持创建时间不变
                obj_ClassifyItem = ClassifyItem.objects.get(id=data['id'])
                obj_ClassifyItem.project_number = data['project_number']
                obj_ClassifyItem.types = data['types']
                obj_ClassifyItem.save()
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
        try:
            Classif_object = ClassifyItem.objects.get(id=id)
            return JsonResponse({'code': 200, 'item': SysPostSerializer(Classif_object).data})
        except ClassifyItem.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '数据不存在'}, status=404)


    def delete(self, request):
        try:
            # 解析前端传递的id数组（如[1,2,3]）
            ids = json.loads(request.body.decode("utf-8"))
            # 使用id__in批量删除
            ClassifyItem.objects.filter(id__in=ids).delete()  # 关键：用id__in
            return JsonResponse({'code': 200, 'msg': '删除成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})  # 这里会返回具体错误


class ClassifyListView(View):
    def get(self, request):
        try:
            classify_list = list(ClassifyItem.objects.all().values('id', 'project_number'))
            return JsonResponse({'code': 200, 'data': classify_list})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})


