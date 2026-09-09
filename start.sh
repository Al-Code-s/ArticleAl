#!/bin/bash

echo "======================================"
echo "  ArticleAI 项目初始化脚本"
echo "======================================"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 已安装"
echo "✅ Docker Compose 已安装"
echo ""

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件并配置必要的环境变量"
    echo ""
    read -p "是否现在编辑 .env 文件? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
fi

echo ""
echo "🚀 开始启动服务..."
echo ""

# 切换到docker目录
cd docker

# 启动服务
docker-compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

echo ""
echo "======================================"
echo "  ✅ ArticleAI 启动完成！"
echo "======================================"
echo ""
echo "🌐 访问地址："
echo "   前端: http://localhost"
echo "   后端API: http://localhost/api"
echo "   健康检查: http://localhost/health"
echo ""
echo "📝 查看日志："
echo "   docker-compose logs -f"
echo ""
echo "🛑 停止服务："
echo "   docker-compose down"
echo ""
