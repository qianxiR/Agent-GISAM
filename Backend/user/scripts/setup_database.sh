#!/bin/bash
# 数据库一键初始化脚本（Linux/Mac）

echo "=========================================="
echo "🚀 数据库初始化脚本"
echo "=========================================="

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装，请先安装Python"
    exit 1
fi

# 进入脚本目录
cd "$(dirname "$0")/.."

echo ""
echo "📝 步骤1: 创建数据库表结构..."
python scripts/init_database.py

if [ $? -eq 0 ]; then
    echo ""
    echo "📝 步骤2: 创建默认管理员账户..."
    python scripts/create_default_admin.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "✅ 数据库初始化完成！"
        echo "=========================================="
        echo ""
        echo "默认管理员账户："
        echo "  用户名: admin"
        echo "  邮箱: admin@example.com"
        echo "  密码: admin123456"
        echo ""
        echo "⚠️  请在生产环境中修改默认密码！"
    else
        echo "❌ 创建管理员账户失败"
        exit 1
    fi
else
    echo "❌ 创建数据库表失败"
    exit 1
fi

