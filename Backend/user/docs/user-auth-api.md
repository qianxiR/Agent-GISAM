# 用户认证API使用文档

## 📋 概述

用户认证API提供完整的用户账户管理功能，包括注册、登录、资料管理、密码修改等操作。所有接口都支持JSON格式的请求和响应。

**基础URL**: `http://localhost:8089/api/v1/user`

---

## 🔐 1. 用户注册

### 接口信息
- **URL**: `POST /api/v1/user/register`
- **描述**: 新用户注册，创建账户
- **认证**: 无需认证

### 请求参数

```json
{
  "username": "testuser",
  "email": "test@example.com", 
  "phone": "13800138000",
  "password": "password123",
  "confirm_password": "password123"
}
```

| 字段 | 类型 | 必填 | 说明 | 验证规则 |
|------|------|------|------|----------|
| `username` | string | ✅ | 用户名 | 2-50个字符 |
| `email` | string | ✅ | 邮箱地址 | 有效邮箱格式 |
| `phone` | string | ❌ | 手机号码 | 可选 |
| `password` | string | ✅ | 密码 | 6-100个字符 |
| `confirm_password` | string | ✅ | 确认密码 | 必须与password一致 |

### 响应示例

**成功响应 (200)**:
```json
{
  "success": true,
  "message": "用户注册成功",
  "data": {
    "username": "testuser"
  }
}
```

**错误响应 (400)**:
```json
{
  "detail": "密码和确认密码不匹配"
}
```

### 使用示例

```bash
# curl 示例
curl -X POST "http://localhost:8089/api/v1/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000", 
    "password": "password123",
    "confirm_password": "password123"
  }'

# PowerShell 示例
$body = @{
    username = "testuser"
    email = "test@example.com"
    phone = "13800138000"
    password = "password123"
    confirm_password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8089/api/v1/user/register" -Method POST -Body $body -ContentType "application/json"
```

---

## 🔑 2. 用户登录

### 接口信息
- **URL**: `POST /api/v1/user/login`
- **描述**: 用户登录并获取访问令牌
- **认证**: 无需认证

### 请求参数

```json
{
  "login_identifier": "testuser",
  "password": "password123"
}
```

| 字段 | 类型 | 必填 | 说明 | 验证规则 |
|------|------|------|------|----------|
| `login_identifier` | string | ✅ | 登录标识 | 支持用户名/邮箱/手机号 |
| `password` | string | ✅ | 密码 | 不能为空 |

### 响应示例

**成功响应 (200)**:
```json
{
  "success": true,
  "message": "登录成功",
  "token": "dummy_token_here",
  "data": {
    "username": "testuser"
  }
}
```

**错误响应 (401)**:
```json
{
  "detail": "用户名/邮箱/手机号不存在"
}
```

```json
{
  "detail": "密码错误"
}
```

### 使用示例

```bash
# 使用用户名登录
curl -X POST "http://localhost:8089/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "testuser",
    "password": "password123"
  }'

# 使用邮箱登录
curl -X POST "http://localhost:8089/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "test@example.com",
    "password": "password123"
  }'

# 使用手机号登录
curl -X POST "http://localhost:8089/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "13800138000",
    "password": "password123"
  }'
```

---

## 👤 3. 获取用户资料

### 接口信息
- **URL**: `GET /api/v1/user/profile`
- **描述**: 获取当前用户的详细资料
- **认证**: 需要认证

### 请求参数
无

### 响应示例

**成功响应 (200)**:
```json
{
  "id": 1,
  "username": "test_user",
  "email": "test@example.com",
  "phone": "13800138000",
  "is_active": true,
  "registered_at": "2024-01-15T10:30:00Z"
}
```

### 使用示例

```bash
curl -X GET "http://localhost:8089/api/v1/user/profile" \
  -H "Authorization: Bearer your_token_here"
```

---

## 👤 4. 获取当前用户信息

### 接口信息
- **URL**: `GET /api/v1/user/me`
- **描述**: 获取当前登录用户的基本信息
- **认证**: 需要认证

### 请求参数
无

### 响应示例

**成功响应 (200)**:
```json
{
  "id": 1,
  "username": "test_user",
  "email": "test@example.com",
  "phone": "13800138000",
  "is_active": true,
  "registered_at": "2024-01-15T10:30:00Z"
}
```

### 使用示例

```bash
curl -X GET "http://localhost:8089/api/v1/user/me" \
  -H "Authorization: Bearer your_token_here"
```

---

## 📊 5. 获取用户统计信息

### 接口信息
- **URL**: `GET /api/v1/user/stats`
- **描述**: 获取系统用户统计信息
- **认证**: 需要认证

### 请求参数
无

### 响应示例

**成功响应 (200)**:
```json
{
  "success": true,
  "message": "统计信息获取成功",
  "data": {
    "total_users": 100,
    "active_users": 80,
    "new_users_today": 5
  }
}
```

### 使用示例

```bash
curl -X GET "http://localhost:8089/api/v1/user/stats" \
  -H "Authorization: Bearer your_token_here"
```

---

## 🔄 6. 修改用户信息

### 接口信息
- **URL**: `POST /api/v1/user/update-profile`
- **描述**: 修改用户名、邮箱或手机号
- **认证**: 需要认证

### 请求参数

```json
{
  "old_username": "qianxi",
  "new_username": "qianxi_new",
  "old_email": "qianxi111@126.com",
  "new_email": "qianxi_new@126.com",
  "old_phone": "13800138000",
  "new_phone": "13900139000"
}
```

| 字段 | 类型 | 必填 | 说明 | 验证规则 |
|------|------|------|------|----------|
| `old_username` | string | ✅ | 原用户名 | 必须与当前用户名一致 |
| `new_username` | string | ❌ | 新用户名 | 2-50个字符，可选 |
| `old_email` | string | ✅ | 原邮箱 | 必须与当前邮箱一致 |
| `new_email` | string | ❌ | 新邮箱 | 有效邮箱格式，可选 |
| `old_phone` | string | ❌ | 原手机号 | 可选 |
| `new_phone` | string | ❌ | 新手机号 | 可选 |

### 响应示例

**成功响应 (200)**:
```json
{
  "success": true,
  "message": "用户信息修改成功",
  "data": {
    "old_info": {
      "username": "qianxi",
      "email": "qianxi111@126.com",
      "phone": "13800138000"
    },
    "new_info": {
      "username": "qianxi_new",
      "email": "qianxi_new@126.com",
      "phone": "13900139000"
    }
  }
}
```

**错误响应 (400)**:
```json
{
  "detail": "原用户信息不匹配，请检查输入"
}
```

```json
{
  "detail": "新用户名已存在"
}
```

### 使用示例

```bash
# 完整修改
curl -X POST "http://localhost:8089/api/v1/user/update-profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "old_username": "qianxi",
    "new_username": "qianxi_new",
    "old_email": "qianxi111@126.com",
    "new_email": "qianxi_new@126.com",
    "old_phone": "13800138000",
    "new_phone": "13900139000"
  }'

# 只修改用户名
curl -X POST "http://localhost:8089/api/v1/user/update-profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "old_username": "qianxi",
    "new_username": "qianxi_new",
    "old_email": "qianxi111@126.com",
    "old_phone": "13800138000"
  }'

# 只修改邮箱
curl -X POST "http://localhost:8089/api/v1/user/update-profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "old_username": "qianxi",
    "old_email": "qianxi111@126.com",
    "new_email": "qianxi_new@126.com",
    "old_phone": "13800138000"
  }'
```

---

## 🔐 7. 修改密码

### 接口信息
- **URL**: `POST /api/v1/user/change-password`
- **描述**: 修改用户密码，需要当前密码验证
- **认证**: 需要认证

### 请求参数

```json
{
  "current_password": "qianxi147A",
  "new_password": "qianxi147B",
  "confirm_new_password": "qianxi147B"
}
```

| 字段 | 类型 | 必填 | 说明 | 验证规则 |
|------|------|------|------|----------|
| `current_password` | string | ✅ | 当前密码 | 不能为空 |
| `new_password` | string | ✅ | 新密码 | 6-100个字符 |
| `confirm_new_password` | string | ✅ | 确认新密码 | 必须与new_password一致 |

### 响应示例

**成功响应 (200)**:
```json
{
  "success": true,
  "message": "密码修改成功",
  "data": {
    "username": "qianxi",
    "message": "密码已更新，请使用新密码登录"
  }
}
```

**错误响应 (401)**:
```json
{
  "detail": "当前密码错误"
}
```

**错误响应 (400)**:
```json
{
  "detail": "新密码和确认密码不匹配"
}
```

```json
{
  "detail": "新密码不能与当前密码相同"
}
```

### 使用示例

```bash
curl -X POST "http://localhost:8089/api/v1/user/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "current_password": "qianxi147A",
    "new_password": "qianxi147B",
    "confirm_new_password": "qianxi147B"
  }'
```

---

## 🚪 8. 用户登出

### 接口信息
- **URL**: `POST /api/v1/user/logout`
- **描述**: 用户登出，清除会话
- **认证**: 需要认证

### 请求参数
无

### 响应示例

**成功响应 (200)**:
```json
{
  "success": true,
  "message": "登出成功，已清除用户会话"
}
```

### 使用示例

```bash
curl -X POST "http://localhost:8089/api/v1/user/logout" \
  -H "Authorization: Bearer your_token_here"
```

---

## 🔧 错误处理

### 常见HTTP状态码

| 状态码 | 说明 | 常见原因 |
|--------|------|----------|
| `200` | 成功 | 请求处理成功 |
| `400` | 请求错误 | 参数验证失败、数据格式错误 |
| `401` | 未授权 | 认证失败、令牌无效 |
| `403` | 禁止访问 | 权限不足 |
| `404` | 未找到 | 接口不存在 |
| `500` | 服务器错误 | 内部服务器错误 |

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

---

## 🧪 测试数据

### 预置测试用户

系统包含以下测试用户，可用于API测试：

| 用户名 | 邮箱 | 手机号 | 密码 |
|--------|------|--------|------|
| `qianxi` | `qianxi111@126.com` | `13800138000` | `qianxi147A` |
| `testuser` | `test@example.com` | `13800138000` | `password123` |

### 测试流程示例

```bash
# 1. 用户注册
curl -X POST "http://localhost:8089/api/v1/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "phone": "13900139000",
    "password": "newpassword123",
    "confirm_password": "newpassword123"
  }'

# 2. 用户登录
curl -X POST "http://localhost:8089/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "newuser",
    "password": "newpassword123"
  }'

# 3. 获取用户信息（使用返回的token）
curl -X GET "http://localhost:8089/api/v1/user/me" \
  -H "Authorization: Bearer your_token_here"

# 4. 修改用户信息
curl -X POST "http://localhost:8089/api/v1/user/update-profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "old_username": "newuser",
    "new_username": "updateduser",
    "old_email": "newuser@example.com",
    "new_email": "updateduser@example.com",
    "old_phone": "13900139000",
    "new_phone": "13900139001"
  }'

# 5. 修改密码
curl -X POST "http://localhost:8089/api/v1/user/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "current_password": "newpassword123",
    "new_password": "updatedpassword123",
    "confirm_new_password": "updatedpassword123"
  }'

# 6. 用户登出
curl -X POST "http://localhost:8089/api/v1/user/logout" \
  -H "Authorization: Bearer your_token_here"
```

---

## 📝 注意事项

1. **认证要求**: 除注册和登录外，其他接口都需要在请求头中包含有效的认证令牌
2. **数据验证**: 所有输入数据都会进行格式和内容验证
3. **密码安全**: 密码至少6个字符，建议使用复杂密码
4. **邮箱格式**: 邮箱地址会自动转换为小写并去除首尾空格
5. **用户名唯一性**: 用户名在系统中必须唯一
6. **手机号可选**: 手机号字段为可选，但建议填写
7. **令牌管理**: 登录成功后请妥善保存返回的令牌
8. **错误处理**: 请根据返回的错误信息进行相应的处理

---

## 🔗 相关链接

- [API文档 (Swagger UI)](http://localhost:8089/docs)
- [API文档 (ReDoc)](http://localhost:8089/redoc)
- [健康检查](http://localhost:8089/health)
- [项目README](../README.md)
