# Copyright (c) 2025 知识库管理系统. All rights reserved.

"""
初始化管理员账号、菜单和权限脚本
使用方法：python init_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jj_system.settings')
django.setup()

from user.models import SysUser
from role.models import SysRole, SysUserRole
from menu.models import SysMenu, SysRoleMenu


# 菜单数据：(名称, 图标, 类型, 父菜单名, 排序, 路由, 组件, 权限标识)
# 类型: M=目录, C=菜单, F=按钮
MENUS = [
    # 顶级菜单
    ('系统管理', 'Setting', 'M', None, 1, '/sys', None, None),
    ('业务管理', 'Briefcase', 'M', None, 2, '/bsns', None, None),
    ('日志管理', 'Document', 'M', None, 3, '/log', None, None),
    ('审批管理', 'Stamp', 'M', None, 4, '/sys/approval', None, None),

    # 系统管理子菜单
    ('用户管理', 'User', 'C', '系统管理', 1, '/sys/user', 'sys/user/index', 'sys:user:view'),
    ('角色管理', 'UserFilled', 'C', '系统管理', 2, '/sys/role', 'sys/role/index', 'sys:role:view'),
    ('菜单管理', 'Menu', 'C', '系统管理', 3, '/sys/menu', 'sys/menu/index', 'sys:menu:view'),
    ('部门管理', 'OfficeBuilding', 'C', '系统管理', 4, '/sys/dept', 'sys/dept/index', 'sys:dept:view'),
    ('岗位管理', 'Postcard', 'C', '系统管理', 5, '/sys/post', 'sys/post/index', 'sys:post:view'),
    ('职级管理', 'TrophyBase', 'C', '系统管理', 6, '/sys/level', 'sys/level/index', 'sys:level:view'),
    ('消息通知', 'Bell', 'C', '系统管理', 7, '/sys/notification', 'sys/notification/index', 'sys:notification:view'),

    # 业务管理子菜单
    ('工时填报', 'EditPen', 'C', '业务管理', 1, '/bsns/manhour', 'bsns/manhour/index', 'bsns:manhour:view'),
    ('逾期管理', 'Warning', 'C', '业务管理', 2, '/bsns/blacklist', 'bsns/blacklist/index', 'bsns:blacklist:view'),
    ('知识库管理', 'Collection', 'C', '业务管理', 3, '/bsns/repository', 'bsns/repository/index', 'bsns:repository:view'),
    ('项目管理', 'Folder', 'C', '业务管理', 4, '/bsns/items', 'bsns/items/index', 'bsns:items:view'),
    ('分类管理', 'Grid', 'C', '业务管理', 5, '/bsns/classify', 'bsns/classify/index', 'bsns:classify:view'),
    ('事件管理', 'AlarmClock', 'C', '业务管理', 6, '/bsns/event', 'bsns/event/index', 'bsns:event:view'),
    ('文件管理', 'FolderOpened', 'C', '业务管理', 7, '/bsns/files', 'bsns/files/index', 'bsns:file:view'),

    # 日志管理子菜单
    ('操作日志', 'Notebook', 'C', '日志管理', 1, '/log', 'sys/log/index', 'sys:log:view'),
]


def init_menus():
    """初始化菜单"""
    print('\n--- 初始化菜单 ---')
    created_count = 0
    menu_map = {}  # name -> menu object

    # 先创建所有菜单
    for name, icon, menu_type, parent_name, order, path, component, perms in MENUS:
        parent_id = 0
        if parent_name:
            parent = menu_map.get(parent_name)
            if parent:
                parent_id = parent.id

        menu, created = SysMenu.objects.get_or_create(
            name=name,
            defaults={
                'icon': icon,
                'menu_type': menu_type,
                'parent_id': parent_id,
                'order_num': order,
                'path': path,
                'component': component,
                'perms': perms,
            }
        )
        menu_map[name] = menu
        if created:
            created_count += 1
            print(f'  ✅ 创建菜单: {name}')
        else:
            print(f'  ⚠️  菜单已存在: {name}')

    print(f'  共创建 {created_count} 个菜单\n')
    return menu_map


def init_admin_role(menu_map):
    """初始化管理员角色并分配所有菜单权限"""
    print('--- 初始化管理员角色 ---')

    admin_role, created = SysRole.objects.get_or_create(
        code='admin',
        defaults={
            'name': '超级管理员',
            'status': 1,
            'sort': 0,
            'data_scope': 1,
        }
    )
    if created:
        print('  ✅ 超级管理员角色创建成功')
    else:
        print('  ⚠️  超级管理员角色已存在')

    # 分配所有菜单权限给管理员角色
    all_menus = SysMenu.objects.all()
    assigned = 0
    for menu in all_menus:
        _, created = SysRoleMenu.objects.get_or_create(role=admin_role, menu=menu)
        if created:
            assigned += 1

    print(f'  ✅ 已分配 {assigned} 个菜单权限给超级管理员\n')
    return admin_role


def init_admin_user(admin_role):
    """初始化管理员账号"""
    print('--- 初始化管理员账号 ---')

    if not SysUser.objects.filter(username='admin').exists():
        admin_user = SysUser.objects.create(
            username='admin',
            password='admin123',
            realname='管理员',
            nickname='管理员',
            gender=1,
            avatar='',
            phone='',
            email='',
            birthday='2000-01-01',
            dept_id=0,
            level_id=0,
            position_id=0,
            province_code='',
            city_code='',
            district_code='',
            address_info='',
            address='',
            intro='',
            status=1,
            remark='系统初始化管理员',
            sort=0,
        )
        SysUserRole.objects.create(role=admin_role, user=admin_user)
        print('  ✅ 管理员账号创建成功！')
        print('     用户名: admin')
        print('     密码: admin123')
    else:
        # 账号已存在，确保关联了管理员角色
        admin_user = SysUser.objects.get(username='admin')
        if not SysUserRole.objects.filter(role=admin_role, user=admin_user).exists():
            SysUserRole.objects.create(role=admin_role, user=admin_user)
            print('  ✅ 已将管理员角色分配给 admin 用户')
        else:
            print('  ⚠️  管理员账号已存在，跳过创建')

    print('     ⚠️  请登录后立即修改密码！\n')


if __name__ == '__main__':
    print('=' * 50)
    print('系统初始化')
    print('=' * 50)

    menu_map = init_menus()
    admin_role = init_admin_role(menu_map)
    init_admin_user(admin_role)

    print('=' * 50)
    print('初始化完成！')
    print('=' * 50)
