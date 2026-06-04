# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from datetime import datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from role.models import SysRole, SysUserRole
from user.models import SysUser, SysUserSerializer
from menu.models import SysMenu, SysMenuSerializer
from django.utils import timezone
from level.models import SysLevel
from collections import defaultdict
from post.models import SysPost
import pytz
from jj_system import settings
from department.models import SysDept
from common.data_permission import DataPermissionUtil
from common.decorators import get_user_permissions

User = get_user_model()



class TreeListView(View):
    def build_dept_user_tree(self):
        """
        构建「部门-用户」树状结构
        返回格式：部门节点作为父节点，下属用户作为子节点（无多级部门，可扩展）
        """
        # 步骤1：查询所有用户（按sort排序，优化性能），转换为列表
        user_queryset = SysUser.objects.order_by("sort").all()
        user_list = list(user_queryset)  # 转换为列表，避免多次查询数据库

        # 步骤2：按dept_id分组用户（key=dept_id，value=该部门下的用户列表）
        dept_user_map = defaultdict(list)
        for user in user_list:
            dept_id = user.dept_id or 0  # 处理dept_id为NULL的情况，默认归类到0号部门
            dept_user_map[dept_id].append(user)

        # 步骤3：定义部门映射表（真实部门ID与部门名称对应）
        dept_map = {d.id: d.name for d in SysDept.objects.filter()}

        # 步骤4：构建树状结构（部门节点 + 下属用户节点）
        dept_user_tree = []
        for dept_id, user_list in dept_user_map.items():

            # 3.1 构建部门节点（核心：匹配真实部门名称，区分部门和用户节点）
            dept_node = {
                "node_type": "dept",  # 节点类型：部门（用于前端区分渲染）
                "dept_id": dept_id,
                # 关键优化：从dept_map中匹配真实部门名称，处理边界情况
                "dept_name": self._get_real_dept_name(dept_id, dept_map),
                "children": []  # 子节点：挂载该部门下的所有用户
            }


            # 3.2 为部门节点挂载下属用户（序列化用户信息）
            for user in user_list:
                user_serializer = SysUserSerializer(user)
                user_node = {
                    "node_type": "user",  # 节点类型：用户（用于前端区分渲染）
                    **user_serializer.data  # 合并用户所有字段（解包序列化结果）
                }
                dept_node["children"].append(user_node)

            # 3.3 将部门节点加入树状结构
            dept_user_tree.append(dept_node)

        # 步骤4：（可选）若需要多级部门（需有部门表sys_dept，含parent_id），可在此扩展部门层级
        # 此处先实现平级部门，如需多级可参考后续扩展说明

        return dept_user_tree

    def _get_real_dept_name(self, dept_id, dept_map):
        """
        辅助方法：根据部门ID获取真实部门名称，处理边界情况
        :param dept_id: 部门ID（可能为0，对应未分配部门）
        :param dept_map: 部门ID-名称映射表
        :return: 真实部门名称
        """
        # 情况1：dept_id=0，对应未分配部门
        if dept_id == 0:
            return "未分配部门"
        # 情况2：dept_id在映射表中，返回对应真实名称
        if dept_id in dept_map:
            return dept_map[dept_id]
        # 情况3：dept_id无效（不在映射表中），返回默认提示
        return f"未知部门（ID：{dept_id}）"

    def get(self, request):
        try:
            # 构建部门-用户树
            dept_user_tree = self.build_dept_user_tree()

            return JsonResponse(
                {'code': 200, 'msg': '查询成功', 'treeList': dept_user_tree},
                json_dumps_params={'ensure_ascii': False}  # 解决中文乱码
            )
        except Exception as e:
            return JsonResponse(
                {'code': 500, 'msg': f'查询失败：{str(e)}', 'treeList': []}
            )


class CurrentUserView(View):
    """获取当前登录用户信息"""

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return JsonResponse({'code': 401, 'msg': '用户未登录'})

            user = request.user
            # 获取部门信息
            dept = SysDept.objects.filter(id=user.dept_id).first()

            user_data = {
                'id': user.id,
                'username': user.username,
                'realname': user.realname,
                'dept_id': user.dept_id,
                'departmentName': dept.name if dept else ''
            }

            return JsonResponse({
                'code': 200,
                'user': user_data
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取用户信息失败: {str(e)}'})


class LoginView(View):

    def buildTreeMenu(self, sysMenuList):
        # 先过滤掉按钮类型的菜单（menu_type='F'），只保留目录和菜单
        sysMenuList = [menu for menu in sysMenuList if menu.menu_type != 'F']
        
        resultMenuList: list[SysMenu] = list()
        for menu in sysMenuList:
            # 寻找子节点
            for e in sysMenuList:
                if e.parent_id == menu.id:
                    if not hasattr(menu, "children"):
                        menu.children = list()
                    menu.children.append(e)
            # 判断父节点，添加到集合
            if menu.parent_id == 0:
                resultMenuList.append(menu)
        return resultMenuList

    def post(self, request):
        # 支持从GET参数或POST body中获取用户名和密码
        username = request.GET.get("username") or (json.loads(request.body.decode("utf-8")).get("username") if request.body else None)
        password = request.GET.get("password") or (json.loads(request.body.decode("utf-8")).get("password") if request.body else None)
        
        import logging
        logging.info(f'登录请求 - 用户名: {username}, 请求方法: {request.method}')
        
        if not username or not password:
            logging.warning('登录失败 - 缺少用户名或密码')
            return JsonResponse({'code': 500, 'info': '用户名或密码不能为空！'})
        
        try:
            # 先通过用户名查找用户
            user = SysUser.objects.get(username=username)
            logging.info(f'找到用户: {username}, 用户ID: {user.id}, 用户状态: {user.status}')
            
            # 直接比较明文密码
            password_valid = (user.password == password)
            logging.info(f'密码验证结果: {password_valid}')
            
            if not password_valid:
                logging.warning(f'登录失败 - 用户 {username} 密码错误')
                return JsonResponse({'code': 500, 'info': '用户名或者密码错误！'})
            
            # 新增：检查用户状态是否为禁用（状态：1-正常 2-禁用）
            if user.status == 2:
                logging.warning(f'登录失败 - 用户 {username} 已被禁用')
                return JsonResponse({'code': 500, 'info': '该账号已被禁用，请联系管理员！'})
            
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            # 将用户对象传递进去，获取到该对象的属性值

            # 使用Django ORM替代原始SQL查询，防止SQL注入
            user_role_ids = SysUserRole.objects.filter(user_id=user.id).values_list('role_id', flat=True)
            roleList = SysRole.objects.filter(id__in=user_role_ids)

            # 获取当前用户所有的角色，逗号隔开
            roles = ",".join([role.name for role in roleList])

            menuSet: set[SysMenu] = set()
            for row in roleList:
                # 使用Django ORM替代原始SQL查询，防止SQL注入
                menu_ids = SysMenu.objects.filter(sysrolemenu__role_id=row.id).values_list('id', flat=True)
                menuList = SysMenu.objects.filter(id__in=menu_ids)
                for row2 in menuList:
                    menuSet.add(row2)

            menuList: list[SysMenu] = list(menuSet) #set转list
            sorted_menuList = sorted(menuList, key=lambda x: x.order_num if x.order_num is not None else 9999) #根据order_num排序
            # 构造菜单树
            sysMenuList: list[SysMenu] = self.buildTreeMenu(sorted_menuList)

            serializerMenuList = list()
            for sysMenu in sysMenuList:
                serializerMenuList.append(SysMenuSerializer(sysMenu).data)
            
            # 获取用户的第一个角色ID（假设用户至少有一个角色）
            user_data = SysUserSerializer(user).data
            # 从 sys_user_role 表中获取用户的第一个 role_id
            user_role = SysUserRole.objects.filter(user_id=user.id).first()
            if user_role:
                user_data['role_id'] = user_role.role_id
            else:
                user_data['role_id'] = None  # 如果没有角色，设置为 None
            
            # 获取用户权限列表（按钮权限）
            permissions = list(get_user_permissions(user))
            
            return JsonResponse(
                {'code': 200, 'token': token, 'user': user_data, 'info': '登录成功', 'roles': roles,
                 'menuList': serializerMenuList, 'permissions': permissions})
                
        except SysUser.DoesNotExist:
            import logging
            logging.warning(f'登录失败 - 用户不存在: {username}')
            return JsonResponse({'code': 500, 'info': '用户名或者密码错误！'})
        except json.JSONDecodeError:
            import logging
            logging.warning('登录失败 - JSON解析错误')
            return JsonResponse({'code': 500, 'info': '请求参数格式错误！'})
        except Exception as e:
            import logging
            logging.exception(f'登录过程中发生错误: {str(e)}')  # 记录异常日志
            return JsonResponse({'code': 500, 'info': f'登录失败: {str(e)}'})


class TestView(View):

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token != None and token != '':
            userList_obj = SysUser.objects.all()
            userList_dict = userList_obj.values()  # 转存字典
            userList = list(userList_dict)  # 把外层的容器转存List
            return JsonResponse({'code': 200, 'info': '测试！', 'data': userList})
        else:
            return JsonResponse({'code': 401, 'info': '没有访问权限！'})



class JwtTestView(View):

    def get(self, request):
        try:
            user = SysUser.objects.get(username='admin')
            # 直接比较明文密码
            if user.password == '123456':
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)
                return JsonResponse({'code': 200, 'token': token})
            else:
                return JsonResponse({'code': 500, 'info': '密码错误'})
        except SysUser.DoesNotExist:
            return JsonResponse({'code': 500, 'info': '用户不存在'})




class SaveView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        if data['id'] == -1:  # 添加
            obj_sysUser = SysUser(username=data['username'], realname=data['realname'],nickname=data['nickname'],gender=data['gender'],
                                  phone=data['phone'],email=data['email'],dept_id=data['dept_id'],level_id=data['level_id'],position_id=data['position_id'],
                                  status=data['status'],
                                  can_view_commenter=data.get('can_view_commenter', 0),
                                  remark=data['remark'])
            obj_sysUser.create_time = timezone.now()
            obj_sysUser.avatar = 'default.jpg'
            obj_sysUser.password = '123456'  # 明文存储
            obj_sysUser.save()
        else:  # 修改
            # 先从数据库获取现有用户对象（包含原有avatar等字段）
            obj_sysUser = SysUser.objects.get(id=data['id'])
            # 只更新需要修改的字段，未提及的字段（如avatar）保持原样
            obj_sysUser.username = data['username']
            # 仅在提供了新密码时才更新密码，否则保留原密码
            if 'password' in data and data['password']:  # 只有当密码不为空时才更新
                obj_sysUser.password = data['password']  # 明文存储
            obj_sysUser.realname = data['realname']
            obj_sysUser.nickname = data['nickname']
            obj_sysUser.gender = data['gender']
            obj_sysUser.phone = data['phone']
            obj_sysUser.email = data['email']
            obj_sysUser.birthday = data.get('birthday')  # 用get避免key不存在报错
            obj_sysUser.dept_id = data['dept_id']
            obj_sysUser.level_id = data['level_id']
            obj_sysUser.position_id = data['position_id']
            obj_sysUser.status = data['status']
            obj_sysUser.can_view_commenter = data.get('can_view_commenter', 0)
            obj_sysUser.remark = data['remark']
            obj_sysUser.update_time = timezone.now()  # 更新时间
            obj_sysUser.save()
        return JsonResponse({'code': 200})


class ActionView(View):

    def get(self, request):
        """
        根据id获取用户信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        user_object = SysUser.objects.get(id=id)
        return JsonResponse({'code': 200, 'user': SysUserSerializer(user_object).data})

    def delete(self, request):
        """
        删除操作 - 提交审批
        :param request:
        :return:
        """
        from approval.models import SysApproval
        
        idList = json.loads(request.body.decode("utf-8"))
        current_user = request.user
        
        # 管理员直接删除，普通用户提交审批
        if current_user.username == 'admin':
            SysUserRole.objects.filter(user_id__in=idList).delete()
            SysUser.objects.filter(id__in=idList).delete()
            return JsonResponse({'code': 200, 'msg': '删除成功'})
        else:
            # 获取要删除的用户信息
            users_to_delete = SysUser.objects.filter(id__in=idList)
            user_names = [user.realname or user.username for user in users_to_delete]
            
            # 创建审批申请
            approval = SysApproval.objects.create(
                approval_type=SysApproval.TYPE_USER_DELETE,
                title=f'删除用户申请：{", ".join(user_names)}',
                content=f'申请删除 {len(idList)} 个用户',
                target_data=json.dumps(idList),
                applicant_id=current_user.id,
                applicant_name=current_user.realname or current_user.username,
                status=SysApproval.STATUS_PENDING
            )
            
            return JsonResponse({
                'code': 200,
                'msg': '删除申请已提交，等待审批',
                'approval_id': approval.id
            })




class CheckView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        username = data['username']
        if SysUser.objects.filter(username=username).exists():
            return JsonResponse({'code': 500})
        else:
            return JsonResponse({'code': 200})

class PwdView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        oldPassword = data['oldPassword']
        newPassword = data['newPassword']
        obj_user = SysUser.objects.get(id=id)
        # 验证旧密码（明文比较）
        if obj_user.password == oldPassword:
            obj_user.password = newPassword  # 直接存储明文密码
            obj_user.update_time = timezone.now()
            obj_user.save()
            return JsonResponse({'code': 200})
        else:
            return JsonResponse({'code': 500, 'errorInfo': '原密码错误！'})

class ImageView(View):

    def post(self, request):
        file = request.FILES.get('avatar')

        if file:
            file_name = file.name
            suffixName = file_name[file_name.rfind("."):]
            new_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + suffixName
            file_path = str(settings.MEDIA_ROOT) + "\\userAvatar\\" + new_file_name

            try:
                with open(file_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                return JsonResponse({'code': 200, 'title': new_file_name})
            except:
                return JsonResponse({'code': 500, 'errorInfo': '上传头像失败'})


class AvatarView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        avatar = data['avatar']
        obj_user = SysUser.objects.get(id=id)
        obj_user.avatar = avatar
        obj_user.save()
        return JsonResponse({'code': 200})


class SearchView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            pageNum = data['pageNum']  # 当前页
            pageSize = data['pageSize']  # 每页大小
            query = data['query']  # 查询参数

            # 查询用户并应用数据权限过滤
            user_queryset = SysUser.objects.filter(username__icontains=query)
            
            # 应用数据权限过滤
            user_queryset = DataPermissionUtil.apply_data_filter(
                user_queryset,
                request.user,
                user_field='id',
                dept_field='dept_id'
            )
            
            paginator = Paginator(user_queryset, pageSize)
            
            # 处理页码超出范围的情况
            if pageNum < 1:
                pageNum = 1
            elif pageNum > paginator.num_pages and paginator.num_pages > 0:
                pageNum = paginator.num_pages
            
            userListPage = paginator.page(pageNum)
            obj_users = userListPage.object_list.values()  # 转成字典
            users = list(obj_users)  # 把外层的容器转成List

            # 批量获取相关数据，减少数据库查询
            level_ids = [user['level_id'] for user in users]
            post_ids = [user['position_id'] for user in users]
            dept_ids = [user['dept_id'] for user in users]

            # 查询所有需要的关联数据
            levels = {l.id: l.name for l in SysLevel.objects.filter(id__in=level_ids)}
            posts = {p.id: p.name for p in SysPost.objects.filter(id__in=post_ids)}
            depts = {d.id: d.name for d in SysDept.objects.filter(id__in=dept_ids)}

            for user in users:
                # 处理角色信息
                userId = user['id']
                # 使用Django ORM替代原始SQL查询，防止SQL注入
                user_role_ids = SysUserRole.objects.filter(user_id=userId).values_list('role_id', flat=True)
                roleList = SysRole.objects.filter(id__in=user_role_ids)
                roleListDict = []
                for role in roleList:
                    roleDict = {"id": role.id, "name": role.name}
                    roleListDict.append(roleDict)
                user['roleList'] = roleListDict

                # 添加职级、岗位、部门名称
                user['level_name'] = levels.get(user['level_id'], '')
                user['post_name'] = posts.get(user['position_id'], '')
                user['dept_name'] = depts.get(user['dept_id'], '')

                if user.get('create_time'):
                    # 若数据库中是 datetime 对象，直接格式化；若为字符串，先转换为 datetime
                    if isinstance(user['create_time'], str):
                        # 处理类似 "2025-10-29T10:42:11Z" 的字符串（去除Z，转换为本地时间）
                        create_time = datetime.fromisoformat(user['create_time'].replace('Z', '+00:00'))
                        # 转换为本地时间（如果需要），这里直接格式化
                        user['create_time'] = create_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        # 若为 datetime 对象，直接格式化
                        user['create_time'] = user['create_time'].strftime("%Y-%m-%d %H:%M:%S")

                    # 处理最后登录时间
                if user.get('login_date') and user['login_date'] != '':
                    if isinstance(user['login_date'], str):
                        login_date = datetime.fromisoformat(user['login_date'].replace('Z', '+00:00'))
                        user['login_date'] = login_date.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        user['login_date'] = user['login_date'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # 若未登录过，显示空或提示
                    user['login_date'] = '-'

            total = user_queryset.count()
            return JsonResponse({
                'code': 200,
                'userList': users,
                'total': total
            })
        except Exception as e:
            import logging
            logging.exception(f'用户查询失败: {str(e)}')
            return JsonResponse({
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'userList': [],
                'total': 0
            })

# 重置密码
class PasswordView(View):

    def get(self, request):
        id = request.GET.get("id")
        user_object = SysUser.objects.get(id=id)
        user_object.password = '123456'  # 明文存储
        user_object.update_time = timezone.now()  # 使用Django的timezone而不是datetime.now()
        user_object.save()
        return JsonResponse({'code': 200})


# 用户状态修改
class StatusView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        status = data['status']
        user_object = SysUser.objects.get(id=id)
        user_object.status = status
        user_object.save()
        return JsonResponse({'code': 200})


# 用户角色授权
class GrantRole(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_id = data['id']
        roleIdList = data['roleIds']

        SysUserRole.objects.filter(user_id=user_id).delete()  # 删除用户角色关联表中的指定用户数据
        for roleId in roleIdList:
            userRole = SysUserRole(user_id=user_id, role_id=roleId)
            userRole.save()
        return JsonResponse({'code': 200})

# 在views.py中添加以下视图
class DeptListView(View):
    """获取部门列表"""
    def get(self, request):
        try:
            dept_list = SysDept.objects.all().values('id', 'name')
            return JsonResponse({
                'code': 200,
                'deptList': list(dept_list)
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取部门列表失败: {str(e)}'})


class PostListView(View):
    """获取岗位列表"""
    def get(self, request):
        try:
            post_list = SysPost.objects.all().values('id', 'name')
            return JsonResponse({
                'code': 200,
                'postList': list(post_list)
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取岗位列表失败: {str(e)}'})


class LevelListView(View):
    """获取职级列表"""
    def get(self, request):
        try:
            level_list = SysLevel.objects.all().values('id', 'name')
            return JsonResponse({
                'code': 200,
                'levelList': list(level_list)
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取职级列表失败: {str(e)}'})

class UserListView(View):
    def get(self, request):
        """获取所有用户列表"""
        users = SysUser.objects.all().values('id', 'realname')
        return JsonResponse({
            'code': 200,
            'userList': list(users)
        })


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# 调试视图 - 检查admin用户状态
@method_decorator(csrf_exempt, name='dispatch')
class CheckAdminUserView(View):
    def get(self, request):
        """检查admin用户是否存在及状态"""
        try:
            admin_user = SysUser.objects.get(username='admin')
            return JsonResponse({
                'code': 200,
                'info': 'admin用户存在',
                'user_status': admin_user.status,
                'user_id': admin_user.id
            })
        except SysUser.DoesNotExist:
            return JsonResponse({
                'code': 500,
                'info': 'admin用户不存在'
            })

# 重置admin用户密码视图
@method_decorator(csrf_exempt, name='dispatch')
class ResetAdminPasswordView(View):
    def get(self, request):
        """重置admin用户密码为1234567"""
        try:
            admin_user = SysUser.objects.get(username='admin')
            admin_user.password = '1234567'  # 明文存储
            admin_user.save()
            return JsonResponse({'code': 200, 'info': 'admin用户密码已重置为1234567'})
        except SysUser.DoesNotExist:
            return JsonResponse({'code': 500, 'info': 'admin用户不存在'})



