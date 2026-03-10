from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.models.user import User
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class AuditLogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self, 
        performed_by: UUID, 
        action: str, 
        resource: str, 
        target_id: UUID
    ) -> AuditLog:
        """Cria um registro de auditoria"""
        log = AuditLog(
            performed_by=performed_by,
            action=action,
            resource=resource,
            target_id=target_id
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        return log

    async def get_audit_logs(self, skip: int = 0, limit: int = 100):
        """Lista todos os registros de auditoria"""
        result = await self.db.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_logs_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100):
        """Lista registros de auditoria de um usuário específico"""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.performed_by == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_logs_by_resource(self, resource: str, skip: int = 0, limit: int = 100):
        """Lista registros de auditoria para um recurso específico"""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.resource == resource)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_logs_by_target(self, target_id: UUID, skip: int = 0, limit: int = 100):
        """Lista registros de auditoria para um alvo específico"""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
