"""回测脚本：仅拉取历史 K 线，回测逻辑与输出由 monitor_signals 统一处理。"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from futu import OpenQuoteContext, RET_OK

# 使 scripts 目录在路径中，以便导入 monitor_signals
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from monitor_signals import run_backtest_print


def main():
    parser = argparse.ArgumentParser(description="港股期权策略回测（数据在此拉取，输出由 monitor_signals 打印）")
    parser.add_argument("--symbol", default="HK.00981", help="正股代码，如 HK.00981")
    parser.add_argument("--date", default=None, help="回测日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--ktype", default="K_1M", help="K线类型，如 K_1M / K_5M / K_15M")
    parser.add_argument("--strategy", default="both", choices=["trend", "mean", "both"])
    parser.add_argument("--min_bars", type=int, default=60, help="最少K线数量后开始评估")
    args = parser.parse_args()

    symbol = args.symbol
    date = args.date or datetime.now().strftime("%Y-%m-%d")

    quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
    try:
        ret, data, _ = quote_ctx.request_history_kline(
            symbol, start=date, end=date, ktype=args.ktype
        )
        if ret != RET_OK or data is None or data.empty:
            print("获取失败:", data)
            return
        run_backtest_print(
            data, symbol=symbol, date=date, ktype=args.ktype,
            strategy=args.strategy, min_bars=args.min_bars,
        )
    finally:
        quote_ctx.close()


if __name__ == "__main__":
    main()
