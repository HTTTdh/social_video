

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from .common import ORMModel
from datetime import datetime

# Roles
class RoleCreateIn(BaseModel):
    name: str
    permissions: Optional[Dict[str, Any]] = None

class RoleUpdateIn(BaseModel):
    name: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None

class RoleOut(ORMModel):
    id: int
    name: str
    permissions: Optional[dict] = None
    
class RoleRef(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

#Users    
class UserCreate(BaseModel):
    username: str
    email: str
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role_ids: Optional[List[int]] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserOut(ORMModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    roles: List[RoleRef] = Field(default_factory=list) 
    created_at: datetime
    updated_at: Optional[datetime] = None

