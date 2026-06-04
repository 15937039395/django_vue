# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View

from post.models import SysPost,SysPostSerializer



class SearchView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pageNum = data['pageNum']  # 当前页
        pageSize = data['pageSize']  # 每页大小
        query = data['query']  # 查询参数
        postListPage = Paginator(SysPost.objects.filter(name__icontains=query), pageSize).page(pageNum)
        obj_posts = postListPage.object_list.values()  # 转成字典
        posts = list(obj_posts)  # 把外层的容器转成List
        total = SysPost.objects.filter(name__icontains=query).count()

        return JsonResponse({'code': 200, 'postList': posts, 'total': total})

class SaveView(View):
    def post(self, request):

        try:
            data = json.loads(request.body.decode("utf-8"))
            if data['id'] == -1:  # 添加
                # 创建新记录
                obj_sysPost = SysPost(
                    name=data['name'],
                )

                obj_sysPost.save()
                return JsonResponse({'code': 200, 'msg': '新增成功'})
            else:
                # 先查询再更新
                obj_sysPost = SysPost(id=data['id'],name=data['name'])
                obj_sysPost.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                obj_sysPost.save()
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
        post_object = SysPost.objects.get(id=id)
        return JsonResponse({'code': 200, 'post': SysPostSerializer(post_object).data})

        # 删除功能

    def delete(self, request):
        try:
            # 解析前端传递的id数组（如[1,2,3]）
            ids = json.loads(request.body.decode("utf-8"))
            # 使用id__in批量删除
            SysPost.objects.filter(id__in=ids).delete()  # 关键：用id__in
            return JsonResponse({'code': 200, 'msg': '删除成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})  # 这里会返回具体错误



