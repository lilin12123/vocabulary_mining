import argparse
import re
import time
from datetime import datetime, timedelta

import pandas as pd
from futu import OpenQuoteContext, RET_OK


def ktype_to_interval_seconds(ktype: str) -> int:
    """从 K 线类型解析轮询间隔秒数，与 ktype 保持一致。如 K_1M -> 60, K_5M -> 300."""
    m = re.match(r"K_(\d+)(M|m|D|d|W|w)", ktype, re.IGNORECASE)
    if not m:
        return 60
    num, unit = int(m.group(1)), m.group(2).upper()
    if unit == "M":
        return num * 60
    if unit == "D":
        return num * 86400
    if unit == "W":
        return num * 86400 * 7
    return num * 60


def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)


def calc_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist


def calc_vwap(df: pd.DataFrame) -> pd.Series:
    turnover = df["turnover"].fillna(0)
    volume = df["volume"].replace(0, pd.NA)
    vwap = turnover.cumsum() / volume.cumsum()
    return vwap.ffill().fillna(0)


def is_bullish_reversal(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    last = df.iloc[-1]
    return (prev["close"] < prev["open"]) and (last["close"] > last["open"]) and (last["close"] > prev["close"])


def is_bearish_reversal(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    last = df.iloc[-1]
    return (prev["close"] > prev["open"]) and (last["close"] < last["open"]) and (last["close"] < prev["close"])


def detect_divergence(df: pd.DataFrame, hist: pd.Series, window: int = 20):
    if len(df) < window + 2:
        return False, False
    recent = df.iloc[-(window + 1):]
    hist_recent = hist.iloc[-(window + 1):]
    last_close = recent["close"].iloc[-1]
    last_hist = hist_recent.iloc[-1]
    prev_low = recent["close"].iloc[:-1].min()
    prev_high = recent["close"].iloc[:-1].max()
    prev_hist_low = hist_recent.iloc[:-1].min()
    prev_hist_high = hist_recent.iloc[:-1].max()
    bullish = (last_close <= prev_low) and (last_hist > prev_hist_low)
    bearish = (last_close >= prev_high) and (last_hist < prev_hist_high)
    return bullish, bearish


def build_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = calc_rsi(df["close"])
    macd, signal, hist = calc_macd(df["close"])
    df["macd"] = macd
    df["macd_signal"] = signal
    df["macd_hist"] = hist
    df["vwap"] = calc_vwap(df)
    df["ma20"] = df["close"].rolling(20, min_periods=1).mean()
    return df


def get_indicator_summary(df: pd.DataFrame) -> dict:
    """从带指标的 df 取最后一根 K 线的股价与指标区域摘要。"""
    last = df.iloc[-1]
    rsi = float(last["rsi"])
    price = float(last["close"])
    open_ = float(last["open"])
    high = float(last["high"])
    low = float(last["low"])
    vwap = float(last["vwap"])
    macd = float(last["macd"])
    macd_signal = float(last["macd_signal"])
    macd_hist = float(last["macd_hist"])
    time_key = last.get("time_key", "")
    if hasattr(time_key, "strftime"):
        time_key = time_key.strftime("%Y-%m-%d %H:%M:%S")
    # RSI 区域
    if rsi < 30:
        rsi_zone = "超卖"
    elif rsi < 50:
        rsi_zone = "弱势"
    elif rsi <= 65:
        rsi_zone = "强势" if rsi >= 50 else "中性"
    elif rsi <= 70:
        rsi_zone = "偏强"
    else:
        rsi_zone = "超买"
    # 价格 vs VWAP
    if price > vwap * 1.002:
        vwap_relation = "站上VWAP"
    elif price < vwap * 0.998:
        vwap_relation = "跌破VWAP"
    else:
        vwap_relation = "贴近VWAP"
    vwap_pct = (price - vwap) / vwap * 100 if vwap else 0.0
    # MACD 区域
    if macd > macd_signal:
        macd_zone = "水上金叉" if macd > 0 else "水下金叉"
    else:
        macd_zone = "水上死叉" if macd > 0 else "水下死叉"
    return {
        "price": price,
        "open": open_,
        "high": high,
        "low": low,
        "rsi": rsi,
        "rsi_zone": rsi_zone,
        "vwap": vwap,
        "vwap_relation": vwap_relation,
        "vwap_pct": vwap_pct,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_hist": macd_hist,
        "macd_zone": macd_zone,
        "time_key": time_key,
    }


def format_poll_line(summary: dict, symbol: str) -> str:
    """单次轮询的丰富信息一行。"""
    return (
        f"[{summary['time_key']}] {symbol} "
        f"价={summary['price']:.2f} RSI={summary['rsi']:.1f}({summary['rsi_zone']}) "
        f"{summary['vwap_relation']} MACD{summary['macd_zone']}"
    )


def format_signal_banner(
    sig_type: str, message: str, summary: dict, symbol: str, name: str = "", strategy_label: str = ""
) -> str:
    """触发信号时的醒目图案 + 股票代码/名称第一行 + 日期 + RSI/VWAP/MACD 各一行。"""
    title = f">>> 买入 {sig_type} 信号 <<<" + (f"  [{strategy_label}]" if strategy_label else "")
    width = max(44, len(title) + 4)
    line = "!" * width
    mid = "!" + title.center(width - 2) + "!"
    s = summary
    # 第一行：股票代码和名称
    symbol_line = f"  股票: {symbol}" + (f"  {name}" if name else "")
    # 日期
    date_line = f"  日期: {s['time_key']}"
    # RSI 一行
    rsi_line = (
        f"  RSI:  {s['rsi']:.1f} ({s['rsi_zone']})  "
        f"[0-30 超卖 | 30-50 弱势 | 50-65 强势 | 65-70 偏强 | 70+ 超买]"
    )
    # VWAP 一行
    vwap_line = (
        f"  VWAP: {s['vwap']:.2f}  当前价 {s['price']:.2f}  "
        f"{s['vwap_relation']}，偏离 {s['vwap_pct']:+.2f}%"
    )
    # MACD 一行
    macd_line = (
        f"  MACD: 线 {s['macd']:.4f}  信号 {s['macd_signal']:.4f}  柱 {s['macd_hist']:.4f}  "
        f"({s['macd_zone']})"
    )
    msg_line = f"  {symbol}  {message}"
    return (
        f"\n{line}\n{mid}\n{line}\n"
        f"{symbol_line}\n"
        f"{date_line}\n"
        f"{rsi_line}\n"
        f"{vwap_line}\n"
        f"{macd_line}\n"
        f"{msg_line}\n"
        f"{line}\n"
    )


def eval_trend_following(df: pd.DataFrame):
    last = df.iloc[-1]
    signals = []
    rsi = last["rsi"]
    macd = last["macd"]
    macd_signal = last["macd_signal"]
    hist = df["macd_hist"].iloc[-3:]
    price = last["close"]
    vwap = last["vwap"]
    if price > vwap and 50 <= rsi <= 65 and macd > macd_signal and macd > 0 and hist.is_monotonic_increasing:
        signals.append(("CALL", "顺势-买入Call：站上VWAP，RSI强势区，MACD水上金叉且红柱放大"))
    if price < vwap and 35 <= rsi <= 50 and macd < macd_signal and macd < 0 and hist.is_monotonic_decreasing:
        signals.append(("PUT", "顺势-买入Put：压制在VWAP下方，RSI弱势区，MACD水下死叉且绿柱放大"))
    return signals


def eval_mean_reversion(df: pd.DataFrame):
    last = df.iloc[-1]
    signals = []
    rsi = last["rsi"]
    price = last["close"]
    vwap = last["vwap"]
    bullish_div, bearish_div = detect_divergence(df, df["macd_hist"])
    if rsi < 30 and bullish_div and price < vwap and is_bullish_reversal(df):
        signals.append(("CALL", "逆势-买入Call：RSI超卖+MACD背离+远离VWAP+反转K线"))
    if rsi > 70 and bearish_div and price > vwap and is_bearish_reversal(df):
        signals.append(("PUT", "逆势-买入Put：RSI超买+MACD背离+远离VWAP+反转K线"))
    return signals


def get_kline(quote_ctx: OpenQuoteContext, symbol: str, ktype: str, count: int):
    ret, data = quote_ctx.get_cur_kline(symbol, num=count, ktype=ktype)
    if ret != RET_OK:
        raise RuntimeError(data)
    return data


def run_backtest_print(
    data: pd.DataFrame,
    symbol: str,
    date: str,
    ktype: str,
    strategy: str,
    min_bars: int,
) -> None:
    """对已拉取的历史 K 线做回测并统一在此处打印（股价、指标区域、醒目信号框）。"""
    data = data.sort_values("time_key").reset_index(drop=True)
    signals = []
    for i in range(min_bars, len(data)):
        window = data.iloc[: i + 1].copy()
        ind = build_indicators(window)
        sigs = []
        if strategy in ("trend", "both"):
            for sig_type, message in eval_trend_following(ind):
                summary = get_indicator_summary(ind)
                signals.append((sig_type, message, summary, "顺势"))
        if strategy in ("mean", "both"):
            for sig_type, message in eval_mean_reversion(ind):
                summary = get_indicator_summary(ind)
                signals.append((sig_type, message, summary, "逆势"))

    print(f"回测日期: {date}  标的: {symbol}  K线: {ktype}")
    print(f"总信号数: {len(signals)}")
    for sig_type, msg, summary, strategy_label in signals:
        print(format_signal_banner(sig_type, msg, summary, symbol, strategy_label=strategy_label))


def main():
    parser = argparse.ArgumentParser(description="港股期权策略行情监测（仅提示信号）")
    parser.add_argument("--symbol", default="HK.00981", help="正股代码，如 HK.00981")
    parser.add_argument("--ktype", default="K_5M", help="K线类型，如 K_1M / K_5M / K_15M（轮询间隔与之一致）")
    parser.add_argument("--strategy", default="both", choices=["trend", "mean", "both"])
    parser.add_argument("--count", type=int, default=200, help="拉取K线数量")
    parser.add_argument("--cooldown", type=int, default=120, help="同类信号冷却秒数")
    args = parser.parse_args()

    interval_sec = ktype_to_interval_seconds(args.ktype)
    quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
    last_emit = {}

    try:
        print("启动行情监测:", args.symbol, args.ktype, args.strategy, f"轮询间隔={interval_sec}秒")
        while True:
            df = get_kline(quote_ctx, args.symbol, args.ktype, args.count)
            df = df.sort_values("time_key")
            df = build_indicators(df)
            summary = get_indicator_summary(df)

            # 每次轮询打印丰富信息
            print(format_poll_line(summary, args.symbol))

            signals = []
            if args.strategy in ("trend", "both"):
                for sig_type, message in eval_trend_following(df):
                    signals.append((sig_type, message, "顺势"))
            if args.strategy in ("mean", "both"):
                for sig_type, message in eval_mean_reversion(df):
                    signals.append((sig_type, message, "逆势"))

            now = datetime.now()
            for sig_type, message, strategy_label in signals:
                key = f"{args.strategy}:{sig_type}"
                last_time = last_emit.get(key)
                if last_time is None or now - last_time > timedelta(seconds=args.cooldown):
                    last_emit[key] = now
                    print(format_signal_banner(sig_type, message, summary, args.symbol, strategy_label=strategy_label))

            time.sleep(interval_sec)
    finally:
        quote_ctx.close()


if __name__ == "__main__":
    main()
