"""应用入口。"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.bootstrap import ensure_runtime_assets
from app.ui.main_window import MainWindow


def main() -> int:
    """启动 Qt 应用。"""
    ensure_runtime_assets()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
