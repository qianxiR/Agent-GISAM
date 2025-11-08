"""
创建默认管理员账户脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import get_db_session
from infrastructure.database.postgres.repositories import PostgreSQLUserRepository
from domains.user.services import UserService
from application.use_cases.user.auth_use_case import AuthUseCase
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# 默认管理员账户配置
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123456",  # 请在生产环境中修改
    "is_superuser": True
}


async def create_default_admin():
    """创建默认管理员账户"""
    print("=" * 60)
    print("🔐 创建默认管理员账户...")
    print("=" * 60)
    
    # 先检查数据库连接
    print("\n🔍 检查数据库连接...")
    from core.config import settings
    import asyncpg
    
    try:
        test_conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        await test_conn.close()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print(f"\n请检查:")
        print(f"  1. PostgreSQL服务是否运行")
        print(f"  2. 数据库配置是否正确 (host={settings.postgres_host}, port={settings.postgres_port}, db={settings.postgres_db})")
        print(f"  3. 数据库是否存在")
        print(f"\n可以运行诊断脚本检查:")
        print(f"  python scripts/check_database_connection.py")
        return
    
    async with get_db_session() as session:
        try:
            # 创建仓储和服务
            user_repository = PostgreSQLUserRepository(session)
            user_service = UserService(user_repository)
            
            # 检查管理员是否已存在
            existing_user = await user_service.get_user_by_username(DEFAULT_ADMIN["username"])
            if existing_user:
                print(f"⚠️  管理员账户 '{DEFAULT_ADMIN['username']}' 已存在")
                print(f"   用户ID: {existing_user.id}")
                print(f"   邮箱: {existing_user.email}")
                print(f"   是否超级用户: {existing_user.is_superuser}")
                return
            
            # 创建管理员账户
            hashed_password = pwd_context.hash(DEFAULT_ADMIN["password"])
            
            # 先创建用户实体
            from domains.user.entities import UserEntity
            from uuid import uuid4
            admin_entity = UserEntity(
                id=uuid4(),
                email=DEFAULT_ADMIN["email"],
                username=DEFAULT_ADMIN["username"],
                hashed_password=hashed_password,
                phone=None,
                is_active=True,
                is_superuser=DEFAULT_ADMIN["is_superuser"]
            )
            
            # 保存到数据库
            admin_user = await user_repository.create(admin_entity)
            
            print(f"\n✅ 管理员账户创建成功！")
            print(f"   用户名: {DEFAULT_ADMIN['username']}")
            print(f"   邮箱: {DEFAULT_ADMIN['email']}")
            print(f"   密码: {DEFAULT_ADMIN['password']}")
            print(f"   用户ID: {admin_user.id}")
            print(f"\n⚠️  请在生产环境中修改默认密码！")
            
        except ValueError as e:
            print(f"❌ 创建失败: {e}")
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(create_default_admin())

