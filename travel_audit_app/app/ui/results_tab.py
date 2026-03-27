"""审核结果展示页面。"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..services import AuditService


class ResultsTab(QWidget):
    """查看和导出审核结果。"""

    def __init__(self, audit_service: AuditService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.audit_service = audit_service
        self.current_rows: list[dict] = []

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ALL", "PASS", "FAIL", "MANUAL_REVIEW"])
        self.refresh_btn = QPushButton("刷新")
        self.export_btn = QPushButton("导出 Excel")

        self.table = QTableWidget()
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)

        self.filter_combo.currentTextChanged.connect(self.refresh_table)
        self.refresh_btn.clicked.connect(self.refresh_table)
        self.export_btn.clicked.connect(self.export_results)
        self.table.itemSelectionChanged.connect(self.show_detail)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("状态筛选"))
        top_layout.addWidget(self.filter_combo)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.export_btn)
        top_layout.addStretch()

        splitter = QSplitter()
        splitter.addWidget(self.table)
        splitter.addWidget(self.detail_text)
        splitter.setSizes([900, 350])

        layout = QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addWidget(splitter)

        self.refresh_table()

    def refresh_table(self) -> None:
        status = self.filter_combo.currentText()
        try:
            rows = self.audit_service.list_results(status)
        except Exception as exc:
            QMessageBox.critical(self, "读取失败", str(exc))
            return

        self.current_rows = rows
        if not rows:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.detail_text.clear()
            return

        headers = list(rows[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, key in enumerate(headers):
                value = row.get(key, "")
                self.table.setItem(i, j, QTableWidgetItem("" if value is None else str(value)))
        self.table.resizeColumnsToContents()

    def show_detail(self) -> None:
        items = self.table.selectedItems()
        if not items:
            self.detail_text.clear()
            return

        row_idx = items[0].row()
        if row_idx >= len(self.current_rows):
            return
        row = self.current_rows[row_idx]
        detail = (
            f"报销单号: {row.get('claim_id')}\n"
            f"员工: {row.get('employee_name')} ({row.get('employee_id')})\n"
            f"费用类型: {row.get('expense_type')}\n"
            f"金额: {row.get('amount')}\n"
            f"审核状态: {row.get('audit_status')}\n"
            f"风险等级: {row.get('risk_level')}\n"
            f"违规类型: {row.get('violation_type')}\n"
            f"问题说明: {row.get('message')}\n"
            f"匹配规则: {row.get('matched_rule_id')}\n"
            f"条款依据: {row.get('matched_rule_text')}\n"
        )
        self.detail_text.setText(detail)

    def export_results(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出审核结果",
            "audit_results.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)",
        )
        if not file_path:
            return
        status = self.filter_combo.currentText()
        try:
            self.audit_service.export_results(file_path, status=status)
            QMessageBox.information(self, "导出成功", f"已导出到: {file_path}")
        except Exception as exc:
            QMessageBox.critical(self, "导出失败", str(exc))
