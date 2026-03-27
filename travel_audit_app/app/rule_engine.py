"""规则引擎模块。"""

from __future__ import annotations

from collections import defaultdict

from .models import AuditResult, Claim, Rule


class RuleEngine:
    """根据制度规则审核报销单。"""

    def __init__(self, rules: list[Rule], claims: list[Claim]) -> None:
        self.rules = rules
        self.claims = claims
        self.duplicate_keys = self._build_duplicate_map(claims)

    @staticmethod
    def _build_duplicate_map(claims: list[Claim]) -> dict[tuple, list[str]]:
        grouped: dict[tuple, list[str]] = defaultdict(list)
        for c in claims:
            key = (c.employee_id, c.trip_date, c.expense_type, c.amount, c.invoice_no)
            grouped[key].append(c.claim_id)
        return grouped

    def _find_best_rule(self, claim: Claim) -> Rule | None:
        """按优先级匹配规则：
        1) employee_level + expense_type + city_level + transport_class
        2) employee_level + expense_type + city_level
        3) employee_level + expense_type
        4) expense_type 默认规则
        """

        def same(left: str | None, right: str | None) -> bool:
            return (left or "").strip().lower() == (right or "").strip().lower()

        def empty(value: str | None) -> bool:
            return value is None or str(value).strip() == ""

        candidates = [r for r in self.rules if same(r.expense_type, claim.expense_type)]
        if not candidates:
            return None

        for r in candidates:
            if (
                same(r.employee_level, claim.employee_level)
                and same(r.city_level, claim.city_level)
                and same(r.transport_class, claim.transport_class)
                and not empty(r.transport_class)
            ):
                return r

        for r in candidates:
            if (
                same(r.employee_level, claim.employee_level)
                and same(r.city_level, claim.city_level)
                and empty(r.transport_class)
            ):
                return r

        for r in candidates:
            if same(r.employee_level, claim.employee_level) and empty(r.city_level):
                return r

        for r in candidates:
            if empty(r.employee_level):
                return r

        return None

    def run(self) -> list[AuditResult]:
        """执行审核并返回审核结果。"""
        results: list[AuditResult] = []

        for claim in self.claims:
            violations: list[str] = []
            messages: list[str] = []
            risk_level = "LOW"
            status = "PASS"
            rule = self._find_best_rule(claim)

            dup_key = (claim.employee_id, claim.trip_date, claim.expense_type, claim.amount, claim.invoice_no)
            dup_claims = self.duplicate_keys.get(dup_key, [])
            if len(dup_claims) > 1 and len(set(dup_claims)) > 1:
                status = "MANUAL_REVIEW"
                risk_level = "HIGH"
                violations.append("DUPLICATE_SUSPECT")
                messages.append("疑似重复报销")

            if rule is None:
                if status != "MANUAL_REVIEW":
                    status = "MANUAL_REVIEW"
                    risk_level = "MEDIUM"
                violations.append("RULE_NOT_FOUND")
                messages.append("未找到适配制度规则")
                results.append(
                    AuditResult(
                        claim_id=claim.claim_id,
                        audit_status=status,
                        risk_level=risk_level,
                        violation_type=";".join(violations) if violations else "NONE",
                        message="；".join(messages) if messages else "审核通过",
                        matched_rule_id=None,
                        matched_rule_text=None,
                    )
                )
                continue

            if rule.requires_preapproval and not claim.has_preapproval and not claim.special_approval:
                status = "FAIL"
                risk_level = "HIGH"
                violations.append("MISSING_PREAPPROVAL")
                messages.append("该费用类型需事前审批，但当前记录无审批")

            if rule.max_amount is not None and claim.amount is not None:
                if claim.amount > rule.max_amount and not claim.special_approval:
                    status = "FAIL"
                    risk_level = "HIGH"
                    violations.append("AMOUNT_EXCEED_LIMIT")
                    messages.append(f"报销金额 {claim.amount:.2f} 超过上限 {rule.max_amount:.2f}")

            if (claim.expense_type or "").lower() in {"train", "flight"} and rule.transport_class:
                if (claim.transport_class or "").strip().lower() != rule.transport_class.strip().lower() and not claim.special_approval:
                    status = "FAIL"
                    risk_level = "MEDIUM"
                    violations.append("TRANSPORT_CLASS_MISMATCH")
                    messages.append("交通席别/舱位不符合制度要求")

            if claim.special_approval and status == "FAIL":
                status = "MANUAL_REVIEW"
                risk_level = "MEDIUM"
                violations.append("SPECIAL_APPROVAL")
                messages.append("存在特批，需人工复核")

            if not messages:
                messages.append("审核通过")

            results.append(
                AuditResult(
                    claim_id=claim.claim_id,
                    audit_status=status,
                    risk_level=risk_level,
                    violation_type=";".join(violations) if violations else "NONE",
                    message="；".join(messages),
                    matched_rule_id=rule.rule_id,
                    matched_rule_text=rule.rule_text,
                )
            )

        return results
