import pytest
from app.services.user_service import UserService
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserCreate
from app.models.user import UserRole


class TestUserService:
    
    @pytest.mark.asyncio
    async def test_register_user(self, db_session, department):
        user_service = UserService(db_session)
        
        user_data = UserCreate(
            username="newuser",
            email="newuser@test.com",
            nome="New",
            sobrenome="User",
            password="password123",
            role=UserRole.EMPLOYEE,
            department_id=department.id
        )
        
        user = await user_service.register_user(user_data)
        
        assert user.username == "newuser"
        assert user.email == "newuser@test.com"
        assert user.nome == "New"
        assert user.role == UserRole.EMPLOYEE
        assert verify_password("password123", user.password_hash)

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, db_session, employee_user):
        user_service = UserService(db_session)
        
        user_data = UserCreate(
            username="anotheruser",
            email=employee_user.email,
            nome="Another",
            sobrenome="User",
            password="password123",
            role=UserRole.EMPLOYEE,
            department_id=employee_user.department_id
        )
        
        with pytest.raises(Exception):
            await user_service.register_user(user_data)

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, db_session, employee_user):
        user_service = UserService(db_session)
        
        user_data = UserCreate(
            username=employee_user.username,
            email="different@test.com",
            nome="Another",
            sobrenome="User",
            password="password123",
            role=UserRole.EMPLOYEE,
            department_id=employee_user.department_id
        )
        
        with pytest.raises(Exception):
            await user_service.register_user(user_data)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session, employee_user):
        user_service = UserService(db_session)
        
        authenticated_user = await user_service.authenticate_user(
            "employee", "employee123"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.username == "employee"
        assert authenticated_user.id == employee_user.id

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, db_session, employee_user):
        user_service = UserService(db_session)
        
        authenticated_user = await user_service.authenticate_user(
            "employee", "wrongpassword"
        )
        
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, db_session):
        user_service = UserService(db_session)
        
        authenticated_user = await user_service.authenticate_user(
            "nonexistent", "password"
        )
        
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db_session, employee_user):
        user_service = UserService(db_session)
        
        user = await user_service.get_user_by_id(employee_user.id)
        
        assert user.id == employee_user.id
        assert user.username == "employee"

    @pytest.mark.asyncio
    async def test_get_user_by_id_nonexistent(self, db_session):
        from uuid import uuid4
        user_service = UserService(db_session)
        
        with pytest.raises(Exception):
            await user_service.get_user_by_id(uuid4())

    @pytest.mark.asyncio
    async def test_search_users(self, db_session, department):
        from app.models.user import User
        from uuid import uuid4
        
        user1 = User(
            id=uuid4(),
            username="john",
            email="john@test.com",
            nome="John",
            sobrenome="Doe",
            password_hash=get_password_hash("pass123"),
            role=UserRole.EMPLOYEE,
            department_id=department.id
        )
        user2 = User(
            id=uuid4(),
            username="jane",
            email="jane@test.com",
            nome="Jane",
            sobrenome="Smith",
            password_hash=get_password_hash("pass123"),
            role=UserRole.EMPLOYEE,
            department_id=department.id
        )
        db_session.add(user1)
        db_session.add(user2)
        await db_session.commit()
        
        user_service = UserService(db_session)
        
        results = await user_service.search_users("john")
        assert len(results) >= 1
        assert any(u.username == "john" for u in results)

    @pytest.mark.asyncio
    async def test_get_all_users(self, db_session, super_user, manager_user, employee_user):
        user_service = UserService(db_session)
        
        users = await user_service.get_all_users()
        
        assert len(users) >= 3
        usernames = [u.username for u in users]
        assert "admin" in usernames
        assert "manager" in usernames
        assert "employee" in usernames

    @pytest.mark.asyncio
    async def test_update_user(self, db_session, employee_user):
        """Test user update."""
        user_service = UserService(db_session)
        
        update_data = {"nome": "Updated Name"}
        updated_user = await user_service.update_user(employee_user.id, update_data)
        
        assert updated_user.nome == "Updated Name"
        assert updated_user.id == employee_user.id

    @pytest.mark.asyncio
    async def test_delete_user(self, db_session, employee_user):
        """Test user deletion."""
        user_service = UserService(db_session)
        user_id = employee_user.id
        
        result = await user_service.delete_user(user_id)
        assert result is True
        
        with pytest.raises(Exception):
            await user_service.get_user_by_id(user_id)
