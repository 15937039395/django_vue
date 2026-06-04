# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.core.management.base import BaseCommand
from role.models import SysRole
from menu.models import SysMenu, SysRoleMenu

class Command(BaseCommand):
    help = '为超级管理员角色自动分配所有权限'

    def handle(self, *args, **options):
        try:
            # 查找超级管理员角色（假设是 admin 或包含 admin 的角色）
            admin_roles = SysRole.objects.filter(code__icontains='admin')
            
            if not admin_roles.exists():
                self.stdout.write(
                    self.style.ERROR('✗ 未找到超级管理员角色！')
                )
                return
            
            # 获取所有菜单
            all_menus = SysMenu.objects.all()
            
            for admin_role in admin_roles:
                self.stdout.write(
                    self.style.SUCCESS(f'\n=== 为角色 [{admin_role.name}] 分配权限 ===')
                )
                
                assigned_count = 0
                skipped_count = 0
                
                for menu in all_menus:
                    # 检查是否已分配
                    existing = SysRoleMenu.objects.filter(
                        role_id=admin_role.id,
                        menu_id=menu.id
                    ).exists()
                    
                    if existing:
                        skipped_count += 1
                    else:
                        # 分配权限
                        SysRoleMenu.objects.create(
                            role_id=admin_role.id,
                            menu_id=menu.id
                        )
                        assigned_count += 1
                        
                        if menu.perms:
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ 分配权限：{menu.name} ({menu.perms})')
                            )
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✓ 成功分配 {assigned_count} 个权限，跳过 {skipped_count} 个已存在的权限')
                )
            
            self.stdout.write(
                self.style.SUCCESS('\n\n=== 权限分配完成！===')
            )
            self.stdout.write(
                self.style.WARNING('提示：请重新登录以刷新权限')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ 分配权限失败：{str(e)}')
            )
