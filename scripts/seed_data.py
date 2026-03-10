import asyncio
import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.department import Department
from app.db.base import Base

async def seed_database():
    super_password = os.getenv("SEED_SUPER_PASSWORD", "super123")
    manager_password = os.getenv("SEED_MANAGER_PASSWORD", "manager123")
    employee_password = os.getenv("SEED_EMPLOYEE_PASSWORD", "employee123")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("[INFO] Tabelas criadas/verificadas")
        
        result = await session.execute(
            select(User).where(User.username == "super")
        )
        if result.scalars().first():
            print("[INFO] Dados de teste já existem. Abortando...")
            await engine.dispose()
            return
        
        dept_financeiro = Department(
            id=uuid4(),
            name="Financeiro"
        )
        dept_comercial = Department(
            id=uuid4(),
            name="Comercial"
        )
        dept_ti = Department(
            id=uuid4(),
            name="TI"
        )
        
        session.add_all([dept_financeiro, dept_comercial, dept_ti])
        await session.flush()
        
        print(f"[INFO] Departamentos criados: {dept_financeiro.name}, {dept_comercial.name}, {dept_ti.name}")
        
        super_user = User(
            id=uuid4(),
            username="super",
            email="super@propig.com",
            nome="Super",
            sobrenome="Admin",
            password_hash=get_password_hash(super_password),
            role=UserRole.SUPER,
            department_id=None
        )
        
        manager_fin = User(
            id=uuid4(),
            username="gerente_financeiro",
            email="gerente.financeiro@propig.com",
            nome="João",
            sobrenome="Financeiro",
            password_hash=get_password_hash(manager_password),
            role=UserRole.MANAGER,
            department_id=dept_financeiro.id
        )
        
        manager_com = User(
            id=uuid4(),
            username="gerente_comercial",
            email="gerente.comercial@propig.com",
            nome="Maria",
            sobrenome="Comercial",
            password_hash=get_password_hash(manager_password),
            role=UserRole.MANAGER,
            department_id=dept_comercial.id
        )
        
        employee_fin = User(
            id=uuid4(),
            username="funcionario_fin",
            email="funcionario.fin@propig.com",
            nome="Pedro",
            sobrenome="Contador",
            password_hash=get_password_hash(employee_password),
            role=UserRole.EMPLOYEE,
            department_id=dept_financeiro.id
        )
        
        employee_ti = User(
            id=uuid4(),
            username="funcionario_ti",
            email="funcionario.ti@propig.com",
            nome="Carlos",
            sobrenome="Dev",
            password_hash=get_password_hash(employee_password),
            role=UserRole.EMPLOYEE,
            department_id=dept_ti.id
        )
        
        session.add_all([super_user, manager_fin, manager_com, employee_fin, employee_ti])
        await session.commit()
        
        print("[INFO] Usuários de teste criados:")
        print(f"  - SUPER: super / {super_password}")
        print(f"  - MANAGER (Financeiro): gerente_financeiro / {manager_password}")
        print(f"  - MANAGER (Comercial): gerente_comercial / {manager_password}")
        print(f"  - EMPLOYEE (Financeiro): funcionario_fin / {employee_password}")
        print(f"  - EMPLOYEE (TI): funcionario_ti / {employee_password}")
    
    await engine.dispose()
    print("\n✓ Banco de dados populado com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed_database())
