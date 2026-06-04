# 知识库管理系统 - 部署说明

## 一、项目简介

- **前端**：Vue 3 + Element Plus + ECharts
- **后端**：Django 5.2.6 + DRF + MySQL
- **默认账号**：admin / admin123

## 二、环境要求

- Python >= 3.10
- Node.js >= 16
- MySQL >= 8.0
- Nginx（生产部署）

## 三、项目目录结构

```
Django_admin/
├── README.md                          # 部署说明文档
── nginx_config.txt                   # Nginx 生产部署配置参考
│
├── jj_system/                         # 后端项目根目录
│   ├── manage.py                      # Django 管理脚本（迁移、启动等）
│   ├── init_admin.py                  # 系统初始化脚本（创建菜单、管理员角色、管理员账号）
│   ├── requirements.txt               # Python 依赖包清单
│   ├── requirements_scheduler.txt     # 定时任务相关依赖（已移除，仅供参考）
│   ├── debug.log                      # 调试日志
│   │
│   ├── jj_system/                     # Django 项目配置目录
│   │   ├── settings.py                # 核心配置文件（数据库、中间件、跨域等）
│   │   ├── urls.py                    # 主路由配置
│   │   ├── wsgi.py                    # WSGI 入口（生产部署用）
│   │   └── asgi.py                    # ASGI 入口
│   │
│   ├── user/                          # 用户模块
│   │   ├── models.py                  # 用户数据模型
│   │   ├── views.py                   # 用户接口（登录、CRUD等）
│   │   ├── urls.py                    # 用户路由
│   │   ├── middleware.py              # JWT 认证中间件
│   │   └── migrations/               # 数据库迁移文件
│   │
│   ├── role/                          # 角色模块
│   │   ├── models.py                  # 角色、用户角色关联模型
│   │   ├── views.py                   # 角色接口
│   │   └── urls.py                    # 角色路由
│   │
│   ├── menu/                          # 菜单模块
│   │   ├── models.py                  # 菜单、角色菜单关联模型
│   │   ├── views.py                   # 菜单接口
│   │   ├── urls.py                    # 菜单路由
│   │   └── management/commands/       # 菜单初始化命令
│   │
│   ├── department/                    # 部门模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── post/                          # 岗位模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── level/                         # 职级模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── log/                           # 日志模块
│   │   ├── models.py                  # 操作日志模型
│   │   ├── middleware.py              # 日志记录中间件
│   │   ├── views.py / urls.py
│   │   └── migrations/
│   │
│   ├── repository/                    # 知识库模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── event/                         # 事件管理模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── classify/                      # 分类管理模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── items/                         # 项目管理模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── file_manager/                  # 文件管理模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── approval/                      # 审批管理模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── notification/                  # 消息通知模块
│   │   ├── models.py / views.py / urls.py / tasks.py
│   │   ── migrations/
│   │
│   ├── blacklist/                     # 逾期管理模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── manhour/                       # 工时填报模块
│   │   ├── models.py / views.py / urls.py
│   │   └── migrations/
│   │
│   ├── common/                        # 公共模块
│   │   ├── decorators.py              # 自定义装饰器
│   │   ├── permissions.py             # 权限相关
│   │   └── data_permission.py         # 数据权限
│   │
│   ├── media/                         # 媒体文件存储目录（上传文件、图片等）
│   │   ├── images/
│   │   ├── uploads/
│   │   └── userAvatar/
│   │
│   └── logs/                          # 日志目录
│       └── django_project.log
│
├── vue3_admin/                        # 前端项目根目录
│   ├── package.json                   # 前端依赖清单
│   ├── vue.config.js                  # Vue CLI 配置（代理、打包等）
│   ├── jsconfig.json                  # JS 配置
│   ├── babel.config.js                # Babel 配置
│   ├── ecosystem.config.js            # PM2 部署配置
│   │
│   ├── public/                        # 静态公共资源
│   │   ├── index.html                 # 入口 HTML
│   │   └── favicon.ico
│   │
│   ├── src/                           # 源代码目录
│   │   ├── App.vue                    # 根组件
│   │   ├── main.js                    # 入口文件
│   │   ├── router/                    # 路由配置
│   │   │   └── index.js
│   │   ├── store/                     # Vuex 状态管理
│   │   ├── views/                     # 页面组件
│   │   │   ├── Login.vue              # 登录页
│   │   │   ├── sys/                   # 系统管理页面
│   │   │   │   ├── user/              # 用户管理
│   │   │   │   ├── role/              # 角色管理
│   │   │   │   ├── menu/              # 菜单管理
│   │   │   │   ├── dept/              # 部门管理
│   │   │   │   ├── post/              # 岗位管理
│   │   │   │   ├── level/             # 职级管理
│   │   │   │   ├── notification/      # 消息通知
│   │   │   │   ├── log/               # 日志管理
│   │   │   │   └── approval/          # 审批管理
│   │   │   └── bsns/                  # 业务管理页面
│   │   │       ├── manhour/           # 工时填报
│   │   │       ├── blacklist/         # 逾期管理
│   │   │       ├── repository/        # 知识库管理
│   │   │       ├── items/             # 项目管理
│   │   │       ├── classify/          # 分类管理
│   │   │       ├── event/             # 事件管理
│   │   │       └── files/             # 文件管理
│   │   ├── components/                # 公共组件
│   │   ├── util/                      # 工具类
│   │   │   └── request.js             # Axios 请求封装
│   │   └── assets/                    # 静态资源
│   │
│   └── dist/                          # 构建产物（npm run build 后生成）
│
└── .idea/                             # IDE 配置文件（可忽略）
```

## 四、后端部署（jj_system）

### 4.1 创建虚拟环境并安装依赖

```bash
cd jj_system
python -m venv venv
# Windows
venv\Scripts\activate
# Linux
# source venv/bin/activate

pip install -r requirements.txt
```

### 4.2 配置数据库

编辑 `jj_system/jj_system/settings.py`，修改数据库连接信息：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '你的数据库名',
        'USER': '你的用户名',
        'PASSWORD': '你的密码',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

> 同时修改 `CSRF_TRUSTED_ORIGINS` 和 `MEDIA_DOMAIN` 中的地址为实际部署地址。

### 4.3 清理旧的迁移文件

**首次部署或重置数据库前，必须先删除所有旧的迁移文件：**

删除各模块 `migrations/` 目录下所有 `0*.py` 文件，仅保留 `__init__.py`。涉及以下模块：

```
approval/migrations/0001_initial.py
blacklist/migrations/0001_initial.py
classify/migrations/0001_initial.py
department/migrations/0001_initial.py
event/migrations/0001_initial.py
file_manager/migrations/0001_initial.py
items/migrations/0001_initial.py
level/migrations/0001_initial.py
log/migrations/0001_initial.py
manhour/migrations/0001_initial.py
menu/migrations/0001_initial.py
notification/migrations/0001_initial.py
post/migrations/0001_initial.py
repository/migrations/0001_initial.py
role/migrations/0001_initial.py
user/migrations/0001_initial.py
```

Windows 批量删除（在 `jj_system/` 目录下执行）：
```bash
for /r %d in (.) do @if exist "%d\0*.py" del "%d\0*.py"
```

Linux 批量删除：
```bash
find . -path "*/migrations/0*.py" -delete
```

> 注意：不要删除 `__init__.py`，只删除 `0` 开头的迁移文件。

### 4.4 生成迁移文件并建表

```bash
cd jj_system
python manage.py makemigrations
python manage.py migrate
```

### 4.5 初始化系统数据（菜单、管理员账号）

```bash
python init_admin.py
```

该脚本会自动创建：
- 全部系统菜单（系统管理、业务管理、日志管理、审批管理）
- 超级管理员角色（含所有菜单权限）
- 管理员账号（admin / admin123）

### 4.6 收集静态文件

```bash
python manage.py collectstatic --noinput
```

### 4.7 启动后端服务

**开发环境：**
```bash
python manage.py runserver 0.0.0.0:8000
```

**生产环境（使用 Gunicorn）：**
```bash
pip install gunicorn
gunicorn jj_system.wsgi:application --bind 0.0.0.0:8000 -w 4
```

## 五、前端部署（vue3_admin）

### 5.1 安装依赖

```bash
cd vue3_admin
npm install
```

### 5.2 配置后端地址

编辑 `vue3_admin/vue.config.js` 中的 `devServer.proxy` 配置，将所有代理的 `target` 改为实际后端地址：

```js
devServer: {
    port: 8080,
    proxy: {
        '/user': {
            target: 'http://你的后端地址:8000',
            changeOrigin: true
        },
        // ... 其他路由同理
    }
}
```

### 5.3 开发模式启动

```bash
npm run serve
```

访问 `http://localhost:8080` 即可。

### 5.4 生产构建

```bash
npm run build
```

构建完成后，产物在 `vue3_admin/dist` 目录下。

## 六、Nginx 部署（生产）

参考 `nginx_config.txt` 配置，修改后部署：

```bash
# 复制配置
cp nginx_config.txt /etc/nginx/sites-available/jj_system

# 修改配置中的 server_name 和文件路径
# 将 xxxxxxx 改为你的域名或IP
# 将 /var/www/vue3_admin/dist 改为实际前端dist路径
# 将 /var/www/jj_system/media/ 改为实际media路径

# 启用站点
ln -s /etc/nginx/sites-available/jj_system /etc/nginx/sites-enabled/

# 重载Nginx
nginx -t
nginx -s reload
```

## 七、常用操作命令

| 操作 | 命令 | 说明 |
|------|------|------|
| 重新生成迁移 | `python manage.py makemigrations` | 在 `jj_system/` 目录下执行 |
| 执行迁移 | `python manage.py migrate` | 创建/更新数据库表 |
| 初始化系统数据 | `python init_admin.py` | 在 `jj_system/` 目录下执行，创建菜单+管理员 |
| 启动后端 | `python manage.py runserver 0.0.0.0:8000` | 开发模式启动 |
| 启动前端 | `npm run serve` | 在 `vue3_admin/` 目录下执行 |
| 前端打包 | `npm run build` | 在 `vue3_admin/` 目录下执行 |

## 八、注意事项

1. **密码存储**：本系统密码采用明文存储，请在生产环境中修改默认密码
2. **数据库备份**：建议定期备份 MySQL 数据库
3. **文件上传**：媒体文件存储在 `jj_system/media/` 目录，确保 Nginx 有读取权限
4. **日志文件**：后端日志位于 `jj_system/logs/django_project.log`
5. **首次部署流程**：配置数据库 → `makemigrations` → `migrate` → `init_admin.py` → 启动服务
6. **数据库重置**：如需清空重建，删除各模块 `migrations/` 目录下的 `0*.py` 文件（保留 `__init__.py`），然后重新执行 `makemigrations` → `migrate` → `init_admin.py`
