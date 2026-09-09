"""Authenticated skill management; defaults remain immutable on disk."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.skill import SkillOverride
from app.skills import SKILLS
from datetime import datetime

router = APIRouter()


class SkillUpdate(BaseModel):
    instructions: str = Field(min_length=1, max_length=30000)

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, value):
        if not value.strip():
            raise ValueError("技能内容不能为空")
        return value.strip()


class SkillResponse(BaseModel):
    key: str
    name: str
    description: str
    output_format: str
    instructions: str
    default_instructions: str
    is_customized: bool
    updated_at: datetime | None = None


def response_for(key, override=None):
    if key not in SKILLS:
        raise HTTPException(404, "Skill 不存在")
    skill = SKILLS[key]
    return SkillResponse(
        key=key, name=skill.name, description=skill.description,
        output_format=skill.output_format, default_instructions=skill.instructions,
        instructions=override.instructions if override else skill.instructions,
        is_customized=override is not None,
        updated_at=override.updated_at if override else None,
    )


@router.get("", response_model=list[SkillResponse])
async def list_skills(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SkillOverride).where(SkillOverride.user_id == user.id))
    overrides = {row.skill_key: row for row in result.scalars()}
    return [response_for(key, overrides.get(key)) for key in SKILLS]


@router.put("/{key}", response_model=SkillResponse)
async def save_skill(key: str, request: SkillUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    response_for(key)  # Validate before writing; keys are never used as arbitrary paths.
    now = datetime.utcnow()
    statement = insert(SkillOverride).values(
        user_id=user.id, skill_key=key, instructions=request.instructions, updated_at=now,
    ).on_conflict_do_update(
        index_elements=["user_id", "skill_key"],
        set_={"instructions": request.instructions, "updated_at": now},
    )
    await db.execute(statement)
    await db.commit()
    return response_for(key, SkillOverride(instructions=request.instructions, updated_at=now))


@router.delete("/{key}", response_model=SkillResponse)
async def reset_skill(key: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    response = response_for(key)
    await db.execute(delete(SkillOverride).where(
        SkillOverride.user_id == user.id, SkillOverride.skill_key == key,
    ))
    await db.commit()
    return response
