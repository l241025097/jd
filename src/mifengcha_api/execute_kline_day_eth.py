import os
import sys
from datetime import datetime
from sqlalchemy import Integer, Float
from kline_day import get_kline_day
from api import current_path
now_path = current_path()
parent_path = os.path.dirname(now_path)
sys.path.append(parent_path)
from utils import get_log

def execute():
    currency = "eth"
    app_name = f"kline_day_{currency}"
    currency_begin_time = datetime(2017, 10, 1)
    log_obj = get_log(app_name)
    col_dict = {
        "T": {
            "en_name": "timestamp",
            "zh_name": "时间戳",
            "type": Integer()
        },
        "o": {
            "en_name": "open",
            "zh_name": "开盘价",
            "type": Float()
        },
        "h": {
            "en_name": "high",
            "zh_name": "最高价",
            "type": Float()
        },
        "l": {
            "en_name": "low",
            "zh_name": "最低价",
            "type": Float()
        },
        "c": {
            "en_name": "close",
            "zh_name": "收盘价",
            "type": Float()
        },
        "v": {
            "en_name": "volume",
            "zh_name": "交易量",
            "type": Float()
        }
    }
    get_kline_day(currency, currency_begin_time, col_dict, log_obj)

if __name__ == "__main__":
    execute()
