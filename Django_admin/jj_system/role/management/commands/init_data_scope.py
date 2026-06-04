# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.core.management.base import BaseCommand
from role.models import SysRole


class Command(BaseCommand):
    help = '为现有角色初始化数据权限范围'

    def handle(self, *args, **options):
        """
        为现有角色设置默认数据权限：
        - admin 角色：全部数据权限
        - 其他角色：仅本人数据权限
        """
        roles = SysRole.objects.all()
        
        updated_count = 0
        for role in roles:
            # 如果角色代码是 admin，设置为全部数据权限
            if role.code and 'admin' in role.code.lower():
                role.data_scope = SysRole.DATA_SCOPE_ALL
                role.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 角色 [{role.name}] 设置为：全部数据权限')
                )
                updated_count += 1
            # 如果角色名称包含"管理"，设置为本部门及下级部门
            elif role.name and '管理' in role.name:
                role.data_scope = SysRole.DATA_SCOPE_DEPT_AND_SUB
                role.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 角色 [{role.name}] 设置为：本部门及下级部门')
                )
                updated_count += 1
            # 其他角色默认为仅本人
            else:
                role.data_scope = SysRole.DATA_SCOPE_SELF
                role.save()
                self.stdout.write(
                    self.style.WARNING(f'○ 角色 [{role.name}] 设置为：仅本人')
                )
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ 成功初始化 {updated_count} 个角色的数据权限！')
        )
