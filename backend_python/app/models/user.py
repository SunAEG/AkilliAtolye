"""
User model + repository (asyncpg, JSONB-first).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import asyncpg

from app.models.base import BaseTimestampedRecord


@dataclass
class UserRecord(BaseTimestampedRecord):
    group_type: str = "student"

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> "UserRecord":
        return cls(
            id=row["id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            group_type=row["group_type"],
            value=cls._parse_value(row["value"]),
        )

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["group_type"] = self.group_type
        # Şifreyi asla döndürme
        d.pop("password_hash", None)
        return d


# ---------------------------------------------------------------
# Repository
# ---------------------------------------------------------------
class UserRepository:

    @staticmethod
    async def get_all(
        conn: asyncpg.Connection,
        limit: int = 50,
        offset: int = 0,
        group_type: str | None = None,
    ) -> list[UserRecord]:
        if group_type:
            rows = await conn.fetch(
                "SELECT * FROM users WHERE group_type = $1 ORDER BY id LIMIT $2 OFFSET $3",
                group_type, limit, offset,
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM users ORDER BY id LIMIT $1 OFFSET $2",
                limit, offset,
            )
        return [UserRecord.from_row(r) for r in rows]

    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, user_id: int) -> UserRecord | None:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return UserRecord.from_row(row) if row else None

    @staticmethod
    async def get_by_email(conn: asyncpg.Connection, email: str) -> UserRecord | None:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE value->>'email' = $1", email
        )
        return UserRecord.from_row(row) if row else None

    @staticmethod
    async def create(
        conn: asyncpg.Connection,
        group_type: str,
        value: dict[str, Any],
    ) -> UserRecord:
        row = await conn.fetchrow(
            "INSERT INTO users (group_type, value) VALUES ($1, $2) RETURNING *",
            group_type,
            json.dumps(value),
        )
        return UserRecord.from_row(row)

    @staticmethod
    async def update(
        conn: asyncpg.Connection,
        user_id: int,
        value: dict[str, Any],
    ) -> UserRecord | None:
        row = await conn.fetchrow(
            """
            UPDATE users
            SET value = value || $1::JSONB
            WHERE id = $2
            RETURNING *
            """,
            json.dumps(value),
            user_id,
        )
        return UserRecord.from_row(row) if row else None

    @staticmethod
    async def delete(conn: asyncpg.Connection, user_id: int) -> bool:
        result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)
        return result == "DELETE 1"

    @staticmethod
    async def get_screens(conn: asyncpg.Connection, user_id: int) -> list[dict]:
        """Kullanıcının rolüne göre erişebileceği ekranları PostgreSQL fonksiyonundan alır."""
        result = await conn.fetchval(
            "SELECT fn_get_user_screens($1)", user_id
        )
        if result is None:
            return []
        return json.loads(result) if isinstance(result, str) else result
