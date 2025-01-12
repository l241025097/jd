import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from api import current_path, get_kline, get_history
from sqlalchemy import create_engine, String, Float, Integer
from urllib.parse import quote
from time import time, sleep

now_path = current_path()
parent_path = os.path.dirname(now_path)
sys.path.append(parent_path)

from utils import get_log, connect_mysql, get_insert_sql, modify_fly_many

def mysql_engine(host="101.33.240.185", port=60001, user="lyn", passwd="S198641cn@", db="rich"):
    return create_engine(f"mysql+pymysql://{user}:{quote(passwd)}@{host}:{port}/{db}")

def get_kline_day(col_dict, log_obj):
    table_name = "kline_day_sol"
    sol_begin_time = datetime(2023, 6, 1)
    engine = mysql_engine()
    max_time_sql = f"select max(`timestamp`) max_time from {table_name}"
    max_time_df = pd.read_sql_query(max_time_sql, con=engine)
    max_time_int = max_time_df["max_time"].iloc[0]
    if max_time_int is not None:
        max_time_obj = datetime.fromtimestamp(max_time_int / 1000)
        sol_begin_time = max_time_obj
    judage_loop = True
    while judage_loop:
        loop_begin = time()
        time_se = pd.date_range(start=sol_begin_time, periods=2000, freq="D").to_series()
        sol_end_time = time_se.max()
        end_time_obj = datetime.now().replace(minute=0, second=0, microsecond=0)
        if sol_end_time > end_time_obj:
            sol_end_time = end_time_obj
            judage_loop = False
        sol_begin_int = int(sol_begin_time.timestamp() * 1000)
        sol_end_int = int(sol_end_time.timestamp() * 1000)
        name, data = get_kline("gate-io_SOL_USDT", sol_begin_int, sol_end_int, "1d")
        df = pd.DataFrame(data).rename(columns={key: col_dict[key]["en_name"] for key in col_dict.keys()})
        dbh ,sth = connect_mysql()
        try:
            key_list = df.columns.tolist()
            data_list = [[each_dict[key] for key in key_list] for each_dict in df.to_dict(orient="records")]
            insert_sql = get_insert_sql(table_name, key_list)
            modify_fly_many(dbh, sth, insert_sql, data_list, log_obj)
        except Exception as err:
            log_obj.exception(err)
        finally:
            sth.close()
            dbh.close()
        # df.to_sql(table_name, con=engine, index=False, if_exists="append", dtype={key: col_dict[key]["type"] for key in col_dict.keys()})
        log_obj.info(f"{sol_begin_time} -- {sol_end_time} --> {table_name}")
        loop_end = time()
        loop_diff = 1 - (loop_end - loop_begin)
        if loop_diff > 0:
            log_obj.info(f"sleep {loop_diff:.2f} s")
            sleep(loop_diff)

def execute():
    app_name = "kline_day_sol"
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
    get_kline_day(col_dict, log_obj)

if __name__ == "__main__":
    execute()
