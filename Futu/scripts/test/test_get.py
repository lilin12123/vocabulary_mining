from futu import *

# 建立行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 订阅中芯国际（0981.HK）的实时报价
ret, data = quote_ctx.get_market_snapshot(['HK.00981'])

if ret == RET_OK:
    print("--- 连接富途成功！ ---")
    price = data['last_price'].iloc[0]
    update_time = data['update_time'].iloc[0]
    print(f"中芯国际(00981.HK) 当前最新价: {price}  更新时间: {update_time}")
else:
    print(f"连接失败: {data}")

# 关闭连接
quote_ctx.close()
