"""
用户资料相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user, verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserResponse, UserProfileUpdate, PasswordChangeRequest

router = APIRouter()


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新个人信息"""
    update_data = profile_data.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"] != current_user.username:
        result = await db.execute(select(User).where(User.username == update_data["username"]))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

    if "email" in update_data and update_data["email"] != current_user.email:
        result = await db.execute(select(User).where(User.email == update_data["email"]))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码不正确"
        )

    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": "密码修改成功"}
