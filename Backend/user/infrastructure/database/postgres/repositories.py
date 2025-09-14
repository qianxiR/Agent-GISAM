"""
PostgreSQL 仓储实现
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any, cast
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from domains.user.entities import UserEntity
from domains.user.repositories import UserRepository
from infrastructure.database.postgres.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, cast


def _model_to_entity(model: UserModel) -> UserEntity:
    return UserEntity(
        id=cast(UUID, model.id),
        email=cast(str, model.email),
        username=cast(str, model.username),
        hashed_password=cast(str, model.hashed_password),
        phone=cast(Optional[str], model.phone),
        is_active=cast(bool, model.is_active),
        is_superuser=cast(bool, model.is_superuser),
        created_at=cast(Optional[datetime], model.created_at),
        updated_at=cast(Optional[datetime], model.updated_at),
        last_login=cast(Optional[datetime], model.last_login),
    )


class PostgreSQLUserRepository(UserRepository):
    """基于 SQLAlchemy AsyncSession 的用户仓储实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserEntity) -> UserEntity:
        model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _model_to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        stmt = select(UserModel).where(UserModel.username == username.strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        if not phone:
            return None
        stmt = select(UserModel).where(UserModel.phone == phone.strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_login_identifier(self, identifier: str) -> Optional[UserEntity]:
        identifier = identifier.strip()
        # username
        user = await self.get_by_username(identifier)
        if user:
            return user
        # email
        user = await self.get_by_email(identifier)
        if user:
            return user
        # phone
        return await self.get_by_phone(identifier)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_model_to_entity(m) for m in models]

    async def get_active_users(self) -> List[UserEntity]:
        stmt = select(UserModel).where(UserModel.is_active.is_(True))
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_model_to_entity(m) for m in models]

    async def update(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[UserEntity]:
        # 执行更新
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values({**update_data, "updated_at": func.now()})
            .returning(UserModel)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def update_last_login(self, user_id: UUID) -> bool:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login=func.now(), updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete(self, user_id: UUID) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def soft_delete(self, user_id: UUID) -> bool:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=False, updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.username == username.strip())
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def exists_by_phone(self, phone: str) -> bool:
        if not phone:
            return False
        stmt = select(func.count()).select_from(UserModel).where(UserModel.phone == phone.strip())
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def get_user_stats(self) -> Dict[str, int]:
        total_stmt = select(func.count()).select_from(UserModel)
        active_stmt = select(func.count()).select_from(UserModel).where(UserModel.is_active.is_(True))
        today = func.current_date()
        new_today_stmt = select(func.count()).select_from(UserModel).where(func.date(UserModel.created_at) == today)

        total = (await self.session.execute(total_stmt)).scalar_one()
        active = (await self.session.execute(active_stmt)).scalar_one()
        new_today = (await self.session.execute(new_today_stmt)).scalar_one()

        return {
            "total_users": int(total or 0),
            "active_users": int(active or 0),
            "new_users_today": int(new_today or 0),
        }


