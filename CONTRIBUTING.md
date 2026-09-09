# 贡献指南

感谢你考虑为 ArticleAI 做出贡献！

## 如何贡献

### 报告Bug

如果你发现了Bug，请创建一个Issue并包含以下信息：

- Bug的详细描述
- 复现步骤
- 预期行为
- 实际行为
- 截图（如果适用）
- 环境信息（操作系统、浏览器版本等）

### 提出功能建议

我们欢迎新功能的建议！请创建一个Issue并描述：

- 功能的详细描述
- 使用场景
- 为什么这个功能有用
- 可能的实现方式

### 提交代码

1. Fork本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建一个Pull Request

### 代码规范

#### 后端（Python/FastAPI）

- 使用Black和isort格式化代码
- 遵循PEP 8编码规范
- 为公共方法编写docstring注释
- 使用类型提示（Type Hints）
- 编写单元测试

```python
async def generate_outline(
    project_id: str,
    options: dict
) -> Outline:
    """生成论文大纲
    
    Args:
        project_id: 项目ID
        options: 生成选项
        
    Returns:
        Outline: 生成的大纲对象
    """
async generateOutline(projectId: string, options: OutlineOptions): Promise<Outline> {
  // 实现
}
```

#### 前端（TypeScript/React）

- 使用ESLint和Prettier格式化代码
- 使用函数式组件和Hooks
- 组件应该有清晰的props类型定义
- 遵循Ant Design的设计规范

```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false }) => {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
};
```

### 提交信息规范

使用语义化的提交信息：

- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 添加论文导出功能

- 支持导出为Word格式
- 支持导出为PDF格式
- 添加自定义模板功能
```

### 测试

在提交代码前，请确保：

- 所有测试通过
- 添加了必要的新测试
- 代码覆盖率没有下降

```bash
# 后端测试
cd backend
npm test

# 前端测试
cd frontend
npm test
```

### 文档

如果你的更改需要更新文档，请同时更新相关的Markdown文件。

## 开发环境设置

参考 [README.md](./README.md) 中的"本地开发"部分。

## 问题和讨论

如果你有任何问题或想法，欢迎：

- 创建Issue讨论
- 加入我们的社区频道

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺让每个人都能自由地参与我们的项目和社区。

### 我们的标准

积极行为的例子：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同情

不可接受的行为：

- 使用性化的语言或图像
- 挑衅、侮辱或贬损的评论
- 公开或私下的骚扰
- 未经许可发布他人的私人信息
- 其他在专业环境中被认为不适当的行为

## 许可证

通过贡献，你同意你的贡献将在MIT许可证下授权。

## 感谢

感谢所有为ArticleAI做出贡献的人！
