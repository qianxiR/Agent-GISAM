@echo off
chcp 65001 >nul
echo ========================================
echo     SuperMap 全栈服务批量启动脚本
echo     根目录: G:\1代码\开发\SuperMap
echo ========================================
echo.

:::: 设置颜色
color 0A

:::: 切换到项目根目录
cd /d "G:\1代码\开发\SuperMap"
echo [INFO] 当前工作目录: %CD%
echo.

echo [INFO] 检查并终止占用端口的进程...
echo.

:::: 终止占用端口8087的进程 (Analysis服务)
echo 检查端口 8087...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8087') do (
    echo 终止进程 %%a (端口 8087)
    taskkill /f /pid %%a >nul 2>&1
)

:::: 终止占用端口8088的进程 (User服务)  
echo 检查端口 8088...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8088') do (
    echo 终止进程 %%a (端口 8088)
    taskkill /f /pid %%a >nul 2>&1
)

:::: 终止占用端口8089的进程 (Agent服务)
echo 检查端口 8089...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8089') do (
    echo 终止进程 %%a (端口 8089)
    taskkill /f /pid %%a >nul 2>&1
)

:::: 终止占用端口5173的进程 (Frontend服务)
echo 检查端口 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo 终止进程 %%a (端口 5173)
    taskkill /f /pid %%a >nul 2>&1
)

echo 端口检查完成
echo.
echo [INFO] 正在启动所有服务...
echo.

:::: 启动 Analysis 服务 (Node.js)
echo [1/4] 启动 Analysis 服务 (Node.js)...
start "Analysis Service" cmd /k "cd /d \"G:\1代码\开发\SuperMap\Backend\analysis\" && echo 启动 Analysis 服务... && npm run dev"

:::: 等待3秒
timeout /t 3 /nobreak >nul

:::: 启动 User 服务 (Python FastAPI)
echo [2/4] 启动 User 服务 (Python FastAPI)...
start "User Service" cmd /k "cd /d \"G:\1代码\开发\SuperMap\Backend\user\" && echo 激活 conda py310 环境... && conda activate py310 && echo 启动 User 服务... && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8088"

:::: 等待3秒
timeout /t 3 /nobreak >nul

:::: 启动 Agent 服务 (Python FastAPI)
echo [3/4] 启动 Agent 服务 (Python FastAPI)...
start "Agent Service" cmd /k "cd /d \"G:\1代码\开发\SuperMap\Backend\" && echo 激活 conda py310 环境... && conda activate py310 && echo 启动 Agent 服务... && python -m uvicorn agent.app:app --reload --host 0.0.0.0 --port 8089"

:::: 等待3秒
timeout /t 3 /nobreak >nul

:::: 启动 Frontend 服务 (Vue.js)
echo [4/4] 启动 Frontend 服务 (Vue.js)...
start "Frontend Service" cmd /k "cd /d \"G:\1代码\开发\SuperMap\Frontend\" && echo 启动 Frontend 服务... && npm run dev"

echo.
echo ========================================
echo     服务启动完成！
echo ========================================
echo.
echo 📍 项目根目录: G:\1代码\开发\SuperMap
echo.
echo 🌐 服务访问地址:
echo    - Frontend 前端应用: http://localhost:5173
echo    - Analysis 分析服务: http://localhost:8087
echo    - User 用户服务: http://localhost:8088
echo    - Agent AI服务: http://localhost:8089
echo.
echo 📚 API文档地址:
echo    - Analysis API: http://localhost:8087/docs
echo    - User API: http://localhost:8088/docs
echo    - Agent API: http://localhost:8089/docs
echo.
echo 🚀 Agent服务功能:
echo    - LLM聊天接口: http://localhost:8089/agent/chat
echo    - 工具调用接口: http://localhost:8089/agent/tool-chat
echo    - 健康检查: http://localhost:8089/health
echo.
echo 💡 使用说明:
echo    1. 等待所有服务启动完成（约30秒）
echo    2. 访问 http://localhost:5173 使用前端应用
echo    3. 各服务运行在独立命令行窗口
echo    4. 关闭服务请运行 shutdown_services.bat
echo.
echo 按任意键关闭此窗口...
pause >nul
