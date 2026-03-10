import uuid
from enum import Enum
from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from datetime import datetime

class UserRole(str, Enum):
    SUPER = "SUPER"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    sobrenome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    
    role: Mapped[UserRole] = mapped_column(String, default=UserRole.EMPLOYEE, nullable=False)

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("departments.id", ondelete="SET NULL"), 
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"), nullable=False)

    department: Mapped["Department"] = relationship("Department", back_populates="users")
    logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="author")