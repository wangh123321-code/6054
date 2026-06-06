# 莆田剪纸合作社在线商城 - API接口文档

## 基础信息

- 基础URL: `http://localhost:8000`
- 交互式文档: `http://localhost:8000/docs` (Swagger UI)
- 认证方式: Bearer Token (JWT)
- Token获取: 登录接口返回 `access_token`，后续请求头加 `Authorization: Bearer <token>`

---

## 1. 认证模块 `/api/auth`

### POST /api/auth/register
注册新用户

**请求体:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "customer | artisan | admin",
  "phone": "string (可选)"
}
```

**响应 200:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "role": "customer",
  "phone": "string",
  "avatar_url": "string",
  "created_at": "2026-06-05T00:00:00"
}
```

### POST /api/auth/login
用户登录

**请求体:**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应 200:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

## 2. 产品模块 `/api/products`

### GET /api/products
获取产品列表

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 筛选分类: wedding/enterprise/festival/custom |

**响应 200:** `ProductListOut[]`
```json
[
  {
    "id": 1,
    "name": "龙凤呈祥双喜",
    "category": "wedding",
    "template_image_url": "string",
    "price_base": 298.0,
    "is_template": true,
    "stock": 50
  }
]
```

### GET /api/products/{product_id}
获取产品详情

**路径参数:** product_id (int)

**响应 200:** `ProductOut`
```json
{
  "id": 1,
  "name": "龙凤呈祥双喜",
  "description": "传统婚庆剪纸...",
  "category": "wedding",
  "template_image_url": "string",
  "price_base": 298.0,
  "is_template": true,
  "stock": 50,
  "version": 1,
  "created_at": "2026-06-05T00:00:00",
  "images": []
}
```

### POST /api/products
创建产品 (需管理员权限)

**请求体:** `ProductCreate`
```json
{
  "name": "string",
  "description": "string",
  "category": "wedding | enterprise | festival | custom",
  "template_image_url": "string",
  "price_base": 0.0,
  "is_template": true,
  "stock": 0
}
```

### PUT /api/products/{product_id}
更新产品 (需管理员权限)

**请求体:** 同创建

---

## 3. 订单模块 `/api/orders`

### POST /api/orders
下单 (需登录)

**请求体:** `OrderCreate`
```json
{
  "product_id": 1,
  "total_price": 328.0,
  "custom_size": "50cm",
  "custom_color": "中国红",
  "custom_message": "百年好合",
  "reference_image_url": "string",
  "is_original": false
}
```

**乐观锁说明:** 下单时自动检查库存，使用version字段实现乐观锁：
```sql
UPDATE products SET stock=stock-1, version=version+1
WHERE id=? AND version=? AND stock>0
```
若影响行数为0，返回400错误"库存不足或产品已被修改，请重试"

**响应 201:** `OrderOut`

### GET /api/orders
获取我的订单列表 (需登录)

### GET /api/orders/{order_id}
获取订单详情 (需登录，仅订单所有者/管理员/匠人可查看)

### PUT /api/orders/{order_id}/status
变更订单状态 (需管理员/匠人权限)

**请求体:**
```json
{
  "status": "pending | assigned | in_progress | qc | shipped | completed | cancelled"
}
```

状态变更后自动通过Celery异步任务发送站内通知给客户。

### POST /api/orders/{order_id}/assign
分配匠人 (需管理员权限)

**请求体:**
```json
{
  "artisan_id": 1,
  "deadline": "2026-07-01T00:00:00"
}
```

**乐观锁说明:** 分配匠人时检查当月排期，使用version字段实现乐观锁：
```sql
UPDATE artisan_schedules SET assigned_count=assigned_count+1, version=version+1
WHERE artisan_id=? AND year_month=? AND version=? AND assigned_count<capacity
```
若影响行数为0，返回400错误"匠人当月产能已满"

### POST /api/orders/{order_id}/progress-photo
匠人上传制作进度照片 (需匠人/管理员权限)

**请求体 (Form Data):**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image_url | string | 是 | 照片URL |
| description | string | 否 | 描述 |

### GET /api/orders/{order_id}/progress-photos
获取订单进度照片

---

## 4. 匠人模块 `/api/artisans`

### GET /api/artisans
获取匠人列表

### GET /api/artisans/{artisan_id}/schedule
获取匠人排期

**响应:** `ArtisanScheduleOut[]`
```json
[
  {
    "id": 1,
    "artisan_id": 1,
    "year_month": 202606,
    "assigned_count": 15,
    "capacity": 20,
    "version": 3
  }
]
```

### GET /api/artisans/{artisan_id}/tasks
获取匠人任务列表

**响应:** `ArtisanTaskOut[]`
```json
[
  {
    "order_id": 1,
    "order_no": "PC20260605120000000001",
    "status": "in_progress",
    "assigned_at": "2026-06-05T00:00:00",
    "deadline": "2026-06-20T00:00:00"
  }
]
```

---

## 5. 通知模块 `/api/notifications`

### GET /api/notifications
获取我的通知列表 (需登录)

### PUT /api/notifications/{notification_id}/read
标记通知为已读

### GET /api/notifications/unread-count
获取未读通知数量

**响应:**
```json
{
  "unread_count": 3
}
```

---

## 6. 健康检查

### GET /api/health
```json
{"status": "ok"}
```
