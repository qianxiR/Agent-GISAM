@echo off
chcp 65001 >nul
echo ========================================
echo     SuperMap 项目服务批量启动脚本
echo ========================================
echo.

::::::: 设置颜色
color 0A

echo [INFO] 当前工作目录: %~dp0
echo [INFO] 检查并终止占用端口的进程...
echo.

::::::: 关闭 Frontend 端口 (5173)
:FREE5173
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo 终止进程 %%a (端口 5173)
    taskkill /f /pid %%a >nul 2>&1
)
rem 验证端口是否已释放
netstat -ano | findstr :5173 >nul
if not errorlevel 1 (
    echo 端口 5173 仍被占用，重试释放...
    timeout /t 1 /nobreak >nul
    goto FREE5173
)

::::::: 关闭 Agent 端口 (8089)
echo 检查端口 8089...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8089') do (
    echo 终止进程 %%a (端口 8089)
    taskkill /f /pid %%a >nul 2>&1
)

::::::: 关闭 User 端口 (8088)
echo 检查端口 8088...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8088') do (
    echo 终止进程 %%a (端口 8088)
    taskkill /f /pid %%a >nul 2>&1
)

::::::: 关闭 Analysis 端口 (8087)
echo 检查端口 8087...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8087') do (
    echo 终止进程 %%a (端口 8087)
    taskkill /f /pid %%a >nul 2>&1
)

echo 端口检查与清理完成
echo.

::::::: 清理可能的端口缓存（可选）
netsh interface ip delete arpcache >nul 2>&1
ipconfig /flushdns >nul 2>&1

echo [INFO] 正在启动后端服务和前端服务...
echo.

goto FAST_START

:FAST_START
::::::: 启动 Analysis 服务 (Node.js)
echo [1/4] 启动 Analysis 服务 (Node.js)...
echo 路径: %~dp0Backend\analysis
start "Analysis Service" cmd /k "cd /d %~dp0Backend\analysis && echo 启动 Analysis 服务... && echo 当前目录: %CD% && npm run dev"

::::::: 等待2秒
timeout /t 2 /nobreak >nul

::::::: 启动 User 服务 (Python FastAPI)
echo [2/4] 启动 User 服务 (Python FastAPI)...
echo 路径: %~dp0Backend\user
start "User Service" cmd /k "cd /d %~dp0Backend\user && echo 激活 conda py310 环境... && conda activate py310 && echo 启动 User 服务... && echo 当前目录: %CD% && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8088"

::::::: 等待2秒
timeout /t 2 /nobreak >nul

::::::: 启动 Agent 服务 (Python FastAPI)
echo [3/4] 启动 Agent 服务 (Python FastAPI)...
echo 路径: %~dp0Backend
start "Agent Service" cmd /k "cd /d %~dp0Backend && echo 激活 conda py310 环境... && conda activate py310 && echo 启动 Agent 服务... && echo 当前目录: %CD% && python -m uvicorn agent.app:app --reload --host 0.0.0.0 --port 8089"

::::::: 等待2秒
timeout /t 2 /nobreak >nul

::::::: 启动 Frontend 服务 (Vue.js)
echo [4/4] 启动 Frontend 服务 (Vue.js)...
echo 路径: %~dp0Frontend
start "Frontend Service" cmd /k "cd /d %~dp0Frontend && echo 启动 Frontend 服务... && echo 当前目录: %CD% && npm run dev -- --port 5173 --strictPort --host"

echo.
echo ========================================
echo     服务启动完成！
echo ========================================
echo.
echo Analysis 服务: 运行在独立窗口 (http://localhost:8087)
echo User 服务: 运行在独立窗口 (http://localhost:8088)
echo Agent 服务: 运行在独立窗口 (http://localhost:8089)
echo Frontend 服务: 运行在独立窗口 (http://localhost:5173)
echo.
echo 🚀 Agent服务功能:
echo    - LLM聊天 (自动注入prompt.md): http://localhost:8089/agent/chat
echo    - API密钥管理: http://localhost:8089/api/v1/api-keys
echo    - 提示词管理: http://localhost:8089/api/v1/prompts
echo    - 知识库管理: http://localhost:8089/api/v1/知识库
echo    - API文档: http://localhost:8089/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
