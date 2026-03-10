import asyncio
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.department import Department
from app.core.security import get_password_hash


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def department(db_session):
    dept = Department(
        id=uuid4(),
        name="Test Department"
    )
    db_session.add(dept)
    await db_session.commit()
    await db_session.refresh(dept)
    return dept


@pytest.fixture
async def super_user(db_session):
    user = User(
        id=uuid4(),
        username="admin",
        email="admin@test.com",
        nome="Admin",
        sobrenome="User",
        password_hash=get_password_hash("admin123"),
        role=UserRole.SUPER,
        department_id=None
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def manager_user(db_session, department):
    user = User(
        id=uuid4(),
        username="manager",
        email="manager@test.com",
        nome="Manager",
        sobrenome="User",
        password_hash=get_password_hash("manager123"),
        role=UserRole.MANAGER,
        department_id=department.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def employee_user(db_session, department):
    user = User(
        id=uuid4(),
        username="employee",
        email="employee@test.com",
        nome="Employee",
        sobrenome="User",
        password_hash=get_password_hash("employee123"),
        role=UserRole.EMPLOYEE,
        department_id=department.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
