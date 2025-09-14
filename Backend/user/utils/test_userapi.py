#!/usr/bin/env python3
"""
API测试脚本
测试用户注册、登录和数据流入数据库
"""
import asyncio
import sys
import os
import httpx
import json
from datetime import datetime

# 添加项目根目录到 Python 路径（确保可导入 user 包）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录位于当前文件上两级目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 现在可以安全导入user模块
from core.config import get_settings

# API基础URL
settings = get_settings()
BASE_URL = "http://localhost:8088"  # 直接使用服务器地址
API_PREFIX = settings.api_v1_prefix  # 单独获取API前缀

# 测试用户数据
TEST_USER = {
    "username": f"testuser_{int(datetime.now().timestamp())}",
    "email": f"test_{int(datetime.now().timestamp())}@example.com",
    "phone": f"138{int(datetime.now().timestamp()) % 100000000:08d}",
    "password": "password",
    "confirm_password": "password"
}

# 默认账户数据
DEFAULT_USER = {
    "username": "admin",
    "email": "admin@example.com",
    "phone": "13800138000",
    "password": "123456",
    "confirm_password": "123456"
}

async def verify_config():
    """验证配置文件读取"""
    print("🔍 验证配置文件读取...")
    
    try:
        settings = get_settings()
        print(f"✅ 配置读取成功:")
        print(f"  应用名称: {settings.app_name}")
        print(f"  应用版本: {settings.app_version}")
        print(f"  调试模式: {settings.debug}")
        print(f"  环境: {settings.environment}")
        print(f"  API前缀: {settings.api_v1_prefix}")
        print(f"  数据库: {settings.postgres_db}")
        print(f"  数据库主机: {settings.postgres_host}")
        print(f"  数据库端口: {settings.postgres_port}")
        print(f"  数据库用户: {settings.postgres_user}")
        print(f"  数据库密码: {'*' * len(settings.postgres_password) if settings.postgres_password else '(未设置)'}")
        print(f"  BASE_URL: {BASE_URL}")
        print(f"  API_PREFIX: {API_PREFIX}")
        print(f"  完整API地址: {BASE_URL}{API_PREFIX}")
        return True
    except Exception as e:
        print(f"❌ 配置读取失败: {e}")
        return False


async def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查成功: {data}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False


async def test_user_register():
    """测试用户注册"""
    print(f"\n🔍 测试用户注册: {TEST_USER['username']}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/register",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 用户注册成功: {data}")
                return True
            else:
                print(f"❌ 用户注册失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return False


async def test_default_user_register():
    """测试默认账户注册"""
    print(f"\n🔍 测试默认账户注册: {DEFAULT_USER['username']}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/register",
                json=DEFAULT_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 默认账户注册成功: {data}")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                print(f"✅ 默认账户已存在，跳过注册")
                return True
            else:
                print(f"❌ 默认账户注册失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 默认账户注册异常: {e}")
            return False


async def test_default_user_login():
    """测试默认账户登录"""
    print(f"\n🔍 测试默认账户登录: {DEFAULT_USER['username']}...")
    
    login_data = {
        "login_identifier": DEFAULT_USER["username"],
        "password": DEFAULT_USER["password"]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 默认账户登录成功: {data}")
                return data.get("token")
            else:
                print(f"❌ 默认账户登录失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 默认账户登录异常: {e}")
            return None


async def test_user_login():
    """测试用户登录"""
    print(f"\n🔍 测试用户登录: {TEST_USER['username']}...")
    
    login_data = {
        "login_identifier": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 用户登录成功: {data}")
                return data.get("token")
            else:
                print(f"❌ 用户登录失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 用户登录异常: {e}")
            return None


async def test_user_login_wrong_password():
    """测试用户登录密码错误"""
    print(f"\n🔍 测试用户登录密码错误: {TEST_USER['username']}...")
    
    login_data = {
        "login_identifier": TEST_USER["username"],
        "password": "wrong_password_123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                data = response.json()
                print(f"✅ 密码错误测试成功: {data}")
                return True
            else:
                print(f"❌ 密码错误测试失败: 期望401，实际{response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 密码错误测试异常: {e}")
            return False


async def test_user_profile(token):
    """测试获取用户资料"""
    print(f"\n🔍 测试获取用户资料...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/user/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取用户资料成功: {data}")
                return True
            else:
                print(f"❌ 获取用户资料失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取用户资料异常: {e}")
            return False


async def test_get_user_info(token):
    """测试获取当前用户信息"""
    print(f"\n🔍 测试获取当前用户信息...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/user/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取用户信息成功: {data}")
                return True
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return False


async def test_get_user_stats(token):
    """测试获取用户统计信息"""
    print(f"\n🔍 测试获取用户统计信息...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/user/stats",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取用户统计成功: {data}")
                return True
            else:
                print(f"❌ 获取用户统计失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取用户统计异常: {e}")
            return False


async def test_update_user_profile(token):
    """测试修改用户资料"""
    print(f"\n🔍 测试修改用户资料...")
    
    # 先获取当前用户信息
    current_user_info = None
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}{API_PREFIX}/user/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                current_user_info = response.json().get("data", {})
            else:
                print(f"❌ 获取当前用户信息失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取当前用户信息异常: {e}")
            return False
    
    # 准备更新数据
    update_data = {
        "old_username": current_user_info.get("username", ""),
        "new_username": current_user_info.get("username", ""),  # 保持不变
        "old_email": current_user_info.get("email", ""),
        "new_email": f"updated_{int(datetime.now().timestamp())}@example.com",
        "old_phone": current_user_info.get("phone", ""),
        "new_phone": f"139{int(datetime.now().timestamp()) % 100000000:08d}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/update-profile",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 修改用户资料成功: {data}")
                return True
            else:
                print(f"❌ 修改用户资料失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 修改用户资料异常: {e}")
            return False


async def test_change_password(token):
    """测试修改密码"""
    print(f"\n🔍 测试修改密码...")
    
    password_data = {
        "current_password": TEST_USER["password"],
        "new_password": "newpassword123",
        "confirm_new_password": "newpassword123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/change-password",
                json=password_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 修改密码成功: {data}")
                # 更新测试用户的密码
                TEST_USER["password"] = "newpassword123"
                return True
            else:
                print(f"❌ 修改密码失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 修改密码异常: {e}")
            return False


async def test_user_logout(token):
    """测试用户登出"""
    print(f"\n🔍 测试用户登出...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}{API_PREFIX}/user/logout",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 用户登出成功: {data}")
                return True
            else:
                print(f"❌ 用户登出失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 用户登出异常: {e}")
            return False


async def test_database_verification():
    """验证数据库中的数据"""
    print(f"\n🔍 验证数据库中的数据...")
    
    try:
        from core.database import AsyncSessionLocal
        from infrastructure.database.postgres.models import UserModel
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            # 查询刚创建的用户
            stmt = select(UserModel).where(UserModel.username == TEST_USER["username"])
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"✅ 数据库验证成功:")
                print(f"  用户ID: {str(user.id)}")
                print(f"  用户名: {user.username}")
                print(f"  邮箱: {user.email}")
                print(f"  手机号: {user.phone}")
                print(f"  创建时间: {user.created_at}")
                return True
            else:
                print(f"❌ 数据库中未找到用户: {TEST_USER['username']}")
                return False
    except Exception as e:
        print(f"❌ 数据库验证异常: {e}")
        return False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("SuperMap GIS + AI Backend 用户认证系统完整测试")
    print("=" * 60)
    
    # 0. 验证配置读取
    print("\n📋 测试步骤 0/12: 配置验证")
    if not await verify_config():
        print("❌ 配置验证失败，请检查.env文件")
        return
    
    test_results = {
        "config_verification": True,
        "health_check": False,
        "default_user_register": False,
        "default_user_login": False,
        "user_register": False,
        "user_login": False,
        "user_login_wrong_password": False,
        "user_profile": False,
        "user_info": False,
        "user_stats": False,
        "update_profile": False,
        "change_password": False,
        "user_logout": False,
        "database_verification": False
    }
    
    # 1. 测试健康检查
    print("\n📋 测试步骤 1/13: 系统健康检查")
    test_results["health_check"] = await test_health_check()
    if not test_results["health_check"]:
        print("❌ 健康检查失败，请确保服务器正在运行")
        return
    
    # 2. 测试默认账户注册
    print("\n📋 测试步骤 2/13: 默认账户注册")
    test_results["default_user_register"] = await test_default_user_register()
    if not test_results["default_user_register"]:
        print("❌ 默认账户注册失败")
        return
    
    # 3. 测试默认账户登录
    print("\n📋 测试步骤 3/13: 默认账户登录")
    default_token = await test_default_user_login()
    if not default_token:
        print("❌ 默认账户登录失败")
        return
    test_results["default_user_login"] = True
    
    # 4. 测试用户注册
    print("\n📋 测试步骤 4/13: 用户注册")
    test_results["user_register"] = await test_user_register()
    if not test_results["user_register"]:
        print("❌ 用户注册失败")
        return
    
    # 5. 测试用户登录
    print("\n📋 测试步骤 5/13: 用户登录")
    token = await test_user_login()
    if not token:
        print("❌ 用户登录失败")
        return
    test_results["user_login"] = True
    
    # 6. 测试用户登录密码错误
    print("\n📋 测试步骤 6/13: 用户登录密码错误")
    test_results["user_login_wrong_password"] = await test_user_login_wrong_password()
    if not test_results["user_login_wrong_password"]:
        print("❌ 密码错误测试失败")
        return
    
    # 7. 测试获取用户资料
    print("\n📋 测试步骤 7/13: 获取用户资料")
    test_results["user_profile"] = await test_user_profile(token)
    if not test_results["user_profile"]:
        print("❌ 获取用户资料失败")
        return
    
    # 8. 测试获取当前用户信息
    print("\n📋 测试步骤 8/13: 获取当前用户信息")
    test_results["user_info"] = await test_get_user_info(token)
    if not test_results["user_info"]:
        print("❌ 获取用户信息失败")
        return
    
    # 9. 测试获取用户统计信息
    print("\n📋 测试步骤 9/13: 获取用户统计信息")
    test_results["user_stats"] = await test_get_user_stats(token)
    if not test_results["user_stats"]:
        print("❌ 获取用户统计失败")
        return
    
    # 10. 测试修改用户资料
    print("\n📋 测试步骤 10/13: 修改用户资料")
    test_results["update_profile"] = await test_update_user_profile(token)
    if not test_results["update_profile"]:
        print("❌ 修改用户资料失败")
        return
    
    # 11. 测试修改密码
    print("\n📋 测试步骤 11/13: 修改密码")
    test_results["change_password"] = await test_change_password(token)
    if not test_results["change_password"]:
        print("❌ 修改密码失败")
        return
    
    # 12. 测试用户登出
    print("\n📋 测试步骤 12/13: 用户登出")
    test_results["user_logout"] = await test_user_logout(token)
    if not test_results["user_logout"]:
        print("❌ 用户登出失败")
        return
    
    # 13. 验证数据库中的数据
    print("\n📋 测试步骤 13/13: 数据库验证")
    test_results["database_verification"] = await test_database_verification()
    if not test_results["database_verification"]:
        print("❌ 数据库验证失败")
        return
    
    # 测试结果统计
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print("\n" + "=" * 60)
    print("🎉 用户认证系统完整测试完成！")
    print("=" * 60)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    print(f"📈 成功率: {(passed_tests/total_tests)*100:.1f}%")
    print("\n✅ 已测试的API功能:")
    print("  ✅ 系统健康检查")
    print("  ✅ 默认账户注册 (POST /register)")
    print("  ✅ 默认账户登录 (POST /login)")
    print("  ✅ 用户注册 (POST /register)")
    print("  ✅ 用户登录 (POST /login)")
    print("  ✅ 密码错误验证 (POST /login)")
    print("  ✅ 获取用户资料 (GET /profile)")
    print("  ✅ 获取用户信息 (GET /me)")
    print("  ✅ 获取用户统计 (GET /stats)")
    print("  ✅ 修改用户资料 (POST /update-profile)")
    print("  ✅ 修改密码 (POST /change-password)")
    print("  ✅ 用户登出 (POST /logout)")
    print("  ✅ 数据库验证")
    print("\n🎯 用户认证系统 100% 功能测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
