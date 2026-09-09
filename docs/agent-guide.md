# ArticleAI 智能体开发指南

## 概述

ArticleAI的智能体系统是基于Langchain.js构建的，支持自然语言交互、意图识别、技能调用和上下文管理。

## 智能体架构

### 核心组件

1. **Project Agent（项目智能体）**
   - 每个项目的AI助手
   - 处理自然语言交互
   - 调度Skill执行
   - 管理对话上下文

2. **Skill Registry（技能注册表）**
   - 管理所有可用的Skill
   - 根据意图匹配Skill
   - 执行Skill并返回结果

3. **Intent Parser（意图识别器）**
   - 解析用户输入
   - 识别用户意图
   - 提取参数

4. **Context Manager（上下文管理器）**
   - 维护对话历史
   - 管理项目状态
   - 提供上下文信息

## 开发新的Skill

### Skill基础结构

```typescript
// src/skills/example.skill.ts
import { Injectable } from '@nestjs/common';
import { Skill } from '../agents/base/skill.interface';

@Injectable()
export class ExampleSkill implements Skill {
  name = 'example-skill';
  description = '示例技能，展示如何创建新的Skill';

  async execute(params: any): Promise<any> {
    // 1. 验证参数
    this.validateParams(params);

    // 2. 执行核心逻辑
    const result = await this.processTask(params);

    // 3. 格式化返回结果
    return this.formatResult(result);
  }

  private validateParams(params: any): void {
    if (!params.requiredField) {
      throw new Error('Missing required parameter: requiredField');
    }
  }

  private async processTask(params: any): Promise<any> {
    // 实现具体逻辑
    return { success: true };
  }

  private formatResult(result: any): any {
    return {
      action: this.name,
      result,
      timestamp: new Date().toISOString(),
    };
  }
}
```

### Skill接口定义

```typescript
export interface Skill {
  name: string;
  description: string;
  execute(params: any): Promise<any>;
}
```

### 注册Skill

```typescript
// src/skills/skills.module.ts
import { Module } from '@nestjs/common';
import { ExampleSkill } from './example.skill';

@Module({
  providers: [ExampleSkill],
  exports: [ExampleSkill],
})
export class SkillsModule {}
```

### 在Agent中使用

```typescript
// src/agents/project-agent/project-agent.ts
import { ExampleSkill } from '@skills/example.skill';

export class ProjectAgent {
  constructor(
    private exampleSkill: ExampleSkill,
    // ... 其他依赖
  ) {}

  async processIntent(intent: Intent): Promise<Response> {
    if (intent.action === 'example-action') {
      const result = await this.exampleSkill.execute(intent.params);
      return this.formatResponse(result);
    }
    // ... 其他意图处理
  }
}
```

## 内置Skill详解

### 1. Outline Generation Skill（大纲生成）

**功能：** 根据论文题目和字数要求生成论文大纲

**参数：**
```typescript
{
  title: string;
  wordCount: number;
  major?: string;
  paperType?: string;
}
```

**返回：**
```typescript
{
  outline: {
    title: string;
    chapters: Chapter[];
  }
}
```

**使用示例：**
```typescript
const result = await outlineGenerationSkill.execute({
  title: '基于深度学习的图像识别研究',
  wordCount: 15000,
  major: '计算机科学',
  paperType: '设计类',
});
```

### 2. Reference Search Skill（文献搜索）

**功能：** 在知网搜索相关学术论文

**参数：**
```typescript
{
  keywords: string[];
  limit?: number;
}
```

**返回：**
```typescript
{
  references: Reference[];
}
```

### 3. Writing Skill（写作技能）

**功能：** 生成各类学术文档

**子类型：**
- Task Book Writing（任务书）
- Proposal Writing（开题报告）
- Literature Review Writing（文献综述）
- Paper Writing（论文）

## 意图识别

### 意图定义

```typescript
interface Intent {
  action: string;
  params: Record<string, any>;
  confidence: number;
}
```

### 意图示例

```typescript
const intentExamples = [
  {
    userInput: '帮我生成论文大纲',
    intent: {
      action: 'generate_outline',
      params: {},
      confidence: 0.95,
    },
  },
  {
    userInput: '搜索深度学习相关的文献',
    intent: {
      action: 'search_references',
      params: { keywords: ['深度学习'] },
      confidence: 0.90,
    },
  },
  {
    userInput: '写任务书',
    intent: {
      action: 'write_task_book',
      params: {},
      confidence: 0.95,
    },
  },
];
```

### 实现意图识别器

```typescript
@Injectable()
export class IntentParser {
  constructor(private llmService: LLMService) {}

  async parse(userInput: string, context: Context): Promise<Intent> {
    const prompt = this.buildPrompt(userInput, context);
    const response = await this.llmService.complete(prompt);
    return this.parseResponse(response);
  }

  private buildPrompt(userInput: string, context: Context): string {
    return `
你是一个意图识别助手。根据用户输入和上下文，识别用户的意图。

上下文信息：
- 项目标题：${context.project.title}
- 当前阶段：${context.project.current_stage}
- 已有大纲：${context.hasOutline ? '是' : '否'}

用户输入：${userInput}

请以JSON格式返回意图：
{
  "action": "动作名称",
  "params": { "参数": "值" },
  "confidence": 0.95
}

可用的动作列表：
- generate_outline: 生成大纲
- search_references: 搜索文献
- write_task_book: 写任务书
- write_proposal: 写开题报告
- write_literature_review: 写文献综述
- write_paper: 写论文
- revise_content: 修改内容
    `;
  }
}
```

## 上下文管理

### Context结构

```typescript
interface AgentContext {
  project: Project;
  outline?: Outline;
  references: Reference[];
  documents: Document[];
  conversationHistory: Message[];
  currentTask?: string;
}
```

### 上下文更新

```typescript
@Injectable()
export class ContextManager {
  private contexts: Map<string, AgentContext> = new Map();

  getContext(projectId: string): AgentContext {
    return this.contexts.get(projectId);
  }

  updateContext(projectId: string, updates: Partial<AgentContext>): void {
    const context = this.getContext(projectId);
    this.contexts.set(projectId, { ...context, ...updates });
  }

  addMessage(projectId: string, message: Message): void {
    const context = this.getContext(projectId);
    context.conversationHistory.push(message);
    this.contexts.set(projectId, context);
  }
}
```

## 流式响应

对于长文本生成，使用流式响应提升用户体验：

```typescript
async generateWithStream(
  prompt: string,
  callback: (chunk: string) => void,
): Promise<void> {
  const stream = await this.llmService.streamComplete(prompt);

  for await (const chunk of stream) {
    callback(chunk);
  }
}
```

## 错误处理

```typescript
try {
  const result = await skill.execute(params);
  return { success: true, result };
} catch (error) {
  if (error instanceof ValidationError) {
    return { success: false, error: '参数验证失败' };
  } else if (error instanceof LLMError) {
    return { success: false, error: 'AI服务调用失败' };
  } else {
    return { success: false, error: '未知错误' };
  }
}
```

## 测试

### 单元测试

```typescript
describe('ExampleSkill', () => {
  let skill: ExampleSkill;

  beforeEach(() => {
    skill = new ExampleSkill();
  });

  it('should execute successfully with valid params', async () => {
    const result = await skill.execute({ requiredField: 'value' });
    expect(result.success).toBe(true);
  });

  it('should throw error with invalid params', async () => {
    await expect(skill.execute({})).rejects.toThrow();
  });
});
```

### 集成测试

```typescript
describe('ProjectAgent', () => {
  let agent: ProjectAgent;

  beforeEach(() => {
    // 初始化
  });

  it('should handle outline generation intent', async () => {
    const response = await agent.processMessage('帮我生成大纲');
    expect(response.action).toBe('outline_generated');
  });
});
```

## 最佳实践

1. **保持Skill单一职责**
   - 每个Skill只做一件事
   - 复杂任务拆分为多个Skill

2. **合理使用上下文**
   - 避免上下文过大
   - 定期清理历史消息

3. **处理异常情况**
   - 优雅降级
   - 友好的错误提示

4. **性能优化**
   - 缓存常用数据
   - 异步处理长任务
   - 使用流式响应

5. **安全考虑**
   - 验证所有输入
   - 限制资源使用
   - 避免注入攻击

## 调试技巧

### 启用详细日志

```typescript
this.logger.debug('Intent parsed:', intent);
this.logger.debug('Context:', context);
this.logger.debug('Skill result:', result);
```

### 使用调试模式

```bash
DEBUG=articleai:* npm run start:dev
```

### 监控Token使用

```typescript
const tokensUsed = result.usage.total_tokens;
this.metricsService.recordTokenUsage(tokensUsed);
```
