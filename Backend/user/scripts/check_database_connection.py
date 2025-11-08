"""
数据库连接诊断脚本
用于检查数据库连接配置和连接状态
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import settings
import asyncpg


async def check_database_connection():
    """检查数据库连接"""
    print("=" * 60)
    print("🔍 数据库连接诊断")
    print("=" * 60)
    
    # 显示配置信息
    print("\n📋 数据库配置:")
    print(f"  主机: {settings.postgres_host}")
    print(f"  端口: {settings.postgres_port}")
    print(f"  数据库: {settings.postgres_db}")
    print(f"  用户: {settings.postgres_user}")
    print(f"  密码: {'*' * len(settings.postgres_password)}")
    print(f"  连接URL: postgresql://{settings.postgres_user}:***@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    
    # 测试连接
    print("\n🔌 测试数据库连接...")
    try:
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        
        print("✅ 数据库连接成功！")
        
        # 检查数据库版本
        version = await conn.fetchval('SELECT version()')
        print(f"\n📊 PostgreSQL版本:")
        print(f"   {version.split(',')[0]}")
        
        # 检查数据库是否存在
        db_exists = await conn.fetchval("""
            SELECT 1 FROM pg_database WHERE datname = $1
        """, settings.postgres_db)
        
        if db_exists:
            print(f"\n✅ 数据库 '{settings.postgres_db}' 存在")
        else:
            print(f"\n❌ 数据库 '{settings.postgres_db}' 不存在")
            print(f"   请先创建数据库:")
            print(f"   CREATE DATABASE {settings.postgres_db};")
        
        # 检查users表是否存在
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """)
        
        if table_exists:
            print(f"\n✅ users 表已存在")
            
            # 获取表记录数
            count = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"   当前用户数: {count}")
        else:
            print(f"\n⚠️  users 表不存在")
            print(f"   请先运行初始化脚本创建表:")
            print(f"   python scripts/init_database.py")
        
        await conn.close()
        print("\n" + "=" * 60)
        print("✅ 诊断完成")
        print("=" * 60)
        return True
        
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ 数据库密码错误")
        print("   请检查 .env 文件中的 POSTGRES_PASSWORD 配置")
        return False
    except asyncpg.exceptions.InvalidCatalogNameError:
        print(f"❌ 数据库 '{settings.postgres_db}' 不存在")
        print(f"   请先创建数据库:")
        print(f"   CREATE DATABASE {settings.postgres_db};")
        return False
    except asyncpg.exceptions.ConnectionRefusedError:
        print("❌ 无法连接到数据库服务器")
        print("   请检查:")
        print(f"   1. PostgreSQL服务是否运行")
        print(f"   2. 主机地址是否正确: {settings.postgres_host}")
        print(f"   3. 端口是否正确: {settings.postgres_port}")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}")
        print(f"   错误信息: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(check_database_connection())
    sys.exit(0 if success else 1)

