# 差旅费制度审核平台（MVP）

这是一个基于 **Python + PySide6 + SQLite** 的桌面应用，用于导入公司差旅制度和报销明细，并执行自动审核。

## 1. 功能清单（MVP）

- 制度管理
  - 导入结构化规则（Excel/CSV）
  - 规则写入 SQLite
  - 列表查看规则
  - 一键清空规则
- 报销导入
  - 导入报销明细（Excel/CSV）
  - 报销写入 SQLite
  - 列表查看报销
- 自动审核
  - 事前审批校验
  - 金额上限校验
  - 交通等级校验
  - 特批逻辑（FAIL -> MANUAL_REVIEW）
  - 缺失规则逻辑
  - 疑似重复报销识别
- 审核结果
  - 按状态筛选（ALL/PASS/FAIL/MANUAL_REVIEW）
  - 查看详细审核说明
  - 导出 Excel/CSV

## 2. 运行环境

- Python 3.11+
- 操作系统：Windows/macOS/Linux（支持 Qt）

## 3. 安装与运行

```bash
cd travel_audit_app
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

首次启动会自动创建数据库文件：`travel_audit.db`。

## 4. 示例数据

- 制度文件：`data/sample_rules.csv`
- 报销文件：`data/sample_claims.csv`

建议操作顺序：
1. 在“制度管理”导入 `sample_rules.csv`
2. 在“报销导入”导入 `sample_claims.csv`
3. 切换到“自动审核”点击“执行审核”
4. 到“审核结果”页查看结果并导出

## 5. 项目结构

```text
travel_audit_app/
  main.py
  requirements.txt
  README.md
  data/
    sample_rules.csv
    sample_claims.csv
  app/
    __init__.py
    config.py
    database.py
    models.py
    repositories.py
    rule_engine.py
    services.py
    utils.py
    ui/
      main_window.py
      rules_tab.py
      claims_tab.py
      audit_tab.py
      results_tab.py
```

## 6. 审核匹配策略说明

规则匹配优先级已在 `rule_engine.py` 中实现：
1. `employee_level + expense_type + city_level + transport_class`
2. `employee_level + expense_type + city_level`
3. `employee_level + expense_type`
4. `expense_type` 默认规则

## 7. 已知限制 / TODO

- TODO: 目前仅支持单公司规则库，不区分版本管理
- TODO: 附件字段仅保留入口，不做 OCR/PDF 识别
- TODO: 缺少更复杂反舞弊（如跨月分拆报销）


## 8. 快速演示案例

已提供一份可直接复现的端到端案例说明：

- `docs/case_demo.md`

建议先按该文档执行，可快速看到 PASS / FAIL / MANUAL_REVIEW 的完整流程。

## 9. 打包成免安装版本（给其他电脑直接用）

如果你希望“别的电脑不用安装 Python 环境就能直接运行”，推荐使用 **PyInstaller** 打包。

### 9.1 在你的打包机器上执行

```bash
cd travel_audit_app
pip install pyinstaller
pyinstaller --noconfirm --windowed --name TravelAuditApp \
  --add-data "data:./data" \
  main.py
```

打包完成后，产物位于：

- `dist/TravelAuditApp/TravelAuditApp`（macOS/Linux）
- `dist/TravelAuditApp/TravelAuditApp.exe`（Windows）

### 9.2 分发给其他电脑

把整个 `dist/TravelAuditApp` 文件夹拷贝到目标电脑即可运行。

- 目标电脑**不需要安装 Python**
- 首次运行会在程序同级目录自动创建：
  - `travel_audit.db`
  - `data/sample_rules.csv`
  - `data/sample_claims.csv`

### 9.3 注意事项

- 建议在与目标系统相同的平台打包（Windows 给 Windows，macOS 给 macOS）。
- 如需“单文件 EXE”，可尝试 `--onefile`，但首次启动会稍慢。


## 10. 常见问题（中文乱码）

如果你用 Excel 直接双击打开 CSV 出现中文乱码，通常是编码识别问题。

本项目已做两件事：

- 示例 CSV 使用 `UTF-8 with BOM`（`utf-8-sig`）保存，Excel 兼容性更好。
- 程序导入 CSV 时会自动尝试 `utf-8-sig / utf-8 / gbk / gb18030` 编码。

另外，审核结果导出为 CSV 时也使用 `utf-8-sig`，避免再次乱码。

如果你公司统一用 Excel，建议优先使用 `.xlsx` 文件进行数据交换。
