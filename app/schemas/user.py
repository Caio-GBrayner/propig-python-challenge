from uuid import UUID
from datetime import datetime
from typing import Optional
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