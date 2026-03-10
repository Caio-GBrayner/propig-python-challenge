import pytest
from app.services.department_service import DepartmentService
from app.schemas.department import DepartmentCreate
from uuid import uuid4


class TestDepartmentService:
    
    @pytest.mark.asyncio
    async def test_create_department(self, db_session):
        dept_service = DepartmentService(db_session)
        
        dept_data = DepartmentCreate(name="New Department")
        dept = await dept_service.create_department(dept_data)
        
        assert dept.name == "New Department"
        assert dept.id is not None

    @pytest.mark.asyncio
    async def test_create_department_duplicate_name(self, db_session, department):
        dept_service = DepartmentService(db_session)
        
        dept_data = DepartmentCreate(name=department.name)
        
        with pytest.raises(Exception):
            await dept_service.create_department(dept_data)

    @pytest.mark.asyncio
    async def test_get_department_by_id(self, db_session, department):
        dept_service = DepartmentService(db_session)
        
        dept = await dept_service.get_department_by_id(department.id)
        
        assert dept.id == department.id
        assert dept.name == department.name

    @pytest.mark.asyncio
    async def test_get_department_by_id_nonexistent(self, db_session):
        dept_service = DepartmentService(db_session)
        
        with pytest.raises(Exception):
            await dept_service.get_department_by_id(uuid4())

    @pytest.mark.asyncio
    async def test_get_all_departments(self, db_session, department):
        dept_service = DepartmentService(db_session)
        
        depts = await dept_service.get_all_departments()
        
        assert len(depts) >= 1
        assert any(d.id == department.id for d in depts)

    @pytest.mark.asyncio
    async def test_search_departments(self, db_session, department):
        dept_service = DepartmentService(db_session)
        
        results = await dept_service.search_departments("Test")
        
        assert len(results) >= 1
        assert any(d.id == department.id for d in results)

    @pytest.mark.asyncio
    async def test_update_department(self, db_session, department):
        dept_service = DepartmentService(db_session)
        
        update_data = {"name": "Updated Department"}
        updated_dept = await dept_service.update_department(department.id, update_data)
        
        assert updated_dept.name == "Updated Department"
        assert updated_dept.id == department.id

    @pytest.mark.asyncio
    async def test_delete_department(self, db_session, department):
        dept_service = DepartmentService(db_session)
        dept_id = department.id
        
        result = await dept_service.delete_department(dept_id)
        assert result is True
        
        with pytest.raises(Exception):
            await dept_service.get_department_by_id(dept_id)
