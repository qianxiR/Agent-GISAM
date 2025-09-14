# 用户认证API 快速参考

## 🚀 快速开始

### 基础URL
```
http://localhost:8089/api/v1/user
```

### 测试用户
| 用户名 | 邮箱 | 手机号 | 密码 |
|--------|------|--------|------|
| `qianxi` | `qianxi111@126.com` | `13800138000` | `qianxi147A` |

---

## 📋 API 接口速查表

| 功能 | 方法 | 路径 | 认证 | 描述 |
|------|------|------|------|------|
| **注册** | POST | `/register` | ❌ | 新用户注册 |
| **登录** | POST | `/login` | ❌ | 用户登录 |
| **获取资料** | GET | `/profile` | ✅ | 获取用户资料 |
| **获取信息** | GET | `/me` | ✅ | 获取当前用户信息 |
| **统计信息** | GET | `/stats` | ✅ | 获取用户统计 |
| **修改信息** | POST | `/update-profile` | ✅ | 修改用户信息 |
| **修改密码** | POST | `/change-password` | ✅ | 修改密码 |
| **登出** | POST | `/logout` | ✅ | 用户登出 |

---

## 🔐 认证方式

### 请求头格式
```bash
Authorization: Bearer your_token_here
```

### 获取令牌
```bash
# 登录获取令牌
curl -X POST "http://localhost:8089/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "qianxi",
    "password": "qianxi147A"
  }'
```

---

## 📝 常用请求示例

### 1. 用户注册
```bash
curl -X POST "http://localhost:8089/api/v1/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "phone": "13900139000",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

### 2. 用户登录
```bash
curl -X POST "http://localhost:8089/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "qianxi",
    "password": "qianxi147A"
  }'
```

### 3. 获取用户信息
```bash
curl -X GET "http://localhost:8089/api/v1/user/me" \
  -H "Authorization: Bearer your_token_here"
```

### 4. 修改用户信息
```bash
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
```

### 5. 修改密码
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

### 6. 用户登出
```bash
curl -X POST "http://localhost:8089/api/v1/user/logout" \
  -H "Authorization: Bearer your_token_here"
```

---

## ⚡ PowerShell 示例

### 用户注册
```powershell
$body = @{
    username = "newuser"
    email = "newuser@example.com"
    phone = "13900139000"
    password = "password123"
    confirm_password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8089/api/v1/user/register" -Method POST -Body $body -ContentType "application/json"
```

### 用户登录
```powershell
$body = @{
    login_identifier = "qianxi"
    password = "qianxi147A"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8089/api/v1/user/login" -Method POST -Body $body -ContentType "application/json"
$token = $response.token
```

### 获取用户信息
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8089/api/v1/user/me" -Method GET -Headers $headers
```

---

## 🔧 错误代码速查

| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| `200` | 成功 | - |
| `400` | 请求错误 | 检查参数格式和验证规则 |
| `401` | 未授权 | 检查认证令牌是否正确 |
| `404` | 未找到 | 检查API路径是否正确 |
| `500` | 服务器错误 | 联系管理员 |

---

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 错误响应
```json
{
  "detail": "错误描述信息"
}
```

---

## 🎯 完整测试流程

```bash
# 1. 启动服务
python -m uvicorn user.main:app --reload --host 0.0.0.0 --port 8000

# 2. 用户注册
curl -X POST "http://localhost:8089/api/v1/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "password": "password123",
    "confirm_password": "password123"
  }'

# 3. 用户登录
curl -X POST "http://localhost:8089/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "testuser",
    "password": "password123"
  }'

# 4. 获取用户信息
curl -X GET "http://localhost:8089/api/v1/user/me" \
  -H "Authorization: Bearer your_token_here"

# 5. 修改用户信息
curl -X POST "http://localhost:8089/api/v1/user/update-profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "old_username": "testuser",
    "new_username": "updateduser",
    "old_email": "test@example.com",
    "new_email": "updated@example.com",
    "old_phone": "13800138000",
    "new_phone": "13900139000"
  }'

# 6. 修改密码
curl -X POST "http://localhost:8089/api/v1/user/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "current_password": "password123",
    "new_password": "newpassword123",
    "confirm_new_password": "newpassword123"
  }'

# 7. 用户登出
curl -X POST "http://localhost:8089/api/v1/user/logout" \
  -H "Authorization: Bearer your_token_here"
```

---

## 🔗 相关文档

- [详细API文档](./user-auth-api.md)
- [Swagger UI](http://localhost:8089/docs)
- [ReDoc](http://localhost:8089/redoc)
- [项目README](../README.md)
