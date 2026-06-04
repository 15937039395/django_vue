# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.core.management.base import BaseCommand
from menu.models import SysMenu
from common.permissions import UserPermissions


class Command(BaseCommand):
    help = '初始化审批管理菜单'

    def handle(self, *args, **options):
        # 检查是否已存在审批管理菜单
        if SysMenu.objects.filter(name='审批管理').exists():
            self.stdout.write(self.style.WARNING('审批管理菜单已存在，跳过创建'))
            return

        # 创建审批管理菜单
        approval_menu = SysMenu.objects.create(
            name='审批管理',
            path='/approval',
            component='sys/approval/index',
            icon='el-icon-document-checked',
            menu_type='C',
            order_num=5,
            perms='sys:approval:view'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ 创建审批管理菜单成功 (ID: {approval_menu.id})'))
        
        # 创建审批管理的按钮权限
        button_menus = [
            {'name': '审批通过', 'perms': 'sys:approval:approve', 'order_num': 1},
            {'name': '审批拒绝', 'perms': 'sys:approval:reject', 'order_num': 2},
            {'name': '撤销审批', 'perms': 'sys:approval:cancel', 'order_num': 3},
        ]
        
        for btn_data in button_menus:
            SysMenu.objects.create(
                name=btn_data['name'],
                parent_id=approval_menu.id,
                perms=btn_data['perms'],
                menu_type='F',
                order_num=btn_data['order_num']
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ 创建按钮权限: {btn_data["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('\n审批管理菜单初始化完成！'))
        self.stdout.write(self.style.WARNING('\n请运行以下命令为管理员分配权限：'))
        self.stdout.write(self.style.WARNING('  python manage.py assign_admin_permissions'))
