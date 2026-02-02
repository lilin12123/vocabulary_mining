# Futu 港股期权策略脚本

基于富途 OpenD 行情，对港股正股做**顺势**与**逆势**两套期权策略的监测与回测，满足条件时提示买入 Call 或 Put。

## 前置条件

- 已安装 [富途 OpenD](https://openapi.futunn.com/download/OpenD) 并保持运行（默认 `127.0.0.1:11111`）
- Python 虚拟环境已创建并安装依赖，例如在项目根目录：
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate   # Windows: .venv\Scripts\activate
  pip install futu-api pandas
  ```

运行脚本时需在**项目根目录**下、且已激活 `.venv`，以便正确导入 `monitor_signals`：

```bash
cd /path/to/vocabulary_mining
source .venv/bin/activate
python Futu/scripts/test/backtest_signals.py --date 2026-02-02
python Futu/scripts/monitor_signals.py --ktype K_5M
```

---

## 目录结构

```
Futu/
├── scripts/
│   ├── monitor_signals.py   # 实时监测（策略逻辑与输出统一在此）
│   └── test/
│       ├── backtest_signals.py   # 历史回测（拉数据后调用 monitor_signals）
│       └── test_get.py           # 富途 API 连接测试
└── stragedies/
    ├── trend_following.txt
    └── mean_reversion.txt
```

---

## 脚本说明

### 1. `scripts/monitor_signals.py` — 实时监测

**作用**：按设定间隔拉取最新 K 线，计算 RSI、VWAP、MACD 等指标，当满足顺势或逆势策略的买入 Call/Put 条件时，在终端打印醒目信号（含股票、日期、RSI/VWAP/MACD 等详细信息）。

**轮询间隔**：与 `--ktype` 一致（如 `K_1M` 每 1 分钟、`K_5M` 每 5 分钟）。

**常用参数**：

| 参数 | 默认 | 说明 |
|------|------|------|
| `--symbol` | HK.00981 | 正股代码 |
| `--ktype` | K_5M | K 线类型：K_1M / K_5M / K_15M 等 |
| `--strategy` | both | 策略：trend（顺势）/ mean（逆势）/ both |
| `--cooldown` | 120 | 同类信号冷却秒数 |

**示例**：

```bash
# 1 分钟 K 线，每 1 分钟轮询，双策略
python Futu/scripts/monitor_signals.py --ktype K_1M

# 5 分钟 K 线，仅顺势策略
python Futu/scripts/monitor_signals.py --ktype K_5M --strategy trend
```

---

### 2. `scripts/test/backtest_signals.py` — 历史回测

**作用**：从富途拉取**指定日期**的历史 K 线，按同样策略规则逐根 K 线评估，得到当日所有触发点；**不负责具体计算与输出格式**，只负责拉数据并调用 `monitor_signals` 里的回测与打印逻辑，因此信号样式与实时监测一致（股票、日期、RSI/VWAP/MACD 各一行 + 醒目框）。

**如何指定日期**：使用 `--date YYYY-MM-DD`。不传则默认为**当天**。

**常用参数**：

| 参数 | 默认 | 说明 |
|------|------|------|
| `--symbol` | HK.00981 | 正股代码 |
| `--date` | 当天 | 回测日期，格式 `YYYY-MM-DD` |
| `--ktype` | K_1M | K 线类型 |
| `--strategy` | both | trend / mean / both |
| `--min_bars` | 60 | 至少多少根 K 线后才开始评估 |

**示例**：

```bash
# 回测 2026-02-02 的 1 分钟 K 线（双策略）
python Futu/scripts/test/backtest_signals.py --date 2026-02-02

# 回测今天的 5 分钟 K 线（不写 --date 即当天）
python Futu/scripts/test/backtest_signals.py --ktype K_5M

# 回测指定日、指定标的、仅逆势
python Futu/scripts/test/backtest_signals.py --date 2026-01-15 --symbol HK.00981 --strategy mean
```

### 3. `scripts/test/test_get.py` — 富途 API 连接测试

**作用**：简单拉取 HK.00981 实时快照，用于验证 OpenD 是否连通、futu-api 是否可用。

---

## 策略简述

- **顺势 (trend)**：站上 VWAP + RSI 强势区 + MACD 水上金叉 → 考虑 Call；压制在 VWAP 下 + RSI 弱势区 + MACD 水下死叉 → 考虑 Put。
- **逆势 (mean_reversion)**：RSI 超卖 + MACD 背离 + 反转 K 线 → 考虑 Call；RSI 超买 + MACD 背离 + 反转 K 线 → 考虑 Put。

详细规则见 `stragedies/trend_following.txt` 与 `stragedies/mean_reversion.txt`。
