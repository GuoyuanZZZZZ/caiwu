"""制度管理页面。"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services import RuleService


class RulesTab(QWidget):
    """制度规则导入与展示。"""

    def __init__(self, rule_service: RuleService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.rule_service = rule_service

        self.import_btn = QPushButton("导入制度文件")
        self.clear_btn = QPushButton("清空制度")
        self.table = QTableWidget()

        self.import_btn.clicked.connect(self.import_rules)
        self.clear_btn.clicked.connect(self.clear_rules)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.refresh_table()

    def import_rules(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择制度文件",
            "",
            "Excel/CSV Files (*.xlsx *.xls *.csv)",
        )
        if not file_path:
            return
        try:
            count = self.rule_service.import_rules(file_path)
            self.refresh_table()
            QMessageBox.information(self, "导入成功", f"成功导入 {count} 条制度规则。")
        except Exception as exc:
            QMessageBox.critical(self, "导入失败", str(exc))

    def clear_rules(self) -> None:
        reply = QMessageBox.question(self, "确认", "确定要清空所有制度规则吗？")
        if reply != QMessageBox.Yes:
            return
        try:
            self.rule_service.repo.clear_all()
            self.refresh_table()
            QMessageBox.information(self, "完成", "制度规则已清空。")
        except Exception as exc:
            QMessageBox.critical(self, "失败", str(exc))

    def refresh_table(self) -> None:
        rows = self.rule_service.list_rules()
        if not rows:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        headers = list(rows[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, key in enumerate(headers):
                self.table.setItem(i, j, QTableWidgetItem(str(row.get(key, ""))))
        self.table.resizeColumnsToContents()
