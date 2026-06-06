# 莆田剪纸合作社在线商城 - 数据库ER图

## 实体关系图 (Mermaid)

```mermaid
erDiagram
    users ||--o{ orders : "下单"
    users ||--o{ notifications : "接收"
    users ||--o| artisans : "关联匠人"

    products ||--o{ orders : "被订购"
    products ||--o{ product_images : "拥有图片"

    orders ||--o{ order_assignments : "分配匠人"
    orders ||--o{ order_progress_photos : "进度照片"

    artisans ||--o{ order_assignments : "接单"
    artisans ||--o{ artisan_schedules : "排期"

    users {
        int id PK
        varchar username UK
        varchar email UK
        varchar password_hash
        enum role "customer|artisan|admin"
        varchar phone
        varchar avatar_url
        datetime created_at
        int version "乐观锁"
    }

    products {
        int id PK
        varchar name
        text description
        enum category "wedding|enterprise|festival|custom"
        varchar template_image_url
        float price_base
        boolean is_template
        int stock
        int version "乐观锁"
        datetime created_at
    }

    product_images {
        int id PK
        int product_id FK
        varchar image_url
        int sort_order
    }

    orders {
        int id PK
        varchar order_no UK
        int customer_id FK
        int product_id FK
        enum status "pending|assigned|in_progress|qc|shipped|completed|cancelled"
        float total_price
        varchar custom_size
        varchar custom_color
        text custom_message
        varchar reference_image_url
        boolean is_original
        int version "乐观锁"
        datetime created_at
        datetime updated_at
    }

    order_assignments {
        int id PK
        int order_id FK
        int artisan_id FK
        datetime assigned_at
        datetime deadline
    }

    order_progress_photos {
        int id PK
        int order_id FK
        int uploaded_by
        varchar image_url
        text description
        datetime uploaded_at
    }

    artisans {
        int id PK
        int user_id FK UK
        varchar name
        varchar specialty
        int monthly_capacity
        text bio
        varchar avatar_url
    }

    artisan_schedules {
        int id PK
        int artisan_id FK
        int year_month
        int assigned_count
        int capacity
        int version "乐观锁"
    }

    notifications {
        int id PK
        int user_id FK
        varchar title
        text content
        enum type "order_status"
        boolean is_read
        datetime created_at
    }
```

## 乐观锁机制说明

### 库存乐观锁
下单时通过 `version` 字段防止超卖：
```sql
UPDATE products
SET stock = stock - 1, version = version + 1
WHERE id = :id AND version = :version AND stock > 0;
-- 若影响行数为0，说明库存不足或version已被修改，抛出异常
```

### 匠人排期乐观锁
分配匠人时通过 `version` 字段防止超过产能上限：
```sql
UPDATE artisan_schedules
SET assigned_count = assigned_count + 1, version = version + 1
WHERE artisan_id = :artisan_id AND year_month = :year_month
  AND version = :version AND assigned_count < capacity;
-- 若影响行数为0，说明匠人当月产能已满，抛出异常
```

### 订单状态乐观锁
订单状态变更同样使用 `version` 字段，防止并发修改冲突：
```sql
UPDATE orders SET status = :new_status, version = version + 1, updated_at = NOW()
WHERE id = :id AND version = :version;
```
