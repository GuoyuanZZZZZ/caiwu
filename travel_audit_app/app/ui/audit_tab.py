"""自动审核页面。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..services import AuditService


class AuditTab(QWidget):
    """执行审核并展示摘要。"""

    audit_completed = Signal()

    def __init__(self, audit_service: AuditService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.audit_service = audit_service

        self.run_btn = QPushButton("执行审核")
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)

        self.run_btn.clicked.connect(self.run_audit)

        layout = QVBoxLayout(self)
        layout.addWidget(self.run_btn)
        layout.addWidget(QLabel("审核摘要"))
        layout.addWidget(self.summary_text)

    def run_audit(self) -> None:
        try:
            summary = self.audit_service.run_audit()
            text = (
                f"总记录数: {summary['total']}\n"
                f"通过: {summary['pass']}\n"
                f"失败: {summary['fail']}\n"
                f"人工复核: {summary['manual_review']}"
            )
            self.summary_text.setText(text)
            QMessageBox.information(self, "审核完成", "自动审核执行完成。")
            self.audit_completed.emit()
        except Exception as exc:
            QMessageBox.critical(self, "审核失败", str(exc))
