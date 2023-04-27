from pydantic import BaseModel, Field, validator
from typing import Optional

class RoleCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    max_archivos: Optional[int] = None
    max_firmas: Optional[int] = None

    @validator("max_archivos", pre=True)
    def validate_max_archivos(cls, value):
        if value is not None and value < 1:
            raise ValueError("max_archivos debe ser mayor o igual a 1")
        return value

    @validator("max_firmas", pre=True)
    def validate_max_firmas(cls, value):
        if value is not None and value < 1:
            raise ValueError("max_firmas debe ser mayor o igual a 1")
        return value


# Schema DeleteResponse
class DeleteResponse(BaseModel):
    message: str
