"""应用配置。"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "travel_audit.db"

RULE_COLUMNS = [
    "rule_id",
    "rule_name",
    "expense_type",
    "employee_level",
    "city_level",
    "transport_class",
    "max_amount",
    "requires_preapproval",
    "exception_allowed",
    "rule_text",
]

CLAIM_COLUMNS = [
    "claim_id",
    "employee_id",
    "employee_name",
    "employee_level",
    "department",
    "trip_date",
    "start_city",
    "destination_city",
    "city_level",
    "expense_type",
    "amount",
    "transport_class",
    "invoice_no",
    "vendor",
    "has_preapproval",
    "special_approval",
    "note",
]

AUDIT_COLUMNS = [
    "claim_id",
    "audit_status",
    "risk_level",
    "violation_type",
    "message",
    "matched_rule_id",
    "matched_rule_text",
]
