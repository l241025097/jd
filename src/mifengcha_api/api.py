import os
import pandas as pd
from requests import get

API_KEY = "BANXGJU8IQIA2LMVC77IEULMKWVKH5WK3WR6CQVG"

def current_path():
    now_path = os.path.dirname(os.path.abspath(__file__))
    if not now_path:
        now_path = os.getcwd()
    return now_path

# 获取所有支持的交易所列表
def get_markets():
    url = f"http://data.mifengcha.com/api/v3/markets?api_key={API_KEY}"
    params_dict = {
        "page": 0,
        "size": 100
    }
    # params_dict = {
    #     "slug": "binance"
    # }
    res = get(url, params=params_dict)
    return "markets", res.json()

# 获取指定交易所信息
def get_markets_from(slug):
    url = f"http://data.mifengcha.com/api/v3/markets/{slug}?api_key={API_KEY}"
    res = get(url)
    return f"markets_{slug}", res.json()

# 获取所有支持的币种列表
def get_symbols():
    url = f"https://data.mifengcha.com/api/v3/symbols?api_key={API_KEY}"
    params_dict = {
        "details": 0,
        "page": 0,
        "size": 100
    }
    res = get(url, params=params_dict)
    return "symbols", res.json()

# 获取单个币种信息
def get_symbols_from(slug):
    url = f"https://data.mifengcha.com/api/v3/symbols/{slug}?api_key={API_KEY}"
    res = get(url)
    return f"symbols_{slug}", res.json()

# 获取汇率
# 更新时间：数字货币更新时间为60秒，法币更新时间为4小时。
# 数据来源：数字货币汇率从加权平均计算的币种价格获取。
# 数据来源：法币汇率由外汇交易所以及各大银行牌价结合。
def get_exchange_rate():
    url = f"https://data.mifengcha.com/api/v3/exchange_rate?api_key={API_KEY}"
    res = get(url)
    return "exchange_rate", res.json()

# 获取币种价格
# 更新时间：5秒-60秒，按照交易量大小分级，交易量最大的币种5秒更新一次价格。
def get_price(slug):
    url = f"https://data.mifengcha.com/api/v3/price?api_key={API_KEY}"
    params_dict = {
        "slug": slug,
        "page": 0,
        "size": 100
    }
    res = get(url, params=params_dict)
    return "price", res.json()

# 获取币种历史价格
# 数据来源：每5分钟快照一次当前价格，交易量。
# 数据点间隔[5m,15m,30m,1h,2h,6h,12h,1d,2d], 默认情况下根据 start，end 计算
# interval不为空的情况下，需要满足 (end - start) / interval <= 1000，如果请求超过1000个数据点则会响应400
def get_history(slug, start=None, end=None, interval=None):
    url = f"https://data.mifengcha.com/api/v3/price/history?api_key={API_KEY}"
    params_dict = {
        "slug": slug
    }
    if start is not None:
        params_dict.update({
        "start": start
        })
    if end is not None:
        params_dict.update({
        "end": end
        })
    if interval is not None:
        params_dict.update({
            "interval": interval
        })
    res = get(url, params=params_dict)
    return "history", res.json()

# 获取交易对K线数据
# K线类型(数据点间隔)[1m,5m,15m,30m,1h,6h,1d]，默认5m
# 单次请求最大可获取2000条数据，传入参数需满足 (end - start) / interval <= 2000， 如果请求超过2000个数据点则会响应400 10010 Duration Limited
def get_kline(desc, start=None, end=None, interval=None):
    url = f"https://data.mifengcha.com/api/v3/kline?api_key={API_KEY}"
    params_dict = {
        "desc": desc
    }
    if start is not None:
        params_dict.update({
        "start": start
        })
    if end is not None:
        params_dict.update({
        "end": end
        })
    if interval is not None:
        params_dict.update({
            "interval": interval
        })
    res = get(url, params=params_dict)
    return "kline", res.json()

def execute():
    now_path = current_path()
    parent_path = os.path.dirname(now_path)
    # name, data = get_markets()
    # name, data = get_markets_from("binance")
    # name, data = get_symbols()
    # name, data = get_symbols_from("tether")
    # name, data = get_exchange_rate()
    # name, data = get_price("bitcoin, ethereum")
    # name, data = get_history("bitcoin", 1577724600000, 1577758200000, "1h")
    name, data = get_kline("gate-io_BTC_USDT", 1577724600000, 1577758200000, "1h")
    output_path = os.path.join(parent_path, "datas", f"{name}.xlsx")
    if isinstance(data, (dict, )):
        data = [data]
    pd.DataFrame(data).to_excel(output_path, index=False)

if __name__ == "__main__":
    execute()
