import asyncio
import os
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.department import Department
from app.db.base import Base

ID_DEPT_FINANCEIRO = UUID("b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
ID_DEPT_COMERCIAL = UUID("c1f0bd00-0d1c-4f11-8888-7cc0ce491b22")
ID_DEPT_TI = UUID("d2e1fc11-1e2d-5f22-9999-8dd1df502c33")

ID_USER_SUPER = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
ID_USER_MANAGER_FIN = UUID("a1b2c3d4-e5f6-4a5b-bc6d-7e8f9a0b1c2d")
ID_USER_EMPLOYEE_FIN = UUID("d1e2f3a4-b5c6-4d7e-8f9a-0b1c2d3e4f5a")
ID_USER_EMPLOYEE_TI = UUID("e2f3a4b5-c6d7-4e8f-9a0b-1c2d3e4f5a6b")

async def seed_database():
    super_password = os.getenv("SEED_SUPER_PASSWORD", "super123")
    manager_password = os.getenv("SEED_MANAGER_PASSWORD", "manager123")
    employee_password = os.getenv("SEED_EMPLOYEE_PASSWORD", "employee123")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        result = await session.execute(select(User).where(User.username == "super"))
        if result.scalars().first():
            print("[INFO] Dados ja existem. Abortando...")
            await engine.dispose()
            return
        
        dept_financeiro = Department(id=ID_DEPT_FINANCEIRO, name="Financeiro")
        dept_comercial = Department(id=ID_DEPT_COMERCIAL, name="Comercial")
        dept_ti = Department(id=ID_DEPT_TI, name="TI")
        
        session.add_all([dept_financeiro, dept_comercial, dept_ti])
        await session.flush()
        
        super_user = User(
            id=ID_USER_SUPER,
            username="super",
            email="super@propig.com",
            nome="Super",
            sobrenome="Admin",
            password_hash=get_password_hash(super_password),
            role=UserRole.SUPER,
            department_id=None
        )
        
        manager_fin = User(
            id=ID_USER_MANAGER_FIN,
            username="gerente_financeiro",
            email="gerente.financeiro@propig.com",
            nome="Joao",
            sobrenome="Financeiro",
            password_hash=get_password_hash(manager_password),
            role=UserRole.MANAGER,
            department_id=ID_DEPT_FINANCEIRO
        )
        
        employee_fin = User(
            id=ID_USER_EMPLOYEE_FIN,
            username="funcionario_fin",
            email="funcionario.fin@propig.com",
            nome="Pedro",
            sobrenome="Contador",
            password_hash=get_password_hash(employee_password),
            role=UserRole.EMPLOYEE,
            department_id=ID_DEPT_FINANCEIRO
        )

        employee_ti = User(
            id=ID_USER_EMPLOYEE_TI,
            username="funcionario_ti",
            email="funcionario.ti@propig.com",
            nome="Carlos",
            sobrenome="Dev",
            password_hash=get_password_hash(employee_password),
            role=UserRole.EMPLOYEE,
            department_id=ID_DEPT_TI
        )
        
        session.add_all([super_user, manager_fin, employee_fin, employee_ti])
        await session.commit()
        
    await engine.dispose()
    print("[SUCCESS] Banco populado com IDs fixos para teste.")

if __name__ == "__main__":
    asyncio.run(seed_database())