from fastapi import APIRouter, Depends, status, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, UserBase
from app.schemas.token import Token
from app.services.user_service import UserService
from app.services.audit_log_service import AuditLogService
from app.core.security import create_access_token, get_current_user
from app.models.user import User, UserRole
from uuid import UUID
from datetime import timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou password incorreto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar usuários."
        )
    
    if current_user.role == UserRole.MANAGER and user_in.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você pode criar usuários apenas no seu departamento."
        )
    
    user_service = UserService(db)
    audit_service = AuditLogService(db)
    
    new_user = await user_service.register_user(user_in)
    
    await audit_service.log_action(
        performed_by=current_user.id,
        action="CREATE",
        resource="USER",
        target_id=new_user.id
    )
    
    return new_user

@router.get("/", response_model=list[UserOut])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    
    if current_user.role == UserRole.SUPER:
        if search:
            users = await user_service.search_users(search, skip, limit)
        else:
            users = await user_service.get_all_users(skip, limit)
        return users
    
    elif current_user.role == UserRole.MANAGER:
        if search:
            all_results = await user_service.search_users(search, 0, 1000)
            dept_results = [u for u in all_results if u.department_id == current_user.department_id]
            return dept_results[skip:skip+limit]
        else:
            users = await user_service.get_users_by_department(
                current_user.department_id, skip, limit
            )
            return users
    
    else:
        return [current_user]

@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if current_user.role == UserRole.SUPER:
        return user
    
    elif current_user.role == UserRole.MANAGER:
        if user.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para ver este usuário."
            )
        return user
    
    else:
        if user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para ver este usuário."
            )
        return user

@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    user_data: UserBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    existing_user = await user_service.get_user_by_id(user_id)
    
    if current_user.role == UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para atualizar usuários."
        )
    
    if current_user.role == UserRole.MANAGER:
        if existing_user.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você pode atualizar apenas usuários do seu departamento."
            )
    
    audit_service = AuditLogService(db)
    
    update_data = user_data.model_dump(exclude_unset=True)
    updated_user = await user_service.update_user(user_id, update_data)
    
    await audit_service.log_action(
        performed_by=current_user.id,
        action="UPDATE",
        resource="USER",
        target_id=updated_user.id
    )
    
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deleta um usuário (apenas SUPER ou MANAGER do departamento)"""
    user_service = UserService(db)
    existing_user = await user_service.get_user_by_id(user_id)
    
    if current_user.role == UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar usuários."
        )
    
    if current_user.role == UserRole.MANAGER:
        if existing_user.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você pode deletar apenas usuários do seu departamento."
            )
    
    audit_service = AuditLogService(db)
    
    await user_service.delete_user(user_id)
    
    await audit_service.log_action(
        performed_by=current_user.id,
        action="DELETE",
        resource="USER",
        target_id=user_id
    )
    
    return None
