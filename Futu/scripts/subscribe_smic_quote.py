#!/usr/bin/env python3
"""
订阅中芯国际（港股 00981）的实时行情。

使用方式：
  1. 确保 OpenD 已启动并监听 127.0.0.1:11111
  2. 运行: python subscribe_smic_quote.py
  3. 按 Ctrl+C 退出

参考: https://openapi.futunn.com/futu-api-doc/quote/sub.html
"""

import sys
import time

from futu import OpenQuoteContext, RET_OK, SubType

# 中芯国际 港股
SMIC_HK = "HK.00981"


def main():
    quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)

    try:
        # 订阅实时报价（QUOTE）；subscribe_push=False 表示仅用拉取方式取数，不注册推送回调
        ret_sub, err = quote_ctx.subscribe(
            [SMIC_HK],
            [SubType.QUOTE],
            is_first_push=True,
            subscribe_push=False,
        )
        if ret_sub != RET_OK:
            print(f"订阅失败: {err}", file=sys.stderr)
            return 1

        print(f"已订阅 {SMIC_HK} 实时报价，按 Ctrl+C 退出\n")

        while True:
            ret, df = quote_ctx.get_stock_quote([SMIC_HK])
            if ret != RET_OK:
                print(f"获取报价失败: {df}", file=sys.stderr)
            elif df is not None and not df.empty:
                row = df.iloc[0]
                name = row.get("name", "")
                data_time = row.get("data_time", "")
                last = row.get("last_price", "")
                open_p = row.get("open_price", "")
                high = row.get("high_price", "")
                low = row.get("low_price", "")
                prev = row.get("prev_close_price", "")
                vol = row.get("volume", "")
                turnover = row.get("turnover", "")
                print(
                    f"[{data_time}] {name}({SMIC_HK}) "
                    f"现价={last} 开={open_p} 高={high} 低={low} 昨收={prev} "
                    f"成交量={vol} 成交额={turnover}"
                )
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n已退出")
    finally:
        quote_ctx.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
