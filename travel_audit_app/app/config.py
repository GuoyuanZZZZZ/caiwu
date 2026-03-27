"""应用配置。"""

from __future__ import annotations

import sys
from pathlib import Path

# 开发模式：以项目目录为基准
SOURCE_BASE_DIR = Path(__file__).resolve().parents[1]

# 打包模式：以可执行文件所在目录为运行根目录
if getattr(sys, "frozen", False):
    APP_HOME = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", APP_HOME))
else:
    APP_HOME = SOURCE_BASE_DIR
    BUNDLE_DIR = SOURCE_BASE_DIR

DATA_DIR = APP_HOME / "data"
BUNDLED_DATA_DIR = BUNDLE_DIR / "data"
DB_PATH = APP_HOME / "travel_audit.db"

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
