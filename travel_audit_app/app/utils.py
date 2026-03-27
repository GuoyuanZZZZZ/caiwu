"""通用工具函数。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_dataframe(file_path: str | Path) -> pd.DataFrame:
    """根据文件扩展名读取 CSV/Excel。"""
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV / Excel 文件")


def normalize_bool(value: object) -> bool:
    """将多种形式的真假值统一为 bool。"""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "是", "有"}


def clean_text(value: object) -> str | None:
    """清洗字符串，空值返回 None。"""
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    return text


def to_float(value: object) -> float | None:
    """安全转换浮点数。"""
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    return float(text)
