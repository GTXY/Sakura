# 桜探記（Sakura）v1.0

个人向的日本店铺与行程探访记录 Web 应用：展示封面图、简介、评分与相册，支持登录后记录自己的探访。仓库根目录名为 **Sakura**，前端在 **`frontend/`**，后端在 **`backend/`**。

**线上地址**：https://www.kudou-shinichi.cn/Sakura/

---

## 1. 产品功能

### 未登录
- 首页三个选项卡：**最新探访**（全员按时间倒序）、**精选推荐**（featured 标记记录）
- 店铺列表 `/shops`：关键词搜索、大类筛选、都道府县筛选
- 店铺详情 `/shops/:id`：封面、元信息、相册灯箱、MapLibre 地图

### 已登录
- 首页增加第三个选项卡：**我的探访**（仅显示自己创建的记录）
- 新增店铺 `/shops/new`：表单录入、封面与多图上传（JPG/PNG，≤10MB）、地图选点
- 导航栏右上角显示**粉色头像圆圈**（用户名首字母大写），可退出登录

### 认证机制
- **无注册**：账号由管理员通过 `create_user.py` 脚本手动创建
- JWT Token，有效期 30 天，存于 `localStorage`

---

## 2. 技术栈

### 前端（`frontend/`）

| 技术 | 说明 |
|------|------|
| Vite + Vue 3 | 构建与框架（Composition API + TypeScript） |
| Vue Router 4 | 路由，生产 base 为 `/Sakura/`，本地开发 base 为 `/` |
| Pinia | 状态管理（`authStore` 管理登录状态） |
| Tailwind CSS | 样式（`sakura` 主题色板） |
| MapLibre GL | 详情页与新建页地图 |

### 后端（`backend/`）

| 技术 | 说明 |
|------|------|
| FastAPI + Uvicorn | HTTP API（生产端口 8001，本地端口 8000） |
| SQLAlchemy 2（async）+ asyncpg / aiomysql | ORM，本地 PostgreSQL，生产 MySQL |
| Pydantic v2 | 请求/响应模型（JSON 字段驼峰） |
| python-jose + bcrypt | JWT 签发与密码哈希（bcrypt 直接调用，不依赖 passlib） |
| google-cloud-storage | 图片存储（GCS，Workload Identity 认证） |

---

## 3. 前端路由

| 路径 | 权限 | 说明 |
|------|------|------|
| `/` | 公开 | 首页（最新探访 / 精选推荐 / 我的探访） |
| `/login` | 公开 | 登录页 |
| `/shops` | 公开 | 店铺列表（搜索/筛选） |
| `/shops/new` | **需登录** | 新增店铺 |
| `/shops/:id` | 公开 | 店铺详情 |

---

## 4. 后端 API 概要

### 认证
- `POST /api/auth/login`：`{username, password}` → `{access_token}`
- `GET /api/auth/me`：返回当前用户信息

### 店铺
- `GET /api/shops`：分页列表；`sort` 参数支持 `recent` | `featured` | `mine`（`mine` 需登录）
- `GET /api/shops/stats`：全局统计
- `GET /api/shops/{id}`：单店详情（含 GCS 签名 URL）
- `POST /api/shops` ⚿：创建店铺（自动绑定当前用户）
- `PUT /api/shops/{id}` ⚿、`DELETE /api/shops/{id}` ⚿

### 图片
- `POST /api/uploads` ⚿：上传封面（临时，JPG/PNG，≤10MB）
- `POST /api/shops/{id}/photos` ⚿：上传相册图
- `DELETE /api/shops/{id}/photos/{photo_id}` ⚿

> ⚿ 标注表示需要 `Authorization: Bearer <token>` 头

---

## 5. 数据模型

**User（`users`）**  
`id`（UUID）、`username`（唯一）、`hashed_password`、`created_at`。

**Shop（`shops`）**  
`id`（UUID）、`user_id`（FK → users，可空）、`name`、`prefecture`、`city`、`category`、`tag`、`address`、`phone`、`hours`、`lat`/`lng`、`cover_image`（GCS 对象路径）、`one_liner`、`description`、`rating`、`visit_date`、`featured`、`created_at`、`updated_at`。

**ShopPhoto（`shop_photos`）**  
`id`、`shop_id`、`url`（GCS 对象路径）、`sort_order`、`created_at`。

---

## 6. 图片存储（GCS）

- 图片上传至 GCS Bucket `sakura-photos-kudoushinichi`
- 数据库存储 **对象路径**（如 `shops/{id}/abc.jpg`）
- 后端使用 **Workload Identity**（VM 绑定 Service Account），无需密钥文件
- 返回给前端时生成 **V4 签名 URL**，有效期 7 天

---

## 7. 本地开发

### 环境要求
- Node.js 18+
- Python 3.11+
- MySQL 数据库
- GCS Bucket（本地可跳过，需在 config 中设置 `GCS_BUCKET_NAME`）

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填写实际值
uvicorn app.main:app --reload --port 8001
```

### 创建用户

```bash
cd backend
python scripts/create_user.py shinichi
```

### 前端

```bash
cd frontend
npm install
npm run dev   # 开发模式，访问 http://localhost:5173/
```

---

## 8. 生产部署（GCP 独立主机 + nginx）

### 前端构建

```bash
cd frontend
npm run build   # 产物在 frontend/dist/
```

将 `dist/` 内容复制到服务器 `/var/www/sakura/dist/`。

### 后端环境

```bash
cd /var/www/sakura/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填写生产值
```

### 启动服务

```bash
# 手动启动
bash start.sh

# 或使用 systemd（推荐）
sudo cp /var/www/sakura/sakura-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sakura-backend
```

### nginx 配置

将 `nginx-sakura.conf` 中的内容合并到服务器已有的 `server {}` 块中，然后：

```bash
sudo nginx -t && sudo nginx -s reload
```

### 首次创建用户

```bash
cd /var/www/sakura/backend
source .venv/bin/activate
python scripts/create_user.py shinichi
```

---

## 9. 环境变量（`backend/.env`）

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | `postgresql+asyncpg://用户@localhost/数据库名`（本地）或 `mysql+aiomysql://用户:密码@localhost/数据库名`（生产） |
| `SECRET_KEY` | JWT 签名密钥（随机 64 位十六进制，自行生成） |
| `ALLOWED_ORIGINS` | CORS 允许的域名（逗号分隔） |
| `BASE_URL` | 服务器域名 |
| `GCS_BUCKET_NAME` | GCS Bucket 名称 |

---

**文档版本**：v1.0（2026-05）
