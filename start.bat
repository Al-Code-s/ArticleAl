@echo off
chcp 65001 >nul

echo ======================================
echo   ArticleAI 项目初始化脚本
echo ======================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker 已安装
echo ✅ Docker Compose 已安装
echo.

REM 检查环境变量文件
if not exist .env (
    echo 📝 创建环境变量文件...
    copy .env.example .env
    echo ⚠️  请编辑 .env 文件并配置必要的环境变量
    echo.
    set /p edit="是否现在编辑 .env 文件? (y/n) "
    if /i "%edit%"=="y" (
        notepad .env
    )
)

echo.
echo 🚀 开始启动服务...
echo.

REM 切换到docker目录
cd docker

REM 启动服务
docker-compose up -d

echo.
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo.
echo 📊 服务状态：
docker-compose ps

echo.
echo ======================================
echo   ✅ ArticleAI 启动完成！
echo ======================================
echo.
echo 🌐 访问地址：
echo    前端: http://localhost
echo    后端API: http://localhost/api
echo    健康检查: http://localhost/health
echo.
echo 📝 查看日志：
echo    docker-compose logs -f
echo.
echo 🛑 停止服务：
echo    docker-compose down
echo.

pause
