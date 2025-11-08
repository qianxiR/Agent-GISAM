@echo off
REM 数据库一键初始化脚本（Windows）

echo ==========================================
echo 🚀 数据库初始化脚本
echo ==========================================

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python
    exit /b 1
)

REM 进入脚本目录
cd /d "%~dp0\.."

echo.
echo 📝 步骤1: 创建数据库表结构...
python scripts\init_database.py

if %errorlevel% equ 0 (
    echo.
    echo 📝 步骤2: 创建默认管理员账户...
    python scripts\create_default_admin.py
    
    if %errorlevel% equ 0 (
        echo.
        echo ==========================================
        echo ✅ 数据库初始化完成！
        echo ==========================================
        echo.
        echo 默认管理员账户：
        echo   用户名: admin
        echo   邮箱: admin@example.com
        echo   密码: admin123456
        echo.
        echo ⚠️  请在生产环境中修改默认密码！
    ) else (
        echo ❌ 创建管理员账户失败
        exit /b 1
    )
) else (
    echo ❌ 创建数据库表失败
    exit /b 1
)

pause

