"""
数据库初始化脚本
用于创建用户表结构
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from core.database import engine, Base
from infrastructure.database.postgres.models import UserModel
from core.config import settings


async def init_database():
    """初始化数据库表结构"""
    print("=" * 60)
    print("🚀 开始初始化数据库...")
    print(f"📊 数据库: {settings.postgres_db}")
    print(f"🔗 连接: {settings.postgres_host}:{settings.postgres_port}")
    print("=" * 60)
    
    try:
        # 创建所有表
        async with engine.begin() as conn:
            print("\n📝 正在创建表结构...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ 表结构创建成功！")
            
            # 验证表是否存在
            print("\n🔍 验证表结构...")
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            """))
            table_exists = result.fetchone()
            
            if table_exists:
                print("✅ users 表已存在")
                
                # 检查表结构
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                print("\n📋 表结构详情:")
                print("-" * 60)
                for col in columns:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    print(f"  {col[0]:<25} {col[1]:<20} {nullable}")
                print("-" * 60)
            else:
                print("❌ users 表不存在")
                
        print("\n" + "=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())

