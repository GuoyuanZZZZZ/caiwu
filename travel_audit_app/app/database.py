"""SQLite 数据库连接与初始化。"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import DB_PATH


class DatabaseManager:
    """管理 SQLite 连接与建表。"""

    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = str(db_path)

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """获取数据库连接并自动提交/回滚。"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """初始化数据库表结构。"""
        with self.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id TEXT NOT NULL UNIQUE,
                    rule_name TEXT NOT NULL,
                    expense_type TEXT NOT NULL,
                    employee_level TEXT,
                    city_level TEXT,
                    transport_class TEXT,
                    max_amount REAL,
                    requires_preapproval INTEGER NOT NULL DEFAULT 0,
                    exception_allowed INTEGER NOT NULL DEFAULT 0,
                    rule_text TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT NOT NULL,
                    employee_id TEXT NOT NULL,
                    employee_name TEXT,
                    employee_level TEXT,
                    department TEXT,
                    trip_date TEXT,
                    start_city TEXT,
                    destination_city TEXT,
                    city_level TEXT,
                    expense_type TEXT,
                    amount REAL,
                    transport_class TEXT,
                    invoice_no TEXT,
                    vendor TEXT,
                    has_preapproval INTEGER NOT NULL DEFAULT 0,
                    special_approval INTEGER NOT NULL DEFAULT 0,
                    note TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT NOT NULL,
                    audit_status TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    violation_type TEXT,
                    message TEXT,
                    matched_rule_id TEXT,
                    matched_rule_text TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
