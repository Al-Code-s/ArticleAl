# ArticleAI 部署文档

## 前置要求

### 系统要求
- 操作系统：Linux/macOS/Windows
- Docker：20.10+
- Docker Compose：2.0+
- Python：3.11+ (仅本地开发)
- Node.js：18+ (仅本地开发)
- PostgreSQL：14+ (仅本地开发)
- Redis：5+ (仅本地开发)

### 硬件要求

**最低配置：**
- CPU：2核
- 内存：4GB
- 磁盘：20GB

**推荐配置：**
- CPU：4核+
- 内存：8GB+
- 磁盘：50GB+

## 快速部署（Docker）

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ArticleAI.git
cd ArticleAI
```

### 2. 配置环境变量

```bash
# 复制后端环境变量模板
cp backend/.env.example backend/.env

# 编辑环境变量
nano backend/.env
```

**必须配置的环境变量：**
```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/articleai

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT密钥
SECRET_KEY=your_jwt_secret_key

# AI API密钥
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. 启动服务

```bash
cd docker
docker-compose up -d
```

### 4. 检查服务状态

```bash
docker-compose ps
```

所有服务应该处于 `Up` 状态。

### 5. 访问应用

- **前端**：http://localhost
- **后端API**：http://localhost/api
- **API文档**：http://localhost/api/docs
- **健康检查**：http://localhost/api/health

### 6. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 本地开发部署

### 1. 启动数据库服务

```bash
cd docker
docker-compose -f docker-compose.dev.yml up -d
```

### 2. 后端开发

```bash
cd backend

# 安装依赖
npm install

# 启动开发服务器
npm run start:dev
```

后端将在 http://localhost:3000 启动。

### 3. 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动。

## 生产环境部署

### 1. 使用反向代理（推荐）

#### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. HTTPS配置

使用 Let's Encrypt 获取免费SSL证书：

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

### 3. 数据备份

#### 数据库备份

```bash
# 创建备份脚本
cat > backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)

docker exec articleai-postgres pg_dump -U admin articleai > "$BACKUP_DIR/db_$DATE.sql"

# 保留最近7天的备份
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
EOF

chmod +x backup.sh

# 设置定时任务
crontab -e
# 添加：0 2 * * * /path/to/backup.sh
```

#### 文件备份

```bash
# 备份上传和导出文件
tar -czf backup_files_$(date +%Y%m%d).tar.gz \
  docker/volumes/backend-uploads \
  docker/volumes/backend-exports
```

### 4. 监控和日志

#### 日志管理

```bash
# 配置日志轮转
cat > /etc/logrotate.d/articleai <<EOF
/var/log/articleai/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

#### 性能监控

推荐使用以下工具：
- Prometheus + Grafana（指标监控）
- ELK Stack（日志分析）
- Sentry（错误追踪）

## 升级部署

### 1. 拉取最新代码

```bash
git pull origin main
```

### 2. 重新构建镜像

```bash
cd docker
docker-compose build
```

### 3. 停止旧服务

```bash
docker-compose down
```

### 4. 启动新服务

```bash
docker-compose up -d
```

### 5. 运行数据库迁移（如有）

```bash
docker exec -it articleai-backend npm run migration:run
```

## 故障排查

### 服务无法启动

1. 检查端口占用
```bash
netstat -tulpn | grep -E '80|3000|5432|6379'
```

2. 检查Docker日志
```bash
docker-compose logs backend
```

3. 检查环境变量
```bash
docker-compose config
```

### 数据库连接失败

1. 检查数据库容器状态
```bash
docker-compose ps postgres
```

2. 测试数据库连接
```bash
docker exec -it articleai-postgres psql -U admin -d articleai
```

### 前端无法访问后端

1. 检查网络连接
```bash
docker network ls
docker network inspect articleai_articleai-network
```

2. 检查CORS配置
查看后端 `main.ts` 中的CORS设置

### AI调用失败

1. 检查API密钥配置
2. 检查网络连接
3. 查看后端日志中的错误信息

## 性能优化

### 1. 数据库优化

```sql
-- 创建必要的索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_user_status 
  ON projects(user_id, status);

-- 分析表统计信息
ANALYZE projects;
ANALYZE agent_messages;
```

### 2. Redis优化

```bash
# 配置Redis最大内存
docker exec articleai-redis redis-cli CONFIG SET maxmemory 2gb
docker exec articleai-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### 3. Nginx优化

```nginx
# 启用gzip压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 静态资源缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 安全加固

### 1. 防火墙配置

```bash
# 只开放必要的端口
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

### 2. 限制Docker容器权限

```yaml
# docker-compose.yml
services:
  backend:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

### 3. 定期更新

```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade

# 更新Docker镜像
docker-compose pull
docker-compose up -d
```

## 扩展部署

### 水平扩展

使用Docker Swarm或Kubernetes进行多节点部署：

```bash
# Docker Swarm示例
docker swarm init
docker stack deploy -c docker-compose.yml articleai
```

### 数据库主从复制

参考PostgreSQL官方文档配置流复制。

### Redis集群

配置Redis Cluster实现高可用。

## 技术支持

如遇到部署问题，请：
1. 查看项目Wiki
2. 提交GitHub Issue
3. 联系技术支持团队
