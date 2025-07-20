"""
Base Pydantic schemas for request/response models
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration"""

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""

    created_at: datetime
    updated_at: datetime


class APIResponse(BaseSchema):
    """Standardized API response format"""

    data: Any
    meta: Dict[str, Any]
    errors: Optional[List[str]] = None

    @classmethod
    def success(cls, data: Any, meta: Optional[Dict[str, Any]] = None) -> "APIResponse":
        """Create successful response"""
        return cls(
            data=data,
            meta={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0",
                **(meta or {}),
            },
        )

    @classmethod
    def error(
        cls, errors: List[str], meta: Optional[Dict[str, Any]] = None
    ) -> "APIResponse":
        """Create error response"""
        return cls(
            data=None,
            meta={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0",
                **(meta or {}),
            },
            errors=errors,
        )


class PaginationParams(BaseSchema):
    """Pagination parameters"""

    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginationMeta(BaseSchema):
    """Pagination metadata"""

    page: int
    size: int
    total: int
    pages: int
