"""
WebSocket 聊天 API
"""
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.services.chat_service import chat_service
from app.agent_runtime import ProjectAgentService, AgentRuntimeUnavailable
from app.services.skill_service import resolve_skill, with_context

_agent_runtimes: dict[tuple[int, int], ProjectAgentService] = {}

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """连接 WebSocket"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """断开连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_json(message)

    async def broadcast(self, message: dict, user_id: int):
        """向用户的所有连接广播消息"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket 端点用于实时聊天

    客户端需要在查询参数中传递 JWT token: /ws?token=xxx

    消息格式:
    客户端 -> 服务器:
    {
        "type": "message",
        "project_id": 1,
        "content": "用户消息内容",
        "context": {
            "topic": "选题内容",
            "outline": "大纲内容"
        }
    }

    服务器 -> 客户端:
    {
        "type": "message" | "thinking" | "error",
        "content": "AI 回复内容",
        "timestamp": "2024-01-01T00:00:00"
    }
    """
    # 验证 token
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return

        user_id = int(user_id)
    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # 连接 WebSocket
    await manager.connect(websocket, user_id)

    try:
        # 发送欢迎消息
        await manager.send_personal_message({
            "type": "system",
            "content": "已连接到 AI 助手，您可以开始对话了"
        }, websocket)

        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "message":
                # 发送思考中状态
                await manager.send_personal_message({
                    "type": "thinking",
                    "content": "AI 正在思考..."
                }, websocket)

                # 调用 AI 服务处理消息
                try:
                    project_id = message_data.get("project_id")
                    runtime = _agent_runtimes.get((user_id, int(project_id))) if project_id else None
                    if project_id and runtime is None:
                        # Build a project-scoped SDK session lazily. If the SDK is not
                        # installed/configured, the existing compatible provider path remains active.
                        from sqlalchemy import select
                        from app.models.project import Project
                        result = await db.execute(select(Project).where(Project.id == int(project_id), Project.user_id == user_id))
                        project = result.scalar_one_or_none()
                        if project:
                            skill = with_context(await resolve_skill(db, user_id, "chat"), {
                                "项目标题": project.title, "专业": project.major,
                                "学历层次": project.education_level, "论文类型": project.paper_type,
                            })
                            runtime = ProjectAgentService(int(project_id), {
                                "project_id": project.id, "title": project.title,
                                "major": project.major, "education_level": project.education_level,
                                "paper_type": project.paper_type,
                            }, skill)
                            try:
                                await runtime.start()
                                _agent_runtimes[(user_id, int(project_id))] = runtime
                            except AgentRuntimeUnavailable:
                                runtime = None

                    if runtime:
                        chunks = []
                        async for event in runtime.send(message_data.get("content", "")):
                            if event.get("type") == "message" and event.get("content"):
                                chunks.append(str(event["content"]))
                        response = {"content": "\n".join(chunks), "timestamp": __import__("datetime").datetime.utcnow().isoformat()}
                    else:
                        response = await chat_service.chat(
                        user_id=user_id,
                        project_id=project_id,
                        message=message_data.get("content", ""),
                        context=message_data.get("context", {}),
                        db=db
                        )

                    # 发送 AI 回复
                    await manager.send_personal_message({
                        "type": "message",
                        "content": response["content"],
                        "timestamp": response["timestamp"]
                    }, websocket)

                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "content": f"处理消息时出错: {str(e)}"
                    }, websocket)

            elif message_data.get("type") == "ping":
                # 心跳响应
                await manager.send_personal_message({
                    "type": "pong"
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        print(f"WebSocket error: {e}")
