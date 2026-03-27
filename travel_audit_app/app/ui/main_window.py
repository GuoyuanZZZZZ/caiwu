"""主窗口。"""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from ..database import DatabaseManager
from ..repositories import AuditResultRepository, ClaimRepository, RuleRepository
from ..services import AuditService, ClaimService, RuleService
from .audit_tab import AuditTab
from .claims_tab import ClaimsTab
from .results_tab import ResultsTab
from .rules_tab import RulesTab


class MainWindow(QMainWindow):
    """差旅费制度审核平台主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("差旅费制度审核平台 MVP")
        self.resize(1400, 800)

        self.db = DatabaseManager()
        self.db.init_db()

        rule_repo = RuleRepository(self.db)
        claim_repo = ClaimRepository(self.db)
        audit_repo = AuditResultRepository(self.db)

        rule_service = RuleService(rule_repo)
        claim_service = ClaimService(claim_repo)
        audit_service = AuditService(rule_repo, claim_repo, audit_repo)

        self.rules_tab = RulesTab(rule_service)
        self.claims_tab = ClaimsTab(claim_service)
        self.audit_tab = AuditTab(audit_service)
        self.results_tab = ResultsTab(audit_service)

        self.audit_tab.audit_completed.connect(self.results_tab.refresh_table)

        tabs = QTabWidget()
        tabs.addTab(self.rules_tab, "制度管理")
        tabs.addTab(self.claims_tab, "报销导入")
        tabs.addTab(self.audit_tab, "自动审核")
        tabs.addTab(self.results_tab, "审核结果")

        self.setCentralWidget(tabs)
        self.statusBar().showMessage("就绪")
