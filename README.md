# TickFix 钟表维修管理系统

面向老钟表店和商场维修柜台的全栈管理系统，支持接件单管理、零件仓库、维修状态流转等核心功能。

## 技术栈

### 后端
- Django 4.2 + Django REST Framework (DRF)
- MySQL 8.0
- SimpleJWT 身份认证
- django-filter 数据过滤

### 前端
- Vue 3 + Vite
- Element Plus UI 组件库
- Pinia 状态管理
- Vue Router 路由管理
- Axios HTTP 请求

## 项目结构

```
.
├── docker-compose.yml          # Docker Compose 配置
├── tickfix-api/                # 后端 Django 项目
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── tickfix/                # Django 项目配置
│   └── apps/
│       ├── accounts/           # 用户管理模块
│       ├── inventory/          # 零件仓库模块
│       └── repairs/            # 维修管理模块
└── tickfix-console/            # 前端 Vue 项目
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── views/              # 页面组件
        ├── api/                # API 接口封装
        ├── store/              # Pinia 状态
        ├── router/             # 路由配置
        └── utils/              # 工具函数
```

## 快速启动

### 方式一：Docker Compose 启动（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

启动后访问：
- 前端: http://localhost:8080
- 后端 API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

### 方式二：本地开发启动

#### 后端

```bash
cd tickfix-api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（修改 settings.py 中的数据库连接）
# 确保本地 MySQL 已启动并创建数据库

# 数据库迁移
python manage.py migrate

# 初始化基础数据
python manage.py init_data

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

#### 前端

```bash
cd tickfix-console

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 默认账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123456 | 管理员 | 系统管理员，拥有全部权限 |
| reception | reception123 | 前台接件员 | 负责接件、录入客户信息 |
| tech01 | tech123456 | 维修技师 | 负责检测、维修、零件出库 |
| cashier | cashier123 | 收银员 | 负责取件结算 |

## 核心功能

### 1. 接件单管理
- 记录品牌、型号、外观瑕疵、故障描述
- 自动生成接件单号和6位取件码
- 预估费用、最终费用、零件费用、工时费用分项统计

### 2. 维修状态流转（规范化）
系统内置状态机，不允许前端随意修改状态：

```
待检测 → 检测中 → 已报价待确认 → 客户同意 → 维修中 → 零件出库 → 维修完成 → 待取件 → 已完成
                        ↓
                    客户拒绝 → 已取消
```

每个状态转换都会记录操作人和备注，形成完整的状态历史轨迹。

### 3. 零件仓库
- 电池、表冠、表镜、机芯配件等分类管理
- 库存数量、最低库存预警
- 库存入库/出库/调整记录
- 零件适配说明

### 4. 取件查询
- 通过取件码快速查询维修状态
- 确认取件结算

### 5. 工作台数据统计
- 总接件单、待检测、维修中、待取件数量统计
- 最近接件单列表
- 库存预警提醒

## Docker 数据卷持久化

项目配置了三个数据卷确保数据持久化：

| 数据卷名称 | 挂载路径 | 说明 |
|-----------|----------|------|
| mysql_data | /var/lib/mysql | MySQL 数据库数据 |
| static_volume | /app/static | Django 静态文件 |
| media_volume | /app/media | 用户上传媒体文件 |

数据不会因容器重建而丢失。如需备份数据：

```bash
# 备份 MySQL 数据
docker exec tickfix-mysql mysqldump -u tickfix_user -ptickfix_pass_2024 tickfix_db > backup.sql

# 恢复 MySQL 数据
docker exec -i tickfix-mysql mysql -u tickfix_user -ptickfix_pass_2024 tickfix_db < backup.sql
```

## API 接口说明

### 认证接口
- `POST /api/auth/login/` - 登录获取 Token
- `POST /api/auth/refresh/` - 刷新 Token
- `GET /api/auth/users/me/` - 获取当前用户信息

### 维修管理接口
- `GET/POST /api/repairs/orders/` - 接件单列表/创建
- `GET/PUT /api/repairs/orders/{id}/` - 接件单详情/更新
- `POST /api/repairs/orders/{id}/transition/` - 状态流转
- `POST /api/repairs/orders/{id}/add_part_usage/` - 添加零件消耗
- `GET /api/repairs/orders/by_pickup_code/?code=xxx` - 取件码查询
- `GET /api/repairs/orders/dashboard_stats/` - 工作台统计

### 零件仓库接口
- `GET /api/inventory/categories/` - 零件分类列表
- `GET/POST /api/inventory/parts/` - 零件列表/创建
- `GET/PUT /api/inventory/parts/{id}/` - 零件详情/更新
- `POST /api/inventory/parts/{id}/adjust_stock/` - 调整库存
- `GET /api/inventory/parts/low_stock/` - 低库存预警
- `GET /api/inventory/stock-records/` - 库存变动记录

## 维修状态编码说明

| 编码 | 显示名称 | 说明 |
|------|----------|------|
| pending | 待检测 | 刚接件，等待技师检测 |
| inspecting | 检测中 | 技师正在检测故障 |
| quoted | 已报价待确认 | 检测完成，已报价等待客户确认 |
| customer_approved | 客户同意 | 客户同意报价，可开始维修 |
| customer_rejected | 客户拒绝 | 客户拒绝报价 |
| repairing | 维修中 | 正在进行维修作业 |
| parts_out | 零件出库 | 已领取维修所需零件 |
| repaired | 维修完成 | 维修已完成，等待通知客户 |
| ready_for_pickup | 待取件 | 已通知客户，等待取件 |
| completed | 已完成 | 客户已取件，订单完成 |
| cancelled | 已取消 | 订单已取消 |

## 注意事项

1. 生产环境请修改 `SECRET_KEY`、数据库密码等敏感配置
2. 建议配置 HTTPS 确保 Token 传输安全
3. 定期备份 MySQL 数据
4. 零件出库会自动扣减库存，请确保库存充足
5. 状态流转不可逆向，操作前请确认
