"""数据模型定义。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Rule:
    rule_id: str
    rule_name: str
    expense_type: str
    employee_level: str | None
    city_level: str | None
    transport_class: str | None
    max_amount: float | None
    requires_preapproval: bool
    exception_allowed: bool
    rule_text: str | None


@dataclass(slots=True)
class Claim:
    claim_id: str
    employee_id: str
    employee_name: str | None
    employee_level: str | None
    department: str | None
    trip_date: str | None
    start_city: str | None
    destination_city: str | None
    city_level: str | None
    expense_type: str | None
    amount: float | None
    transport_class: str | None
    invoice_no: str | None
    vendor: str | None
    has_preapproval: bool
    special_approval: bool
    note: str | None


@dataclass(slots=True)
class AuditResult:
    claim_id: str
    audit_status: str
    risk_level: str
    violation_type: str
    message: str
    matched_rule_id: str | None
    matched_rule_text: str | None
