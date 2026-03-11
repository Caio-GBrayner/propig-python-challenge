from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.department import Department
from app.schemas.department import DepartmentCreate
from uuid import UUID

class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_department(self, dept_in: DepartmentCreate) -> Department:
        name_check = await self.db.execute(
            select(Department).where(Department.name == dept_in.name)
        )
        if name_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Departamento com este nome já existe."
            )

        new_dept = Department(name=dept_in.name)
        self.db.add(new_dept)
        await self.db.commit()
        await self.db.refresh(new_dept)
        return new_dept

    async def get_department_by_id(self, dept_id: UUID) -> Department:
        result = await self.db.execute(
            select(Department).where(Department.id == dept_id)
        )
        dept = result.scalars().first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Departamento não encontrado."
            )
        return dept

    async def get_all_departments(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(Department).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def search_departments(self, query: str, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(Department)
            .where(Department.name.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_department(self, dept_id: UUID, dept_data: dict) -> Department:
        dept = await self.get_department_by_id(dept_id)
        if "name" in dept_data and dept_data["name"] != dept.name:
            name_check = await self.db.execute(
                select(Department).where(Department.name == dept_data["name"])
            )
            if name_check.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Departamento com este nome já existe."
                )
        for key, value in dept_data.items():
            if hasattr(dept, key):
                setattr(dept, key, value)
        await self.db.commit()
        await self.db.refresh(dept)
        return dept

    async def delete_department(self, dept_id: UUID) -> bool:
        dept = await self.get_department_by_id(dept_id)
        await self.db.delete(dept)
        await self.db.commit()
        return True