# Copyright (c) 2025 知识库管理系统. All rights reserved.

"""
ASGI config for jj_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jj_system.settings')

application = get_asgi_application()
