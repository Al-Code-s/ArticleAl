# ArticleAI 快速启动指南

## 前提条件

确保已安装：
- Python 3.11+
- PostgreSQL (运行在 localhost:5433)
- Node.js 18+
- Redis (可选，WebSocket 功能需要)

## 后端启动步骤

### 1. 配置环境变量

确保 `backend/.env` 文件已配置：

```bash
DATABASE_URL=postgresql+asyncpg://postgres:root123@localhost:5433/articleai
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
CORS_ORIGINS=http://localhost:5173
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python main.py
```

后端将在 http://localhost:3000 启动

- API 文档: http://localhost:3000/docs
- 健康检查: http://localhost:3000/health

## 前端启动步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

创建 `frontend/.env` 文件：

```bash
VITE_API_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3000
```

### 3. 启动开发服务器

```bash
npm run dev
```

前端将在 http://localhost:5173 启动

## 功能测试

### 方法 1: 使用自动化测试脚本

```bash
cd backend
python test_complete.py
```

测试脚本会自动测试所有功能：
- ✅ 用户注册/登录
- ✅ 创建项目
- ✅ AI 生成选题
- ✅ AI 生成大纲
- ✅ AI 搜索参考文献
- ✅ AI 生成文档
- ✅ WebSocket 实时对话
- ✅ Word/PDF 导出

### 方法 2: 使用 API 文档测试

1. 访问 http://localhost:3000/docs
2. 点击 "Authorize" 按钮
3. 注册账号并登录获取 token
4. 使用 token 测试各个 API 端点

### 方法 3: 使用前端测试页面

1. 访问 http://localhost:5173/test
2. 输入项目 ID
3. 点击各功能按钮测试

## 核心功能说明

### 1. 选题生成
**API:** `POST /api/topics/generate`

使用 Claude AI 根据专业、学历、论文类型生成学术选题。

示例请求：
```json
{
  "project_id": 1,
  "major": "计算机科学",
  "education_level": "本科",
  "paper_type": "毕业论文",
  "keywords": ["人工智能", "机器学习"],
  "count": 3
}
```

### 2. 大纲生成
**API:** `POST /api/outlines/generate`

AI 生成完整的论文大纲结构，支持多级章节。

示例请求：
```json
{
  "project_id": 1,
  "topic_title": "基于深度学习的图像识别研究",
  "requirements": "需要包含实验部分"
}
```

### 3. 参考文献搜索
**API:** `POST /api/references/search`

AI 搜索学术文献（当前为模拟数据，待集成知网 API）。

示例请求：
```json
{
  "keyword": "深度学习",
  "project_id": 1,
  "max_results": 10,
  "save_to_project": true
}
```

### 4. 文档生成
**API:** `POST /api/documents/generate`

AI 生成完整的文档内容（开题报告、文献综述、论文正文等）。

示例请求：
```json
{
  "project_id": 1,
  "document_type": "proposal",
  "requirements": "需要详细的研究方法说明"
}
```

支持的文档类型：
- `proposal` - 开题报告
- `literature_review` - 文献综述
- `thesis` - 论文正文
- `assignment` - 任务书

### 5. WebSocket 实时对话
**连接:** `ws://localhost:3000/ws/chat?token={JWT_TOKEN}&project_id={PROJECT_ID}`

支持与 AI 助手进行实时对话。

示例代码：
```javascript
const ws = new WebSocket('ws://localhost:3000/ws/chat?token=xxx&project_id=1');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('AI 响应:', data.message);
};

ws.send(JSON.stringify({
  type: 'chat',
  message: '请帮我生成一个选题'
}));
```

### 6. 文档导出
**API:** `POST /api/export/document/{document_id}?format=word`

导出文档为 Word 或 PDF 格式。

支持的格式：
- `word` - Microsoft Word (.docx)
- `pdf` - PDF 文档

## 故障排除

### 问题 1: 数据库连接失败
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案:**
- 确保 PostgreSQL 正在运行
- 检查端口 5433 是否正确
- 验证用户名和密码

### 问题 2: AI API 调用失败
```
anthropic.APIError: Invalid API key
```

**解决方案:**
- 检查 `.env` 文件中的 `ANTHROPIC_API_KEY`
- 确保 API key 有效且有足够配额
- 可以切换到 OpenAI 作为备用

### 问题 3: WebSocket 连接失败
```
WebSocket connection failed
```

**解决方案:**
- 确保 Redis 正在运行（如果使用消息队列）
- 检查 JWT token 是否有效
- 验证 WebSocket URL 格式正确

### 问题 4: 导出功能报错
```
FileNotFoundError: [Errno 2] No such file or directory: './exports'
```

**解决方案:**
```bash
mkdir -p backend/exports
mkdir -p backend/uploads
```

### 问题 5: 前端无法连接后端
```
Network Error
```

**解决方案:**
- 检查后端是否正在运行
- 验证 `VITE_API_URL` 配置
- 检查 CORS 配置（后端 `.env` 中的 `CORS_ORIGINS`）

## 目录结构

```
ArticleAI/
├── backend/
│   ├── app/
│   │   ├── api/              # API 路由
│   │   │   ├── auth.py       # 认证
│   │   │   ├── projects.py   # 项目管理
│   │   │   ├── topics.py     # 选题（AI）
│   │   │   ├── outlines.py   # 大纲（AI）
│   │   │   ├── references.py # 参考文献（AI）
│   │   │   ├── documents.py  # 文档（AI）
│   │   │   ├── websocket.py  # WebSocket
│   │   │   └── export.py     # 导出
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic Schemas
│   │   └── services/         # 业务逻辑
│   │       ├── ai_service.py      # AI 服务
│   │       ├── chat_service.py    # 聊天服务
│   │       └── export_service.py  # 导出服务
│   ├── main.py              # 应用入口
│   ├── test_complete.py     # 完整测试脚本
│   └── requirements.txt     # Python 依赖
│
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   ├── api/         # API 客户端
│   │   │   └── websocket.ts # WebSocket 客户端
│   │   ├── stores/          # 状态管理
│   │   │   └── chatStore.ts # 聊天状态
│   │   ├── components/      # React 组件
│   │   │   ├── ChatPanel/   # 聊天面板
│   │   │   └── ExportButton/ # 导出按钮
│   │   └── pages/
│   │       └── TestPage/    # 测试页面
│   └── package.json
│
├── README.md               # 项目文档
├── DEVELOPMENT.md          # 开发报告
└── QUICKSTART.md          # 本快速启动指南
```

## 下一步

1. **配置 AI API Keys**
   - 获取 Anthropic Claude API key
   - 或使用 OpenAI API key

2. **创建第一个项目**
   - 注册账号
   - 创建论文项目
   - 配置专业、学历、论文类型

3. **体验 AI 功能**
   - 生成选题
   - 生成大纲
   - 搜索文献
   - 生成文档

4. **导出成果**
   - 导出为 Word
   - 导出为 PDF

## 技术支持

如有问题：
1. 查看 API 文档: http://localhost:3000/docs
2. 查看开发报告: [DEVELOPMENT.md](./DEVELOPMENT.md)
3. 查看完整文档: [README.md](./README.md)

## 许可证

MIT License
