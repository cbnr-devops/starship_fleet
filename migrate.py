#!/usr/bin/env python3
"""Load starships from starships.json into PostgreSQL."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import TypedDict, cast

import psycopg


class _PostgresConnKwargs(TypedDict):
    host: str
    port: int
    dbname: str
    user: str
    password: str

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS starships (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    image TEXT,
    speed TEXT,
    "range" TEXT
);
"""

UPSERT_SQL = """
INSERT INTO starships (id, name, description, image, speed, "range")
VALUES (%(id)s, %(name)s, %(description)s, %(image)s, %(speed)s, %(range)s)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    image = EXCLUDED.image,
    speed = EXCLUDED.speed,
    "range" = EXCLUDED."range";
"""


def _connection_info() -> str | _PostgresConnKwargs:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url

    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD", "")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    dbname = os.environ.get("POSTGRES_DB", "starship_fleet")

    if not user:
        print(
            "Missing database config: set DATABASE_URL or POSTGRES_USER (and optionally "
            "POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB).",
            file=sys.stderr,
        )
        sys.exit(1)

    return _PostgresConnKwargs(
        host=host,
        port=int(port),
        dbname=dbname,
        user=user,
        password=password,
    )


def load_starships(json_path: Path) -> list[dict]:
    rows = json.loads(json_path.read_text())
    if not isinstance(rows, list):
        raise ValueError("starships.json must be a JSON array")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each starship must be a JSON object")
        for key in ("id", "name", "description", "image", "speed", "range"):
            if key not in row:
                raise ValueError(f"missing required field {key!r} in starship {row!r}")
    return rows


def migrate(json_path: Path) -> int:
    rows = load_starships(json_path)
    info = _connection_info()

    if isinstance(info, str):
        conn_cm = psycopg.connect(info)
    else:
        cfg = cast(_PostgresConnKwargs, info)
        conn_cm = psycopg.connect(
            host=cfg["host"],
            port=cfg["port"],
            dbname=cfg["dbname"],
            user=cfg["user"],
            password=cfg["password"],
        )

    with conn_cm as conn:
        conn.execute(CREATE_TABLE_SQL)
        with conn.cursor() as cur:
            for row in rows:
                cur.execute(
                    UPSERT_SQL,
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "description": row["description"],
                        "image": row["image"],
                        "speed": row["speed"],
                        "range": row["range"],
                    },
                )
        conn.commit()

    return len(rows)


def main() -> None:
    default_json = Path(__file__).resolve().parent / "starships.json"
    path = Path(os.environ.get("STARSHIPS_JSON_PATH", default_json))
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    count = migrate(path)
    print(f"Migrated {count} starship(s) into PostgreSQL.")


if __name__ == "__main__":
    main()