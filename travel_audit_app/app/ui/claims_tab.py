"""报销导入页面。"""

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

from ..services import ClaimService


class ClaimsTab(QWidget):
    """报销数据导入与展示。"""

    def __init__(self, claim_service: ClaimService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.claim_service = claim_service

        self.import_btn = QPushButton("导入报销文件")
        self.table = QTableWidget()

        self.import_btn.clicked.connect(self.import_claims)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.import_btn)
        btn_layout.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.refresh_table()

    def import_claims(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择报销文件",
            "",
            "Excel/CSV Files (*.xlsx *.xls *.csv)",
        )
        if not file_path:
            return
        try:
            count = self.claim_service.import_claims(file_path)
            self.refresh_table()
            QMessageBox.information(self, "导入成功", f"成功导入 {count} 条报销记录。")
        except Exception as exc:
            QMessageBox.critical(self, "导入失败", str(exc))

    def refresh_table(self) -> None:
        rows = self.claim_service.list_claims()
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
