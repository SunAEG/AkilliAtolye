"""
BaseRecord: Tüm JSONB tabanlı modeller için temel sınıf.
asyncpg Record nesnelerini Python dataclass'larına dönüştürür.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BaseRecord:
    id: int
    created_at: datetime
    value: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------------
    # asyncpg Row → dataclass
    # ---------------------------------------------------------------
    @classmethod
    def _parse_value(cls, raw_value: Any) -> dict:
        """asyncpg JSONB'yi dict'e çevirir (string veya dict gelebilir)."""
        if raw_value is None:
            return {}
        if isinstance(raw_value, str):
            return json.loads(raw_value)
        return dict(raw_value)

    # ---------------------------------------------------------------
    # Serileştirme (API yanıtları için)
    # ---------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            **self.value,
        }


@dataclass
class BaseTimestampedRecord(BaseRecord):
    """updated_at'i olan tablolar için (users, roles, screens)."""
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["updated_at"] = self.updated_at.isoformat()
        return d
