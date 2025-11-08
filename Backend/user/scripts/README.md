# 数据库初始化脚本说明

## 📋 概述

本目录包含用于初始化用户数据库的脚本，包括创建用户表和创建默认管理员账户。

## 🗂️ 文件说明

### 1. `create_users_table.sql`
SQL脚本，用于手动创建用户表结构。

**使用方法：**
```bash
# 使用psql命令行工具
psql -U postgres -d supermap -f scripts/create_users_table.sql

# 或者使用pgAdmin等图形工具执行SQL脚本
```

### 2. `init_database.py`
Python脚本，使用SQLAlchemy自动创建表结构。

**使用方法：**
```bash
cd Backend/user
python scripts/init_database.py
```

**功能：**
- 自动创建所有表结构
- 验证表是否创建成功
- 显示表结构详情

### 3. `create_default_admin.py`
Python脚本，创建默认管理员账户。

**使用方法：**
```bash
cd Backend/user
python scripts/create_default_admin.py
```

**默认管理员账户：**
- 用户名: `admin`
- 邮箱: `admin@example.com`
- 密码: `admin123456`
- 权限: 超级用户（is_superuser = True）

⚠️ **重要提示：** 请在生产环境中修改默认密码！

## 🚀 快速开始

### 方法一：使用SQL脚本（推荐）

1. **创建数据库（如果不存在）**
```bash
psql -U postgres
CREATE DATABASE supermap;
\q
```

2. **执行SQL脚本创建表**
```bash
psql -U postgres -d supermap -f Backend/user/scripts/create_users_table.sql
```

3. **创建默认管理员（可选）**
```bash
cd Backend/user
python scripts/create_default_admin.py
```

### 方法二：使用Python脚本

1. **初始化数据库表**
```bash
cd Backend/user
python scripts/init_database.py
```

2. **创建默认管理员**
```bash
python scripts/create_default_admin.py
```

## 📊 用户表结构

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone BIGINT UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);
```

## 🔍 验证

### 检查表是否存在
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'users';
```

### 查看表结构
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

### 查看用户数据
```sql
SELECT id, username, email, is_active, is_superuser, created_at
FROM users;
```

## ⚙️ 配置

数据库连接配置在 `Backend/user/core/config.py` 中，可以通过环境变量或 `.env` 文件配置：

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=001117
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=supermap
```

## 🔧 故障排除

### 问题1: 表已存在
如果表已存在，SQL脚本会跳过创建。如果需要重新创建，请先删除：
```sql
DROP TABLE IF EXISTS users CASCADE;
```

### 问题2: 连接失败
检查：
1. PostgreSQL服务是否运行
2. 数据库配置是否正确
3. 用户权限是否足够

### 问题3: 权限不足
确保数据库用户有创建表的权限：
```sql
GRANT ALL PRIVILEGES ON DATABASE supermap TO postgres;
```

## 📝 注意事项

1. **生产环境**：请务必修改默认管理员密码
2. **备份**：在生产环境执行前请备份数据库
3. **权限**：确保数据库用户有足够的权限创建表和索引
4. **时区**：所有时间字段使用 `TIMESTAMP WITH TIME ZONE` 类型

