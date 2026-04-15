# 桜探記（Sakura）

个人向的日本店铺与行程探访记录 Web 应用：展示封面图、简介、评分与相册，支持列表筛选与地图定位。仓库根目录名为 **Sakura**，前端在 **`frontend/`**，后端在 **`backend/`**。

---

## 1. 当前实现与产品定位

- **定位**：个人非商用，沉淀访日期间的店铺与景点记录，并以偏杂志感的界面呈现。
- **品牌与界面文案**：站点名为「桜探記」，界面以繁体中文为主（部分英文装饰文案）；后端 API 描述为中日混排。
- **已实现**：
  - 首页：瀑布/卡片流、排序（最新探访 / 评分 / 精选）、无限滚动、`/api/shops/stats` 展示店铺数与都道府县覆盖数。
  - 店铺列表 `/shops`：关键词搜索、大类筛选、都道府县筛选、 masonry 布局、无限滚动。
  - 店铺详情 `/shops/:id`：封面、元信息、相册灯箱、**MapLibre** 地图（Carto Voyager 底图）展示坐标。
  - 新增店铺 `/shops/new`：表单录入、封面与多图上传、地图选点；前端集成 **OpenStreetMap Nominatim** 正/逆地理编码，以及 GPS / IP 辅助定位（`ipapi.co`）。
- **未实现**（旧 PRD 中的规划，代码中暂无）：用户登录、JWT、后台 `/admin/*`、`/profile`、Docker 编排、图片按「门头/菜单」等分类、Prisma/Node 后端等。

---

## 2. 技术栈（与仓库一致）

### 前端（`frontend/`）

| 技术 | 说明 |
|------|------|
| Vite | 构建 |
| Vue 3 | Composition API |
| TypeScript | 类型 |
| Vue Router | 路由（见下表） |
| Pinia | 已接入（当前业务以 composable + API 为主） |
| Tailwind CSS | 样式（含 `sakura` 等主题色） |
| MapLibre GL | 详情页地图 |
| @vueuse/core 等 | 工具库 |
| ESLint + Prettier | 规范与格式化 |

### 后端（`backend/`）

| 技术 | 说明 |
|------|------|
| Python 3 | 运行时 |
| FastAPI | HTTP API |
| Uvicorn | ASGI 服务 |
| SQLAlchemy 2（async） + asyncpg | ORM 与异步 PostgreSQL 访问 |
| Pydantic v2 | 请求/响应模型（JSON 字段驼峰） |
| aiofiles | 异步写本地图片 |
| python-multipart | 上传解析 |

图片默认落在配置的本地目录，并通过 `GET /uploads/...` 提供访问；**未**接对象存储。

---

## 3. 前端路由（实际）

| 路径 | 说明 |
|------|------|
| `/` | 首页 |
| `/shops` | 店铺列表（支持 query：`q`、`type`、`pref`） |
| `/shops/new` | 新增店铺（表单 + 上传） |
| `/shops/:id` | 店铺详情 |

> 仓库中虽有 `AboutView.vue`，但未挂载到路由；`stores/counter.ts` 为脚手架遗留，可视为未使用。

---

## 4. 后端 API 概要

- `GET /`：健康检查 JSON。
- `GET /api/shops`：分页列表；查询参数含 `sort`（`recent` \| `rating` \| `featured`）、`category`、`prefecture`、`q`、`limit`、`offset`。
- `GET /api/shops/stats`：返回 `total`、`prefectures`。
- `GET /api/shops/{id}`：单店详情（含 `photos` URL 列表）。
- `POST /api/shops`：创建店铺（`category` 须为后端枚举的大类）。
- `PUT /api/shops/{id}`、`DELETE /api/shops/{id}`：更新、删除。
- `POST /api/uploads`：上传临时封面图，返回可访问 URL。
- `POST /api/shops/{shop_id}/photos`：多图上传至该店目录。
- `DELETE /api/shops/{shop_id}/photos/{photo_id}`：删除单张照片。

开发环境下 CORS 放行 `http://localhost:5173` 与 `4173`。

---

## 5. 数据模型（当前数据库）

**Shop（`shops`）**  
`id`（UUID）、`name`、`prefecture`、`city`、`category`（如：餐飲、購物等固定大类）、`tag`（细标签字符串）、`address`、`phone`、`hours`、`lat`/`lng`、`cover_image`、`one_liner`、`description`、`rating`、`visit_date`、`featured`、`created_at`、`updated_at`。

**ShopPhoto（`shop_photos`）**  
`id`、`shop_id`、`url`、`sort_order`、`created_at`。相册**无**「门头/菜单」等分类字段，仅排序。

---

## 6. 本地开发

### 环境要求

- Node.js（与当前锁文件兼容的版本）
- Python 3.11+（示例）
- PostgreSQL，以及 `backend/.env` 中的 `DATABASE_URL`（参见 `backend/app/config.py`）

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# 配置 .env：database_url、upload_dir、base_url 等
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
# 可选：.env.local 中设置 VITE_API_BASE_URL，默认 http://localhost:8000
npm run dev
```

默认前端开发地址：<http://localhost:5173>。

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 生产构建 |
| `npm run preview` | 预览构建结果 |
| `npm run lint` | ESLint |
| `npm run format` | Prettier |

---

## 7. 后续可演进方向（参考）

- 鉴权与仅管理员可写接口；独立后台路由与店铺编辑页。
- 生产部署：Docker、Nginx、HTTPS；图片迁对象存储。
- 相册分类、日文名字段、SEO 等与 PRD 对齐的扩展。

---

**文档版本**：与仓库实现同步（2026-04） · 若实现变更请优先更新本文件。
