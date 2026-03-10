from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_in: UserCreate) -> User:
        """Registra um novo usuário"""
        email_check = await self.db.execute(
            select(User).where(User.email == user_in.email)
        )
        if email_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail já cadastrado no sistema."
            )

        username_check = await self.db.execute(
            select(User).where(User.username == user_in.username)
        )
        if username_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário já está em uso."
            )

        user_dict = user_in.model_dump()
        password = user_dict.pop("password")
        
        new_user = User(
            **user_dict,
            password_hash=get_password_hash(password)
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        return new_user

    async def authenticate_user(self, username: str, password: str):
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user

    async def get_user_by_id(self, user_id: UUID) -> User:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        
        return user

    async def get_user_by_username(self, username: str) -> User:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_users_by_department(self, department_id: UUID, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(User)
            .where(User.department_id == department_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search_users(self, query: str, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(User)
            .where(
                (User.nome.ilike(f"%{query}%")) |
                (User.sobrenome.ilike(f"%{query}%")) |
                (User.email.ilike(f"%{query}%")) |
                (User.username.ilike(f"%{query}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_user(self, user_id: UUID, user_data: dict) -> User:
        user = await self.get_user_by_id(user_id)
        
        if "email" in user_data and user_data["email"] != user.email:
            email_check = await self.db.execute(
                select(User).where(User.email == user_data["email"])
            )
            if email_check.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="E-mail já cadastrado no sistema."
                )
        
        if "username" in user_data and user_data["username"] != user.username:
            username_check = await self.db.execute(
                select(User).where(User.username == user_data["username"])
            )
            if username_check.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome de usuário já está em uso."
                )
        
        for key, value in user_data.items():
            if key == "password" and value:
                setattr(user, "password_hash", get_password_hash(value))
            elif hasattr(user, key):
                setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        user = await self.get_user_by_id(user_id)
        await self.db.delete(user)
        await self.db.commit()
        return True
