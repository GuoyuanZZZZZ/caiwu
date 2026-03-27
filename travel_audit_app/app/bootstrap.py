"""应用启动前初始化。"""

from __future__ import annotations

import shutil
from pathlib import Path

from .config import BUNDLED_DATA_DIR, DATA_DIR


def ensure_runtime_assets() -> None:
    """确保运行目录具备 data 样例文件，便于开箱即用。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sample_files = ["sample_rules.csv", "sample_claims.csv"]
    for file_name in sample_files:
        target = DATA_DIR / file_name
        source = BUNDLED_DATA_DIR / file_name

        if target.exists():
            continue
        if source.exists():
            shutil.copy2(source, target)
