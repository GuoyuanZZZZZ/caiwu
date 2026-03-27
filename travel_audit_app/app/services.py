"""服务层：导入、审核、导出流程。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import CLAIM_COLUMNS, RULE_COLUMNS
from .models import Claim, Rule
from .repositories import AuditResultRepository, ClaimRepository, RuleRepository
from .rule_engine import RuleEngine
from .utils import clean_text, load_dataframe, normalize_bool, to_float


class RuleService:
    """制度规则服务。"""

    def __init__(self, repo: RuleRepository) -> None:
        self.repo = repo

    def import_rules(self, file_path: str | Path) -> int:
        df = load_dataframe(file_path)
        self._validate_columns(df, RULE_COLUMNS)
        rules = [
            Rule(
                rule_id=str(row["rule_id"]).strip(),
                rule_name=str(row["rule_name"]).strip(),
                expense_type=str(row["expense_type"]).strip(),
                employee_level=clean_text(row.get("employee_level")),
                city_level=clean_text(row.get("city_level")),
                transport_class=clean_text(row.get("transport_class")),
                max_amount=to_float(row.get("max_amount")),
                requires_preapproval=normalize_bool(row.get("requires_preapproval")),
                exception_allowed=normalize_bool(row.get("exception_allowed")),
                rule_text=clean_text(row.get("rule_text")),
            )
            for _, row in df.iterrows()
        ]
        self.repo.clear_all()
        self.repo.bulk_insert(rules)
        return len(rules)

    def list_rules(self) -> list[dict]:
        return self.repo.list_all()

    @staticmethod
    def _validate_columns(df: pd.DataFrame, expected: list[str]) -> None:
        missing = [c for c in expected if c not in df.columns]
        if missing:
            raise ValueError(f"规则文件缺失字段: {', '.join(missing)}")


class ClaimService:
    """报销单服务。"""

    def __init__(self, repo: ClaimRepository) -> None:
        self.repo = repo

    def import_claims(self, file_path: str | Path) -> int:
        df = load_dataframe(file_path)
        self._validate_columns(df, CLAIM_COLUMNS)
        claims = [
            Claim(
                claim_id=str(row["claim_id"]).strip(),
                employee_id=str(row["employee_id"]).strip(),
                employee_name=clean_text(row.get("employee_name")),
                employee_level=clean_text(row.get("employee_level")),
                department=clean_text(row.get("department")),
                trip_date=clean_text(row.get("trip_date")),
                start_city=clean_text(row.get("start_city")),
                destination_city=clean_text(row.get("destination_city")),
                city_level=clean_text(row.get("city_level")),
                expense_type=clean_text(row.get("expense_type")),
                amount=to_float(row.get("amount")),
                transport_class=clean_text(row.get("transport_class")),
                invoice_no=clean_text(row.get("invoice_no")),
                vendor=clean_text(row.get("vendor")),
                has_preapproval=normalize_bool(row.get("has_preapproval")),
                special_approval=normalize_bool(row.get("special_approval")),
                note=clean_text(row.get("note")),
            )
            for _, row in df.iterrows()
        ]
        self.repo.clear_all()
        self.repo.bulk_insert(claims)
        return len(claims)

    def list_claims(self) -> list[dict]:
        return self.repo.list_all()

    @staticmethod
    def _validate_columns(df: pd.DataFrame, expected: list[str]) -> None:
        missing = [c for c in expected if c not in df.columns]
        if missing:
            raise ValueError(f"报销文件缺失字段: {', '.join(missing)}")


class AuditService:
    """审核服务。"""

    def __init__(
        self,
        rule_repo: RuleRepository,
        claim_repo: ClaimRepository,
        audit_repo: AuditResultRepository,
    ) -> None:
        self.rule_repo = rule_repo
        self.claim_repo = claim_repo
        self.audit_repo = audit_repo

    def run_audit(self) -> dict:
        rules = [Rule(**self._map_rule_row(row)) for row in self.rule_repo.list_all()]
        claims = [Claim(**self._map_claim_row(row)) for row in self.claim_repo.list_all()]

        engine = RuleEngine(rules=rules, claims=claims)
        results = engine.run()

        self.audit_repo.clear_all()
        self.audit_repo.bulk_insert(results)

        summary = {
            "total": len(results),
            "pass": len([r for r in results if r.audit_status == "PASS"]),
            "fail": len([r for r in results if r.audit_status == "FAIL"]),
            "manual_review": len([r for r in results if r.audit_status == "MANUAL_REVIEW"]),
        }
        return summary

    def list_results(self, status: str | None = None) -> list[dict]:
        return self.audit_repo.list_with_claims(status)

    def export_results(self, file_path: str | Path, status: str | None = None) -> None:
        rows = self.list_results(status=status)
        if not rows:
            raise ValueError("当前没有可导出的审核结果")
        df = pd.DataFrame(rows)
        path = Path(file_path)
        if path.suffix.lower() in {".xlsx", ".xls"}:
            df.to_excel(path, index=False)
        elif path.suffix.lower() == ".csv":
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            raise ValueError("导出仅支持 .xlsx 或 .csv")

    @staticmethod
    def _map_rule_row(row: dict) -> dict:
        return {
            "rule_id": row["rule_id"],
            "rule_name": row["rule_name"],
            "expense_type": row["expense_type"],
            "employee_level": clean_text(row.get("employee_level")),
            "city_level": clean_text(row.get("city_level")),
            "transport_class": clean_text(row.get("transport_class")),
            "max_amount": to_float(row.get("max_amount")),
            "requires_preapproval": bool(row.get("requires_preapproval")),
            "exception_allowed": bool(row.get("exception_allowed")),
            "rule_text": clean_text(row.get("rule_text")),
        }

    @staticmethod
    def _map_claim_row(row: dict) -> dict:
        mapped = {
            "claim_id": row["claim_id"],
            "employee_id": row["employee_id"],
            "employee_name": clean_text(row.get("employee_name")),
            "employee_level": clean_text(row.get("employee_level")),
            "department": clean_text(row.get("department")),
            "trip_date": clean_text(row.get("trip_date")),
            "start_city": clean_text(row.get("start_city")),
            "destination_city": clean_text(row.get("destination_city")),
            "city_level": clean_text(row.get("city_level")),
            "expense_type": clean_text(row.get("expense_type")),
            "amount": to_float(row.get("amount")),
            "transport_class": clean_text(row.get("transport_class")),
            "invoice_no": clean_text(row.get("invoice_no")),
            "vendor": clean_text(row.get("vendor")),
            "has_preapproval": bool(row.get("has_preapproval")),
            "special_approval": bool(row.get("special_approval")),
            "note": clean_text(row.get("note")),
        }
        return mapped
