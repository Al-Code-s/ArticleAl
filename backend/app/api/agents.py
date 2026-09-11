"""
智能体API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project, AgentStatus
from app.models.agent_session import AgentSession, SessionStatus
from app.schemas.agent import AgentSessionResponse

router = APIRouter()


@router.post("/{project_id}/start")
async def start_agent(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """启动项目的智能体"""
    # 验证项目
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 如果已有活跃会话，直接返回
    if project.agent_session_id:
        session_result = await db.execute(
            select(AgentSession).where(AgentSession.id == project.agent_session_id)
        )
        existing_session = session_result.scalar_one_or_none()
        if existing_session and existing_session.status == SessionStatus.ACTIVE:
            return {"status": "already_running", "session_id": existing_session.session_id}

    # 创建新会话
    import uuid
    new_session = AgentSession(
        session_id=f"session_{uuid.uuid4().hex[:12]}",
        project_id=project_id,
        status=SessionStatus.ACTIVE,
        context={
            "project_title": project.title,
            "major": project.major,
            "education_level": project.education_level,
        }
    )
    db.add(new_session)
    await db.flush()

    # 更新项目状态
    project.agent_session_id = new_session.id
    project.agent_status = AgentStatus.RUNNING

    await db.commit()
    await db.refresh(new_session)

    return {"status": "started", "session_id": new_session.session_id}


@router.post("/{project_id}/stop")
async def stop_agent(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """停止项目的智能体"""
    # 验证项目
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 如果有活跃会话，停止它
    if project.agent_session_id:
        session_result = await db.execute(
            select(AgentSession).where(AgentSession.id == project.agent_session_id)
        )
        session = session_result.scalar_one_or_none()
        if session:
            session.status = SessionStatus.STOPPED
            from datetime import datetime
            session.ended_at = datetime.utcnow()

    # Close the in-process Claude SDK runtime for this project if present.
    from app.api.chat import _agent_runtimes
    runtime = _agent_runtimes.pop((current_user.id, project_id), None)
    if runtime:
        await runtime.close()

    # 更新项目状态
    project.agent_status = AgentStatus.STOPPED

    await db.commit()

    return {"status": "stopped"}
