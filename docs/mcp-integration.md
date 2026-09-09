# ArticleAI MCP集成指南

## 什么是MCP

MCP (Model Context Protocol) 是一种标准协议，用于AI模型与外部工具、服务进行交互。在ArticleAI中，MCP服务提供了扩展AI能力的标准化方式。

## MCP架构

### 核心概念

1. **MCP Server（MCP服务器）**
   - 提供特定领域的能力
   - 暴露工具（Tools）和资源（Resources）
   - 响应模型的调用请求

2. **Tools（工具）**
   - 可执行的函数
   - 接收参数并返回结果
   - 例如：搜索、查询、转换

3. **Resources（资源）**
   - 只读的数据源
   - 提供上下文信息
   - 例如：文档、配置、状态

## 内置MCP服务

### 1. CNKI Search MCP（知网搜索）

**功能：** 提供知网学术论文搜索能力

**工具列表：**

#### searchCNKI
搜索知网论文

**参数：**
```json
{
  "keywords": ["深度学习", "图像识别"],
  "limit": 20,
  "yearFrom": 2020,
  "yearTo": 2024
}
```

**返回：**
```json
{
  "results": [
    {
      "title": "论文标题",
      "authors": ["作者1", "作者2"],
      "journal": "期刊名称",
      "year": 2023,
      "doi": "10.xxxx/xxxxx",
      "url": "https://...",
      "abstract": "摘要内容"
    }
  ],
  "total": 150
}
```

#### getPaperDetail
获取论文详细信息

**参数：**
```json
{
  "paperId": "cnki_id_or_doi"
}
```

### 2. Document Processor MCP（文档处理）

**功能：** 处理各种格式的文档

**工具列表：**

#### parseDocx
解析DOCX文件

**参数：**
```json
{
  "filePath": "/path/to/file.docx"
}
```

**返回：**
```json
{
  "text": "提取的文本内容",
  "metadata": {
    "pageCount": 10,
    "wordCount": 5000
  }
}
```

#### extractText
从PDF提取文本

**参数：**
```json
{
  "filePath": "/path/to/file.pdf",
  "pages": [1, 2, 3]
}
```

### 3. Format Converter MCP（格式转换）

**功能：** 转换文档格式

**工具列表：**

#### markdownToDocx
Markdown转DOCX

#### markdownToPdf
Markdown转PDF

## 创建自定义MCP服务

### 1. 定义MCP服务器

```typescript
// src/mcp/servers/custom-search/index.ts
import { MCPServer } from '@mcp/server';
import { Tool, Resource } from '@mcp/types';

export class CustomSearchMCPServer extends MCPServer {
  name = 'custom-search';
  description = '自定义搜索服务';
  version = '1.0.0';

  async initialize(): Promise<void> {
    // 初始化逻辑
    this.registerTools();
    this.registerResources();
  }

  private registerTools(): void {
    this.addTool({
      name: 'search',
      description: '搜索功能',
      parameters: {
        type: 'object',
        properties: {
          query: { type: 'string', description: '搜索关键词' },
          limit: { type: 'number', description: '结果数量' },
        },
        required: ['query'],
      },
      handler: this.handleSearch.bind(this),
    });
  }

  private async handleSearch(params: any): Promise<any> {
    const { query, limit = 10 } = params;
    
    // 实现搜索逻辑
    const results = await this.performSearch(query, limit);
    
    return {
      results,
      total: results.length,
    };
  }

  private async performSearch(query: string, limit: number): Promise<any[]> {
    // 具体搜索实现
    return [];
  }
}
```

### 2. 注册MCP服务

```typescript
// src/mcp/mcp-manager.ts
import { Injectable } from '@nestjs/common';
import { CustomSearchMCPServer } from './servers/custom-search';

@Injectable()
export class MCPManager {
  private servers: Map<string, MCPServer> = new Map();

  async initialize(): Promise<void> {
    // 注册MCP服务器
    await this.registerServer(new CustomSearchMCPServer());
  }

  private async registerServer(server: MCPServer): Promise<void> {
    await server.initialize();
    this.servers.set(server.name, server);
  }

  getServer(name: string): MCPServer {
    return this.servers.get(name);
  }

  async callTool(serverName: string, toolName: string, params: any): Promise<any> {
    const server = this.getServer(serverName);
    if (!server) {
      throw new Error(`MCP Server not found: ${serverName}`);
    }
    return await server.callTool(toolName, params);
  }
}
```

### 3. 在Agent中使用MCP

```typescript
// src/agents/project-agent/project-agent.ts
import { MCPManager } from '@mcp/mcp-manager';

export class ProjectAgent {
  constructor(private mcpManager: MCPManager) {}

  async searchReferences(keywords: string[]): Promise<Reference[]> {
    const result = await this.mcpManager.callTool(
      'cnki-search',
      'searchCNKI',
      { keywords, limit: 20 }
    );
    
    return this.formatReferences(result.results);
  }
}
```

## MCP工具最佳实践

### 1. 参数验证

```typescript
private validateParams(params: any, schema: any): void {
  // 使用JSON Schema验证
  const valid = this.validator.validate(params, schema);
  if (!valid) {
    throw new Error('Invalid parameters');
  }
}
```

### 2. 错误处理

```typescript
async callTool(name: string, params: any): Promise<any> {
  try {
    return await this.executeTool(name, params);
  } catch (error) {
    this.logger.error(`MCP Tool error: ${name}`, error);
    throw new MCPError(`Tool execution failed: ${error.message}`);
  }
}
```

### 3. 超时控制

```typescript
async callToolWithTimeout(
  name: string,
  params: any,
  timeout: number = 30000
): Promise<any> {
  return Promise.race([
    this.callTool(name, params),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), timeout)
    ),
  ]);
}
```

### 4. 结果缓存

```typescript
@Injectable()
export class MCPCacheService {
  constructor(private redis: Redis) {}

  async getCached(key: string): Promise<any> {
    const cached = await this.redis.get(key);
    return cached ? JSON.parse(cached) : null;
  }

  async setCached(key: string, value: any, ttl: number = 3600): Promise<void> {
    await this.redis.setex(key, ttl, JSON.stringify(value));
  }
}
```

## 知网搜索MCP实现示例

```typescript
// src/mcp/servers/cnki-search/index.ts
import axios from 'axios';

export class CNKISearchMCPServer extends MCPServer {
  name = 'cnki-search';
  description = '知网学术论文搜索服务';

  private apiUrl: string;
  private apiKey: string;

  async initialize(): Promise<void> {
    this.apiUrl = process.env.CNKI_API_URL;
    this.apiKey = process.env.CNKI_API_KEY;

    this.addTool({
      name: 'searchCNKI',
      description: '在知网搜索学术论文',
      parameters: {
        type: 'object',
        properties: {
          keywords: {
            type: 'array',
            items: { type: 'string' },
            description: '搜索关键词',
          },
          limit: {
            type: 'number',
            description: '返回结果数量',
            default: 20,
          },
          yearFrom: {
            type: 'number',
            description: '起始年份',
          },
          yearTo: {
            type: 'number',
            description: '结束年份',
          },
        },
        required: ['keywords'],
      },
      handler: this.searchCNKI.bind(this),
    });

    this.addTool({
      name: 'getPaperDetail',
      description: '获取论文详细信息',
      parameters: {
        type: 'object',
        properties: {
          paperId: {
            type: 'string',
            description: '论文ID或DOI',
          },
        },
        required: ['paperId'],
      },
      handler: this.getPaperDetail.bind(this),
    });
  }

  private async searchCNKI(params: any): Promise<any> {
    const { keywords, limit = 20, yearFrom, yearTo } = params;

    try {
      const response = await axios.post(
        `${this.apiUrl}/search`,
        {
          keywords: keywords.join(' '),
          page_size: limit,
          year_from: yearFrom,
          year_to: yearTo,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
          },
        }
      );

      return {
        results: this.formatResults(response.data.items),
        total: response.data.total,
      };
    } catch (error) {
      throw new Error(`CNKI search failed: ${error.message}`);
    }
  }

  private async getPaperDetail(params: any): Promise<any> {
    const { paperId } = params;

    try {
      const response = await axios.get(
        `${this.apiUrl}/paper/${paperId}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
          },
        }
      );

      return this.formatPaperDetail(response.data);
    } catch (error) {
      throw new Error(`Get paper detail failed: ${error.message}`);
    }
  }

  private formatResults(items: any[]): any[] {
    return items.map(item => ({
      title: item.title,
      authors: item.authors || [],
      journal: item.journal,
      year: item.year,
      doi: item.doi,
      url: item.url,
      abstract: item.abstract,
      keywords: item.keywords || [],
    }));
  }

  private formatPaperDetail(data: any): any {
    return {
      ...this.formatResults([data])[0],
      fullText: data.full_text,
      references: data.references || [],
      citedBy: data.cited_by || [],
    };
  }
}
```

## 测试MCP服务

```typescript
describe('CNKISearchMCPServer', () => {
  let server: CNKISearchMCPServer;

  beforeEach(async () => {
    server = new CNKISearchMCPServer();
    await server.initialize();
  });

  it('should search papers successfully', async () => {
    const result = await server.callTool('searchCNKI', {
      keywords: ['深度学习'],
      limit: 10,
    });

    expect(result.results).toBeDefined();
    expect(result.results.length).toBeLessThanOrEqual(10);
  });
});
```

## 部署注意事项

1. **API密钥管理**
   - 使用环境变量存储API密钥
   - 不要将密钥提交到代码库

2. **速率限制**
   - 实现请求限流
   - 缓存常用查询结果

3. **错误重试**
   - 网络错误自动重试
   - 指数退避策略

4. **监控和日志**
   - 记录所有MCP调用
   - 监控成功率和延迟
