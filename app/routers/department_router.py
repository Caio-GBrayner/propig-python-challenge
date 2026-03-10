from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.department import DepartmentCreate, DepartmentOut
from app.services.department_service import DepartmentService
from app.services.audit_log_service import AuditLogService
from app.core.security import get_current_user
from app.models.user import User, UserRole
from uuid import UUID

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_in: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.SUPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o perfil SUPER pode criar departamentos."
        )
    
    dept_service = DepartmentService(db)
    audit_service = AuditLogService(db)
    
    new_dept = await dept_service.create_department(dept_in)
    
    await audit_service.log_action(
        performed_by=current_user.id,
        action="CREATE",
        resource="DEPARTMENT",
        target_id=new_dept.id
    )
    
    return new_dept

@router.get("/", response_model=list[DepartmentOut])
async def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista departamentos"""
    dept_service = DepartmentService(db)
    
    if search:
        depts = await dept_service.search_departments(search, skip, limit)
    else:
        depts = await dept_service.get_all_departments(skip, limit)
    
    return depts

@router.get("/{dept_id}", response_model=DepartmentOut)
async def get_department(
    dept_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    dept_service = DepartmentService(db)
    return await dept_service.get_department_by_id(dept_id)

@router.put("/{dept_id}", response_model=DepartmentOut)
async def update_department(
    dept_id: UUID,
    dept_data: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.SUPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o perfil SUPER pode atualizar departamentos."
        )
    
    dept_service = DepartmentService(db)
    audit_service = AuditLogService(db)
    
    update_data = dept_data.model_dump(exclude_unset=True)
    updated_dept = await dept_service.update_department(dept_id, update_data)
    
    await audit_service.log_action(
        performed_by=current_user.id,
        action="UPDATE",
        resource="DEPARTMENT",
        target_id=updated_dept.id
    )
    
    return updated_dept

@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    dept_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.SUPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o perfil SUPER pode deletar departamentos."
        )
    
    dept_service = DepartmentService(db)
    audit_service = AuditLogService(db)
    
    await dept_service.delete_department(dept_id)
    
    await audit_service.log_action(
        performed_by=current_user.id,
        action="DELETE",
        resource="DEPARTMENT",
        target_id=dept_id
    )
    
    return None
