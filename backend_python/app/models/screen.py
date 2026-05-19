"""
Screen model + repository.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import asyncpg

from app.models.base import BaseTimestampedRecord


@dataclass
class ScreenRecord(BaseTimestampedRecord):

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> "ScreenRecord":
        return cls(
            id=row["id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            value=cls._parse_value(row["value"]),
        )


class ScreenRepository:

    @staticmethod
    async def get_all(conn: asyncpg.Connection, active_only: bool = False) -> list[ScreenRecord]:
        if active_only:
            rows = await conn.fetch(
                "SELECT * FROM screens WHERE (value->>'is_active')::BOOLEAN = true ORDER BY (value->>'order')::INT"
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM screens ORDER BY (value->>'order')::INT NULLS LAST"
            )
        return [ScreenRecord.from_row(r) for r in rows]

    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, screen_id: int) -> ScreenRecord | None:
        row = await conn.fetchrow("SELECT * FROM screens WHERE id = $1", screen_id)
        return ScreenRecord.from_row(row) if row else None

    @staticmethod
    async def create(conn: asyncpg.Connection, value: dict[str, Any]) -> ScreenRecord:
        row = await conn.fetchrow(
            "INSERT INTO screens (value) VALUES ($1) RETURNING *",
            json.dumps(value),
        )
        return ScreenRecord.from_row(row)

    @staticmethod
    async def update(
        conn: asyncpg.Connection, screen_id: int, value: dict[str, Any]
    ) -> ScreenRecord | None:
        row = await conn.fetchrow(
            "UPDATE screens SET value = value || $1::JSONB WHERE id = $2 RETURNING *",
            json.dumps(value), screen_id,
        )
        return ScreenRecord.from_row(row) if row else None

    @staticmethod
    async def delete(conn: asyncpg.Connection, screen_id: int) -> bool:
        result = await conn.execute("DELETE FROM screens WHERE id = $1", screen_id)
        return result == "DELETE 1"
