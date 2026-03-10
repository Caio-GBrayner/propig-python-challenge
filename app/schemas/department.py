from pydantic import BaseModel, ConfigDict
from uuid import UUID

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentOut(DepartmentBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)