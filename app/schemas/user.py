from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr
    nome: str
    sobrenome: str
    role: UserRole = UserRole.EMPLOYEE
    department_id: Optional[UUID] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    role: Optional[UserRole] = None
    department_id: Optional[UUID] = None