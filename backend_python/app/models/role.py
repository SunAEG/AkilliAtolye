"""
Role model + repository.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import asyncpg

from app.models.base import BaseTimestampedRecord


@dataclass
class RoleRecord(BaseTimestampedRecord):

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> "RoleRecord":
        return cls(
            id=row["id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            value=cls._parse_value(row["value"]),
        )


class RoleRepository:

    @staticmethod
    async def get_all(conn: asyncpg.Connection) -> list[RoleRecord]:
        rows = await conn.fetch("SELECT * FROM roles ORDER BY id")
        return [RoleRecord.from_row(r) for r in rows]

    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, role_id: int) -> RoleRecord | None:
        row = await conn.fetchrow("SELECT * FROM roles WHERE id = $1", role_id)
        return RoleRecord.from_row(row) if row else None

    @staticmethod
    async def create(conn: asyncpg.Connection, value: dict[str, Any]) -> RoleRecord:
        row = await conn.fetchrow(
            "INSERT INTO roles (value) VALUES ($1) RETURNING *",
            json.dumps(value),
        )
        return RoleRecord.from_row(row)

    @staticmethod
    async def update(
        conn: asyncpg.Connection, role_id: int, value: dict[str, Any]
    ) -> RoleRecord | None:
        row = await conn.fetchrow(
            "UPDATE roles SET value = value || $1::JSONB WHERE id = $2 RETURNING *",
            json.dumps(value), role_id,
        )
        return RoleRecord.from_row(row) if row else None

    @staticmethod
    async def delete(conn: asyncpg.Connection, role_id: int) -> bool:
        result = await conn.execute("DELETE FROM roles WHERE id = $1", role_id)
        return result == "DELETE 1"

    @staticmethod
    async def assign_screen(
        conn: asyncpg.Connection,
        role_id: int,
        screen_id: int,
        can_create: bool = True,
        can_read: bool = True,
        can_update: bool = False,
        can_delete: bool = False,
        file_types: list[str] | None = None,
    ) -> RoleRecord | None:
        ft = json.dumps(file_types or ["txt", "png", "jpg", "jpeg", "pdf"])
        await conn.execute(
            "CALL sp_assign_screen_to_role($1,$2,$3,$4,$5,$6,$7::JSONB)",
            role_id, screen_id, can_create, can_read, can_update, can_delete, ft,
        )
        return await RoleRepository.get_by_id(conn, role_id)

    @staticmethod
    async def remove_screen(
        conn: asyncpg.Connection, role_id: int, screen_id: int
    ) -> RoleRecord | None:
        await conn.execute(
            "CALL sp_remove_screen_from_role($1, $2)", role_id, screen_id
        )
        return await RoleRepository.get_by_id(conn, role_id)
