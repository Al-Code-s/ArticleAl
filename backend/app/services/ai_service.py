"""
AI 服务

提供 AI 模型调用的统一接口
"""
from typing import Optional, List, Dict, Any
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.core.config import settings


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 AI 客户端"""
        self.anthropic_client = None
        self.openai_client = None

        # 初始化 Claude
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )

        # 初始化 OpenAI
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY
            )

    async def generate_topics(
        self,
        major: str,
        education_level: str,
        paper_type: str,
        keywords: Optional[List[str]] = None,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        生成论文选题

        Args:
            major: 专业
            education_level: 学历层次
            paper_type: 论文类型
            keywords: 关键词列表
            count: 生成数量

        Returns:
            选题列表
        """
        keywords_str = "、".join(keywords) if keywords else ""
        keyword_prompt = f"，关键词包括：{keywords_str}" if keywords_str else ""

        prompt = f"""你是一位资深的学术导师，请为{education_level}的{major}专业学生生成{count}个{paper_type}选题{keyword_prompt}。

要求：
1. 选题要具有创新性和可行性
2. 难度适合{education_level}层次
3. 每个选题包含：标题、描述、关键词
4. 描述要简明扼要，说明研究价值

请以JSON格式返回，格式如下：
[
  {{
    "title": "选题标题",
    "description": "选题描述（100-200字）",
    "keywords": ["关键词1", "关键词2", "关键词3"]
  }}
]"""

        # 使用 Claude
        if self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text

            # 解析 JSON
            import json
            import re
            # 提取 JSON 部分
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                topics = json.loads(json_match.group())
                return topics

        # 如果 Claude 不可用或失败，返回模拟数据
        return self._generate_mock_topics(major, education_level, paper_type, count)

    async def generate_outline(
        self,
        topic_title: str,
        major: str,
        education_level: str,
        paper_type: str,
        requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成论文大纲

        Args:
            topic_title: 选题标题
            major: 专业
            education_level: 学历层次
            paper_type: 论文类型
            requirements: 额外要求

        Returns:
            大纲结构
        """
        req_text = f"\n额外要求：{requirements}" if requirements else ""

        prompt = f"""你是一位资深的学术导师，请为以下论文生成详细的大纲结构：

论文标题：{topic_title}
专业：{major}
学历层次：{education_level}
论文类型：{paper_type}{req_text}

要求：
1. 大纲要完整、结构清晰
2. 包含摘要、引言、文献综述、研究方法、研究结果、讨论、结论、参考文献等章节
3. 每个一级章节下包含2-4个二级章节
4. 适合{education_level}的研究深度

请以JSON格式返回，格式如下：
{{
  "title": "论文标题",
  "sections": [
    {{
      "level": 1,
      "title": "1. 引言",
      "content": "简要说明本章节的内容",
      "order": 1,
      "subsections": [
        {{
          "level": 2,
          "title": "1.1 研究背景",
          "content": "说明",
          "order": 1
        }}
      ]
    }}
  ]
}}"""

        # 使用 Claude
        if self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text

            # 解析 JSON
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                outline = json.loads(json_match.group())
                return outline

        # 返回模拟数据
        return self._generate_mock_outline(topic_title)

    async def search_references(
        self,
        keyword: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索参考文献

        TODO: 集成知网或其他学术数据库 API
        目前返回模拟数据

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数

        Returns:
            文献列表
        """
        # 这里应该调用知网 API 或其他学术数据库
        # 暂时返回模拟数据
        return self._generate_mock_references(keyword, max_results)

    async def generate_document(
        self,
        document_type: str,
        topic_title: str,
        outline: Optional[Dict[str, Any]] = None,
        references: Optional[List[Dict[str, Any]]] = None,
        requirements: Optional[str] = None
    ) -> str:
        """
        生成文档内容

        Args:
            document_type: 文档类型
            topic_title: 论文标题
            outline: 大纲结构
            references: 参考文献
            requirements: 额外要求

        Returns:
            文档内容（Markdown格式）
        """
        doc_type_names = {
            "assignment": "任务书",
            "proposal": "开题报告",
            "literature_review": "文献综述",
            "thesis": "论文正文"
        }
        doc_name = doc_type_names.get(document_type, "文档")
        req_text = f"\n额外要求：{requirements}" if requirements else ""

        outline_text = ""
        if outline:
            outline_text = f"\n参考大纲：\n{self._format_outline(outline)}"

        refs_text = ""
        if references:
            refs_text = f"\n参考文献：\n" + "\n".join([
                f"- {ref.get('title', '')} ({ref.get('year', '')})"
                for ref in references[:5]
            ])

        prompt = f"""你是一位资深的学术写作专家，请为以下论文撰写{doc_name}：

论文标题：{topic_title}{outline_text}{refs_text}{req_text}

要求：
1. 内容要专业、严谨
2. 结构完整、逻辑清晰
3. 字数适中（3000-5000字）
4. 使用学术语言，避免口语化
5. 以Markdown格式输出

请直接输出{doc_name}的完整内容。"""

        # 使用 Claude
        if self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        # 返回模拟数据
        return self._generate_mock_document(doc_name, topic_title)

    def _format_outline(self, outline: Dict[str, Any]) -> str:
        """格式化大纲为文本"""
        lines = []
        sections = outline.get("sections", [])
        for section in sections:
            lines.append(f"{section['title']}")
            for subsection in section.get("subsections", []):
                lines.append(f"  {subsection['title']}")
        return "\n".join(lines)

    def _generate_mock_topics(
        self,
        major: str,
        education_level: str,
        paper_type: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """生成模拟选题数据"""
        return [
            {
                "title": f"基于{major}的{i+1}号研究课题",
                "description": f"这是一个关于{major}领域的深入研究，适合{education_level}层次的{paper_type}。本研究旨在探索该领域的关键问题，提出创新性的解决方案。",
                "keywords": [major, "研究", "应用"],
            }
            for i in range(count)
        ]

    def _generate_mock_outline(self, topic_title: str) -> Dict[str, Any]:
        """生成模拟大纲数据"""
        return {
            "title": topic_title,
            "sections": [
                {
                    "level": 1,
                    "title": "摘要",
                    "content": "论文摘要部分",
                    "order": 1
                },
                {
                    "level": 1,
                    "title": "1. 引言",
                    "content": "介绍研究背景和意义",
                    "order": 2,
                    "subsections": [
                        {"level": 2, "title": "1.1 研究背景", "content": "", "order": 1},
                        {"level": 2, "title": "1.2 研究意义", "content": "", "order": 2},
                    ]
                },
                {
                    "level": 1,
                    "title": "2. 文献综述",
                    "content": "回顾相关研究",
                    "order": 3
                },
                {
                    "level": 1,
                    "title": "3. 研究方法",
                    "content": "说明研究方法",
                    "order": 4
                },
                {
                    "level": 1,
                    "title": "4. 研究结果",
                    "content": "展示研究结果",
                    "order": 5
                },
                {
                    "level": 1,
                    "title": "5. 讨论",
                    "content": "讨论研究发现",
                    "order": 6
                },
                {
                    "level": 1,
                    "title": "6. 结论",
                    "content": "总结研究成果",
                    "order": 7
                },
                {
                    "level": 1,
                    "title": "参考文献",
                    "content": "列出参考文献",
                    "order": 8
                }
            ]
        }

    def _generate_mock_references(
        self,
        keyword: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """生成模拟文献数据"""
        return [
            {
                "title": f"关于{keyword}的研究{i+1}",
                "authors": ["张三", "李四"],
                "publication": "学术期刊",
                "year": 2023 - i,
                "volume": f"{40+i}",
                "issue": f"{i+1}",
                "pages": f"{100+i*10}-{120+i*10}",
                "doi": f"10.1234/example.{2023-i}.{i+1:03d}",
                "abstract": f"本文研究了{keyword}相关的问题...",
                "keywords": [keyword, "研究", "应用"],
                "citation_format": "GB/T 7714",
            }
            for i in range(min(max_results, 5))
        ]

    def _generate_mock_document(self, doc_type: str, title: str) -> str:
        """生成模拟文档内容"""
        return f"""# {title} - {doc_type}

## 摘要

本研究针对相关领域的重要问题展开深入探讨，通过系统的理论分析和实证研究，提出了创新性的解决方案。

## 1. 引言

### 1.1 研究背景

随着相关领域的不断发展，该问题日益受到学术界和实践界的关注。

### 1.2 研究意义

本研究具有重要的理论意义和实践价值。

## 2. 文献综述

回顾国内外相关研究...

## 3. 研究方法

本研究采用定性与定量相结合的研究方法...

## 4. 研究结果

通过研究，我们得到了以下主要发现...

## 5. 讨论

研究结果表明...

## 6. 结论

本研究得出以下结论...

## 参考文献

[1] 张三, 李四. 相关研究[J]. 学术期刊, 2023, 40(1): 100-120.
"""


# 全局 AI 服务实例
ai_service = AIService()
