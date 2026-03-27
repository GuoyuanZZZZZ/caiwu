"""数据访问层，负责 CRUD。"""

from __future__ import annotations

from typing import Iterable

from .database import DatabaseManager
from .models import AuditResult, Claim, Rule


class RuleRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def clear_all(self) -> None:
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM rules")

    def bulk_insert(self, rules: Iterable[Rule]) -> None:
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO rules (
                    rule_id, rule_name, expense_type, employee_level, city_level,
                    transport_class, max_amount, requires_preapproval, exception_allowed, rule_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.rule_id,
                        r.rule_name,
                        r.expense_type,
                        r.employee_level,
                        r.city_level,
                        r.transport_class,
                        r.max_amount,
                        1 if r.requires_preapproval else 0,
                        1 if r.exception_allowed else 0,
                        r.rule_text,
                    )
                    for r in rules
                ],
            )

    def list_all(self) -> list[dict]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT rule_id, rule_name, expense_type, employee_level, city_level,
                       transport_class, max_amount, requires_preapproval,
                       exception_allowed, rule_text
                FROM rules ORDER BY expense_type, employee_level
                """
            ).fetchall()
        return [dict(row) for row in rows]


class ClaimRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def clear_all(self) -> None:
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM claims")

    def bulk_insert(self, claims: Iterable[Claim]) -> None:
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO claims (
                    claim_id, employee_id, employee_name, employee_level, department,
                    trip_date, start_city, destination_city, city_level, expense_type,
                    amount, transport_class, invoice_no, vendor, has_preapproval,
                    special_approval, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.claim_id,
                        c.employee_id,
                        c.employee_name,
                        c.employee_level,
                        c.department,
                        c.trip_date,
                        c.start_city,
                        c.destination_city,
                        c.city_level,
                        c.expense_type,
                        c.amount,
                        c.transport_class,
                        c.invoice_no,
                        c.vendor,
                        1 if c.has_preapproval else 0,
                        1 if c.special_approval else 0,
                        c.note,
                    )
                    for c in claims
                ],
            )

    def list_all(self) -> list[dict]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT claim_id, employee_id, employee_name, employee_level, department,
                       trip_date, start_city, destination_city, city_level, expense_type,
                       amount, transport_class, invoice_no, vendor, has_preapproval,
                       special_approval, note
                FROM claims ORDER BY trip_date, claim_id
                """
            ).fetchall()
        return [dict(row) for row in rows]


class AuditResultRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def clear_all(self) -> None:
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM audit_results")

    def bulk_insert(self, results: Iterable[AuditResult]) -> None:
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO audit_results (
                    claim_id, audit_status, risk_level, violation_type,
                    message, matched_rule_id, matched_rule_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.claim_id,
                        r.audit_status,
                        r.risk_level,
                        r.violation_type,
                        r.message,
                        r.matched_rule_id,
                        r.matched_rule_text,
                    )
                    for r in results
                ],
            )

    def list_with_claims(self, status: str | None = None) -> list[dict]:
        where_clause = ""
        params: tuple = ()
        if status and status != "ALL":
            where_clause = "WHERE ar.audit_status = ?"
            params = (status,)

        with self.db.get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT c.claim_id, c.employee_id, c.employee_name, c.employee_level,
                       c.department, c.trip_date, c.start_city, c.destination_city,
                       c.city_level, c.expense_type, c.amount, c.transport_class,
                       c.invoice_no, c.vendor, c.has_preapproval, c.special_approval,
                       c.note,
                       ar.audit_status, ar.risk_level, ar.violation_type,
                       ar.message, ar.matched_rule_id, ar.matched_rule_text
                FROM claims c
                LEFT JOIN audit_results ar ON c.claim_id = ar.claim_id
                {where_clause}
                ORDER BY c.trip_date, c.claim_id
                """,
                params,
            ).fetchall()
        return [dict(row) for row in rows]
