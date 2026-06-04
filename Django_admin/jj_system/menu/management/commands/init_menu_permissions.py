# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.core.management.base import BaseCommand
from menu.models import SysMenu

class Command(BaseCommand):
    help = '为菜单初始化权限标识，并创建按钮类型菜单项'

    def handle(self, *args, **options):
        # 第一步：为主菜单设置基础权限
        main_menus = [
            {'name': '用户管理', 'perms': 'sys:user:view'},
            {'name': '角色管理', 'perms': 'sys:role:view'},
            {'name': '菜单管理', 'perms': 'sys:menu:view'},
            {'name': '部门管理', 'perms': 'sys:dept:view'},
            {'name': '文件管理', 'perms': 'sys:file:view'},
            {'name': '知识库管理', 'perms': 'sys:repository:view'},
            {'name': '事件管理', 'perms': 'sys:event:view'},
        ]
        
        self.stdout.write(self.style.SUCCESS('\n=== 第一步：设置主菜单权限 ==='))
        updated_count = 0
        for menu_data in main_menus:
            try:
                menu = SysMenu.objects.get(name=menu_data['name'])
                menu.perms = menu_data['perms']
                menu.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 菜单 [{menu.name}] 设置权限标识为：{menu.perms}')
                )
                updated_count += 1
            except SysMenu.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'○ 菜单 [{menu_data["name"]}] 不存在，跳过')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ 菜单 [{menu_data["name"]}] 设置失败：{str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ 成功初始化 {updated_count} 个主菜单的权限标识！')
        )
        
        # 第二步：为用户管理创建按钮菜单项
        self.stdout.write(self.style.SUCCESS('\n=== 第二步：创建按钮菜单项 ==='))
        
        try:
            # 查找用户管理菜单
            user_menu = SysMenu.objects.get(name='用户管理')
            
            # 定义按钮菜单
            button_menus = [
                {'name': '新增用户', 'perms': 'sys:user:add', 'order_num': 1},
                {'name': '编辑用户', 'perms': 'sys:user:edit', 'order_num': 2},
                {'name': '删除用户', 'perms': 'sys:user:delete', 'order_num': 3},
                {'name': '分配角色', 'perms': 'sys:user:grant', 'order_num': 4},
                {'name': '重置密码', 'perms': 'sys:user:resetPwd', 'order_num': 5},
            ]
            
            created_count = 0
            for btn_data in button_menus:
                # 检查是否已存在
                existing = SysMenu.objects.filter(
                    parent_id=user_menu.id, 
                    perms=btn_data['perms']
                ).first()
                
                if existing:
                    self.stdout.write(
                        self.style.WARNING(f'○ 按钮 [{btn_data["name"]}] 已存在，跳过')
                    )
                else:
                    # 创建按钮菜单项
                    SysMenu.objects.create(
                        name=btn_data['name'],
                        parent_id=user_menu.id,
                        perms=btn_data['perms'],
                        menu_type='F',  # F表示按钮
                        order_num=btn_data['order_num']
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ 创建按钮菜单 [{btn_data["name"]}] - {btn_data["perms"]}')
                    )
                    created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ 成功创建 {created_count} 个按钮菜单项！')
            )
            
        except SysMenu.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('✗ 用户管理菜单不存在，无法创建按钮菜单项')
            )
        
        # 第三步：为文件管理创建按钮菜单项
        try:
            file_menu = SysMenu.objects.get(name='文件管理')
            
            file_button_menus = [
                {'name': '上传文件', 'perms': 'sys:file:upload', 'order_num': 1},
                {'name': '下载文件', 'perms': 'sys:file:download', 'order_num': 2},
                {'name': '删除文件', 'perms': 'sys:file:delete', 'order_num': 3},
            ]
            
            created_count = 0
            for btn_data in file_button_menus:
                existing = SysMenu.objects.filter(
                    parent_id=file_menu.id, 
                    perms=btn_data['perms']
                ).first()
                
                if existing:
                    self.stdout.write(
                        self.style.WARNING(f'○ 按钮 [{btn_data["name"]}] 已存在，跳过')
                    )
                else:
                    SysMenu.objects.create(
                        name=btn_data['name'],
                        parent_id=file_menu.id,
                        perms=btn_data['perms'],
                        menu_type='F',
                        order_num=btn_data['order_num']
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ 创建按钮菜单 [{btn_data["name"]}] - {btn_data["perms"]}')
                    )
                    created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ 成功创建 {created_count} 个文件管理按钮菜单项！')
            )
            
        except SysMenu.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('✗ 文件管理菜单不存在，无法创建按钮菜单项')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n\n=== 初始化完成！===')
        )
        self.stdout.write(
            self.style.WARNING('提示：请在角色管理中为角色分配这些按钮权限')
        )
