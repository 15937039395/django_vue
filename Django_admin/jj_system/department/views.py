# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from department.models import SysDept,SysPostSerializer

class TreeListView(View):

    # 构造菜单树
    def buildTreeMenu(self, sysDeptList):
        resultMenuList: list[SysDept] = list()
        for menu in sysDeptList:
            # 寻找子节点
            for e in sysDeptList:
                if e.pid == menu.id:
                    if not hasattr(menu, "children"):
                        menu.children = list()
                    menu.children.append(e)
            # 判断父节点，添加到集合
            if menu.pid == 0:
                resultMenuList.append(menu)
        return resultMenuList

    def get(self, request):
        postQuerySet = SysDept.objects.order_by("sort")
        # 构造菜单树
        postMenuList: list[SysDept] = self.buildTreeMenu(postQuerySet)
        serializerPostList: list[SysPostSerializer] = list()
        for sysPost in postMenuList:
            serializerPostList.append(SysPostSerializer(sysPost).data)
        return JsonResponse(
            {'code': 200, 'treeList': serializerPostList})


class SaveView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        if data['id'] == -1:  # 添加
            obj_sysDept = SysDept(name=data['name'], icon=data['code'],
                                  parent_id=data['type'], order_num=data['pid'], path=data['sort'],
                                  remark=data['remark'])
            obj_sysDept.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            obj_sysDept.save()
        else:  # 修改
            obj_sysDept = SysDept(id=data['id'], name=data['name'], icon=data['code'],
                                  parent_id=data['type'], order_num=data['pid'], path=data['sort'],
                                  remark=data['remark'], create_time=data['create_time'],
                                  update_time=data['update_time'])
            obj_sysDept.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            obj_sysDept.save()
        return JsonResponse({'code': 200})

# 菜单基本操作
class ActionView(View):

    def get(self, request):
        """
        根据id获取权限信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        post_object = SysDept.objects.get(id=id)
        return JsonResponse({'code': 200, 'menu': SysPostSerializer(post_object).data})









