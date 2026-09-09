"""
聊天服务 - 处理实时对话
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.project import Project
from app.models.topic import Topic
from app.models.outline import Outline
from app.services.ai_service import ai_service
from app.services.ai_runtime import get_active_ai_config


class ChatService:
    """聊天服务类"""

    async def chat(
        self,
        user_id: int,
        project_id: Optional[int],
        message: str,
        context: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        处理用户消息并返回 AI 回复

        Args:
            user_id: 用户ID
            project_id: 项目ID（可选）
            message: 用户消息
            context: 上下文信息（选题、大纲等）
            db: 数据库会话

        Returns:
            包含 AI 回复的字典
        """
        # 构建系统提示
        system_prompt = self._build_system_prompt(context)

        # 如果有项目ID，获取项目相关信息
        project_context = ""
        if project_id:
            project_context = await self._get_project_context(project_id, user_id, db)

        # 组合完整的上下文
        full_context = f"{system_prompt}\n\n{project_context}" if project_context else system_prompt

        # 调用 AI 服务
        try:
            active_config = await get_active_ai_config(db, user_id, "agent")
            if active_config:
                ai_response = await ai_service._generate_text(
                    active_config,
                    message,
                    2000,
                    system=full_context,
                )
            elif settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your-anthropic-api-key":
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

                response = await client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    system=full_context,
                    messages=[
                        {
                            "role": "user",
                            "content": message
                        }
                    ]
                )

                ai_response = response.content[0].text

            else:
                # 使用模拟数据
                ai_response = f"这是对您消息的回复：{message}\n\n作为学术助手，我可以帮助您：\n1. 生成论文选题\n2. 构建论文大纲\n3. 搜索参考文献\n4. 撰写论文内容\n5. 提供写作建议\n\n请告诉我您需要什么帮助？"

            return {
                "content": ai_response,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "content": f"抱歉，处理您的消息时出现错误。请稍后再试。",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """构建系统提示"""
        base_prompt = """你是一位专业的学术写作助手，专门帮助学生完成学术论文写作。

你的职责包括：
1. 帮助学生选择合适的论文选题
2. 指导学生构建论文大纲
3. 推荐相关的学术文献
4. 协助撰写论文内容
5. 提供写作建议和修改意见

请用专业、友好的语气与学生交流，给出具体可行的建议。"""

        # 添加上下文信息
        if context.get("topic"):
            base_prompt += f"\n\n当前选题：{context['topic']}"

        if context.get("outline"):
            base_prompt += f"\n\n当前大纲：{context['outline']}"

        if context.get("major"):
            base_prompt += f"\n\n专业：{context['major']}"

        if context.get("education_level"):
            base_prompt += f"\n\n学历层次：{context['education_level']}"

        if context.get("paper_type"):
            base_prompt += f"\n\n论文类型：{context['paper_type']}"

        return base_prompt

    async def _get_project_context(
        self,
        project_id: int,
        user_id: int,
        db: AsyncSession
    ) -> str:
        """获取项目上下文信息"""
        context_parts = []

        # 获取项目信息
        project_result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == user_id
            )
        )
        project = project_result.scalar_one_or_none()

        if project:
            context_parts.append(f"项目：{project.title}")
            context_parts.append(f"专业：{project.major}")
            context_parts.append(f"学历：{project.education_level}")
            context_parts.append(f"论文类型：{project.paper_type}")

        # 获取已选择的选题
        topics_result = await db.execute(
            select(Topic).where(
                Topic.project_id == project_id,
                Topic.is_selected == True
            )
        )
        selected_topics = topics_result.scalars().all()

        if selected_topics:
            context_parts.append("\n已选择的选题：")
            for topic in selected_topics:
                context_parts.append(f"- {topic.title}")
                if topic.description:
                    context_parts.append(f"  说明：{topic.description}")

        # 获取最新的大纲
        outline_result = await db.execute(
            select(Outline).where(
                Outline.project_id == project_id
            ).order_by(Outline.created_at.desc()).limit(1)
        )
        outline = outline_result.scalar_one_or_none()

        if outline:
            context_parts.append(f"\n当前大纲：{outline.title}")

        return "\n".join(context_parts) if context_parts else ""


chat_service = ChatService()
