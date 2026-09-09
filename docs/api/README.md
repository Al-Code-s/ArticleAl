# ArticleAI API 文档

## 基础信息

- **Base URL**: `http://localhost:3000/api`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

### 通用响应格式

**成功响应：**
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**错误响应：**
```json
{
  "success": false,
  "statusCode": 400,
  "message": "错误描述",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "path": "/api/..."
}
```

## 认证相关

### 注册

**POST** `/auth/register`

**请求体：**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "username": "string",
      "email": "string"
    },
    "token": "jwt_token"
  }
}
```

### 登录

**POST** `/auth/login`

**请求体：**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "username": "string",
      "email": "string"
    },
    "token": "jwt_token"
  }
}
```

## 选题模块

### 生成题目

**POST** `/topics/generate`

**请求头：**
```
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "major": "计算机科学",
  "educationLevel": "本科",
  "paperType": "设计类",
  "count": 10
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "topics": [
      {
        "id": "uuid",
        "title": "基于深度学习的图像识别系统研究",
        "major": "计算机科学",
        "education_level": "本科",
        "paper_type": "设计类",
        "description": "...",
        "feasibility_score": 85,
        "keywords": ["深度学习", "图像识别"],
        "is_used": false,
        "created_at": "2024-01-01T00:00:00.000Z"
      }
    ]
  }
}
```

### 从题目创建项目

**POST** `/topics/create-project`

**请求体：**
```json
{
  "topicId": "uuid",
  "wordCount": 15000
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "project": {
      "id": "uuid",
      "title": "...",
      "word_count": 15000,
      "status": "created"
    }
  }
}
```

### 获取题目列表

**GET** `/topics?unused=true`

**响应：**
```json
{
  "success": true,
  "data": {
    "topics": [...]
  }
}
```

## 项目模块

### 获取项目列表

**GET** `/projects?status=in_progress&page=1&limit=10`

**响应：**
```json
{
  "success": true,
  "data": {
    "projects": [...],
    "total": 20
  }
}
```

### 获取项目详情

**GET** `/projects/:id`

**响应：**
```json
{
  "success": true,
  "data": {
    "project": {
      "id": "uuid",
      "title": "...",
      "status": "in_progress",
      "agent_status": "idle",
      ...
    }
  }
}
```

### 创建项目

**POST** `/projects`

**请求体：**
```json
{
  "title": "论文题目",
  "major": "专业",
  "educationLevel": "学历",
  "paperType": "类型",
  "wordCount": 15000
}
```

### 更新项目

**PUT** `/projects/:id`

**请求体：**
```json
{
  "title": "新题目",
  "wordCount": 20000,
  "status": "in_progress"
}
```

### 删除项目

**DELETE** `/projects/:id`

**响应：**
```json
{
  "success": true,
  "data": {
    "success": true
  }
}
```

## 大纲模块

### 获取大纲

**GET** `/projects/:projectId/outline`

**响应：**
```json
{
  "success": true,
  "data": {
    "outline": {
      "id": "uuid",
      "content": {
        "title": "...",
        "chapters": [...]
      },
      "version": 1,
      "is_current": true
    }
  }
}
```

### 生成大纲

**POST** `/projects/:projectId/outline/generate`

**请求体：**
```json
{
  "method": "ai"  // 或 "agent"
}
```

### 更新大纲

**PUT** `/projects/:projectId/outline`

**请求体：**
```json
{
  "content": {
    "title": "...",
    "chapters": [...]
  }
}
```

## 参考文献模块

### 搜索参考文献

**POST** `/projects/:projectId/references/search`

**请求体：**
```json
{
  "keywords": ["深度学习", "图像识别"],
  "limit": 20
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "references": [
      {
        "id": "uuid",
        "title": "...",
        "authors": ["作者1", "作者2"],
        "journal": "期刊名",
        "year": 2023,
        "doi": "...",
        "cnki_url": "...",
        "abstract": "...",
        "is_selected": false
      }
    ]
  }
}
```

### 选择参考文献

**POST** `/projects/:projectId/references/select`

**请求体：**
```json
{
  "referenceIds": ["uuid1", "uuid2"]
}
```

### 获取参考文献列表

**GET** `/projects/:projectId/references?selected=true`

### 删除参考文献

**DELETE** `/projects/:projectId/references/:refId`

## 智能体模块

### 启动智能体

**POST** `/projects/:projectId/agent/start`

**请求体：**
```json
{
  "aiConfigId": "uuid"  // 可选
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "session": {
      "id": "uuid",
      "status": "active",
      "created_at": "..."
    }
  }
}
```

### 停止智能体

**POST** `/projects/:projectId/agent/stop`

### 重启智能体

**POST** `/projects/:projectId/agent/restart`

**请求体：**
```json
{
  "aiConfigId": "uuid"  // 可选
}
```

### 获取智能体状态

**GET** `/projects/:projectId/agent/status`

**响应：**
```json
{
  "success": true,
  "data": {
    "status": "running",
    "sessionId": "uuid",
    "messageCount": 15
  }
}
```

### 获取对话历史

**GET** `/projects/:projectId/agent/history?limit=50&offset=0`

**响应：**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "uuid",
        "role": "user",
        "content": "...",
        "tokens_used": 100,
        "created_at": "..."
      }
    ]
  }
}
```

## WebSocket API

### 智能体对话

**连接URL:** `ws://localhost:3000/ws/projects/:projectId/agent`

**认证:** 
```javascript
{
  auth: {
    token: "jwt_token"
  }
}
```

**客户端发送：**
```json
{
  "type": "message",
  "content": "帮我生成论文大纲"
}
```

**服务端响应：**

消息类型：
```json
{
  "type": "message",
  "data": {
    "role": "assistant",
    "content": "好的，我来帮你生成大纲...",
    "metadata": {}
  }
}
```

状态更新：
```json
{
  "type": "status",
  "data": {
    "status": "processing",
    "message": "正在生成大纲..."
  }
}
```

结果通知：
```json
{
  "type": "result",
  "data": {
    "action": "outline_generated",
    "result": { ... }
  }
}
```

## 文档生成模块

### 生成任务书

**POST** `/projects/:projectId/documents/task-book`

**请求体：**
```json
{
  "method": "ai"  // 或 "agent"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "document": { ... },
    "jobId": "uuid"  // 如果是异步任务
  }
}
```

### 生成开题报告

**POST** `/projects/:projectId/documents/proposal`

### 生成文献综述

**POST** `/projects/:projectId/documents/literature-review`

### 获取文档

**GET** `/projects/:projectId/documents/:type`

参数 `type`: `task-book` | `proposal` | `literature-review`

### 更新文档

**PUT** `/projects/:projectId/documents/:docId`

**请求体：**
```json
{
  "content": "更新后的内容"
}
```

## 论文模块

### 生成论文

**POST** `/projects/:projectId/paper/generate`

**请求体：**
```json
{
  "method": "ai",
  "sections": ["1", "2", "3"]  // 可选，指定章节
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "jobId": "uuid"
  }
}
```

### 获取论文章节列表

**GET** `/projects/:projectId/paper/sections`

### 获取章节内容

**GET** `/projects/:projectId/paper/sections/:sectionId`

### 更新章节内容

**PUT** `/projects/:projectId/paper/sections/:sectionId`

**请求体：**
```json
{
  "content": "章节内容"
}
```

### 修改论文

**POST** `/projects/:projectId/paper/revise`

**请求体：**
```json
{
  "sectionId": "uuid",
  "comment": "修改意见"
}
```

## 导出模块

### 导出任务书

**POST** `/projects/:projectId/export/task-book`

**请求体：**
```json
{
  "format": "docx"  // 或 "pdf"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "fileUrl": "/exports/xxx.docx",
    "exportId": "uuid"
  }
}
```

### 导出开题报告

**POST** `/projects/:projectId/export/proposal`

### 导出文献综述

**POST** `/projects/:projectId/export/literature-review`

### 导出论文

**POST** `/projects/:projectId/export/paper`

**请求体：**
```json
{
  "format": "docx",
  "includeCover": true
}
```

### 获取导出历史

**GET** `/projects/:projectId/export/history`

### 下载导出文件

**GET** `/export/:exportId/download`

响应：文件流

## AI配置模块

### 创建AI配置

**POST** `/ai-configs`

**请求体：**
```json
{
  "configName": "Claude Sonnet",
  "provider": "claude",
  "apiKey": "sk-ant-...",
  "modelName": "claude-sonnet-5",
  "baseUrl": "https://api.anthropic.com",
  "maxTokens": 4096,
  "temperature": 0.7
}
```

### 获取配置列表

**GET** `/ai-configs`

### 获取配置详情

**GET** `/ai-configs/:id`

### 更新配置

**PUT** `/ai-configs/:id`

### 删除配置

**DELETE** `/ai-configs/:id`

### 设为默认配置

**POST** `/ai-configs/:id/set-default`

### 测试配置

**POST** `/ai-configs/test`

**请求体：**
```json
{
  "provider": "claude",
  "apiKey": "...",
  "modelName": "...",
  "baseUrl": "..."
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "success": true,
    "latency": 234  // ms
  }
}
```

## 任务队列

### 获取任务状态

**GET** `/jobs/:jobId`

**响应：**
```json
{
  "success": true,
  "data": {
    "job": {
      "id": "uuid",
      "status": "processing",
      "progress": 50,
      "result": null
    }
  }
}
```

### 取消任务

**POST** `/jobs/:jobId/cancel`

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录或token过期） |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 限流策略

- 登录：每分钟最多5次
- 题目生成：每小时最多20次
- AI调用：根据配置的配额
- 其他API：每分钟最多60次
