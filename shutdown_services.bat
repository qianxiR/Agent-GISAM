@echo off
chcp 65001 >nul
echo ========================================
echo     SuperMap 全栈服务批量关闭脚本
echo     根目录: G:\1代码\开发\SuperMap
echo ========================================
echo.

:: 设置颜色
color 0C

:: 切换到项目根目录
cd /d "G:\1代码\开发\SuperMap"
echo [INFO] 当前工作目录: %CD%
echo.

echo [INFO] 正在关闭所有服务...
echo.

:: 关闭 Frontend 服务 (端口 5173)
echo [1/4] 关闭 Frontend 服务 (端口 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo 终止进程 %%a (Frontend 服务)
    taskkill /f /pid %%a >nul 2>&1
)

:: 关闭 Agent 服务 (端口 8089)
echo [2/4] 关闭 Agent 服务 (端口 8089)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8089') do (
    echo 终止进程 %%a (Agent 服务)
    taskkill /f /pid %%a >nul 2>&1
)

:: 关闭 User 服务 (端口 8088)
echo [3/4] 关闭 User 服务 (端口 8088)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8088') do (
    echo 终止进程 %%a (User 服务)
    taskkill /f /pid %%a >nul 2>&1
)

:: 关闭 Analysis 服务 (端口 8087)
echo [4/4] 关闭 Analysis 服务 (端口 8087)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8087') do (
    echo 终止进程 %%a (Analysis 服务)
    taskkill /f /pid %%a >nul 2>&1
)

:: 关闭 ngrok 隧道 (如果存在)
echo [5/5] 关闭 ngrok 隧道...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq ngrok.exe" /fo csv ^| findstr /v "INFO"') do (
    echo 终止 ngrok 进程 %%a
    taskkill /f /im ngrok.exe >nul 2>&1
)

:: 关闭所有相关的命令行窗口
echo [INFO] 关闭相关命令行窗口...
taskkill /f /fi "windowtitle eq Frontend Service*" >nul 2>&1
taskkill /f /fi "windowtitle eq Agent Service*" >nul 2>&1
taskkill /f /fi "windowtitle eq User Service*" >nul 2>&1
taskkill /f /fi "windowtitle eq Analysis Service*" >nul 2>&1
taskkill /f /fi "windowtitle eq ngrok tunnel*" >nul 2>&1

echo.
echo ========================================
echo     所有服务已关闭！
echo ========================================
echo.
echo 📍 项目根目录: G:\1代码\开发\SuperMap
echo.
echo ✅ 已关闭的服务:
echo    - Frontend 前端服务 (端口 5173)
echo    - Agent AI服务 (端口 8089)
echo    - User 用户服务 (端口 8088)
echo    - Analysis 分析服务 (端口 8087)
echo    - ngrok 隧道 (如果存在)
echo    - 相关命令行窗口
echo.
echo 💡 提示:
echo    - 所有服务已完全关闭
echo    - 相关进程和窗口已清理
echo    - 重新启动请运行 start_services.bat
echo.
echo 按任意键关闭此窗口...
pause >nul
