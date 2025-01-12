import os
import re
import pandas as pd
import gate_api
from requests import get
from lxml.html import fromstring
from datetime import datetime
from io import BytesIO
from utils import current_path

html_path = os.path.join(current_path(), "datas", "htmls")

def get_gpu_overview():
    url = "https://www.kryptex.com/en/best-gpus-for-mining"
    res = get(url)
    file_path = os.path.join(html_path, "best_gpus.html")
    with open(file_path, "wb") as fw:
        fw.write(res.content)

def process_gpu_overview():
    file_path = os.path.join(html_path, "best_gpus.html")
    with open(file_path, "rb") as fr:
        html_bytes = fr.read()
    root = fromstring(html_bytes.decode())
    table_header_list = []
    for eobj in root.cssselect("table thead tr th span strong"):
        table_header_list.append(eobj.text)
    table_body_list = []
    for eobj in root.cssselect("table tbody tr"):
        gpu_profit_list = []
        for sub_eobj in eobj.cssselect("td span nobr"):
            gpu_profit_list.append(sub_eobj.text.strip())
        cost_list = []
        for sub_eobj in eobj.cssselect("td nobr span"):
            cost_list.append(sub_eobj.text.strip())
        payback_period_list = []
        for sub_eobj in eobj.cssselect("td div div span"):
            payback_period_list.append(sub_eobj.text.strip())
        currency_list = []
        for sub_eobj in eobj.cssselect("td div"):
            if not sub_eobj.text:
                continue
            if not sub_eobj.text.strip():
                continue
            currency_list.append(sub_eobj.text.strip())
        each_row_list = [gpu_profit_list[0]] + [cost_list[0]] + currency_list + [gpu_profit_list[1]] + [payback_period_list[0]]
        each_unit_list = [None] + ["USD"] + ([None] * len(currency_list)) + ["USD_PER_MONTH"] + ["days"]
        table_body_list.append({(f"{key}_{unit}" if unit else key): value for key, value, unit in zip(table_header_list, each_row_list, each_unit_list)})
    return pd.DataFrame(table_body_list)

def get_worker_hash_rate(currency, type_str, wallet_addr):
    url = f"https://pool.kryptex.com/en/{currency}/miner/{type_str}/{wallet_addr}"
    res = get(url)
    file_path = os.path.join(html_path, f"worker_hash_{type_str}.html")
    with open(file_path, "wb") as fw:
        fw.write(res.content)

def process_worker_hash_rate(type_str):
    file_path = os.path.join(html_path, f"worker_hash_{type_str}.html")
    with open(file_path, "rb") as fr:
        html_bytes = fr.read()
    root = fromstring(html_bytes.decode())
    location_index = None
    location_eobj = None
    for eobj in root.cssselect("div:contains('Average Hashrate (6H)')"):
        sub_eobj_list = eobj.getchildren()
        for i, each_eobj in enumerate(sub_eobj_list):
            if each_eobj is None:
                continue
            if each_eobj.text is None:
                continue
            if "Average Hashrate (6H)" not in each_eobj.text:
                continue
            location_index = i
            location_eobj = eobj
            break
    sub_eobj_list = location_eobj.getchildren()
    for sub_eobj in sub_eobj_list[location_index + 1].cssselect("span:contains('H/s')"):
        if not sub_eobj.text:
            continue
        hash_str = sub_eobj.text.strip()
        regex_obj = re.match("^.*?(\d+\.\d+) (.*)$", hash_str)
        if not regex_obj:
            continue
        return {"actual_hash_rate": float(regex_obj.group(1)), "unit": regex_obj.group(2).strip(), "update_time": datetime.now()}

def get_payout_csv(currency, wallet_addr):
    url = f"https://pool.kryptex.com/{currency}/api/v1/miner/payouts/{wallet_addr}/csv"
    res = get(url)
    with BytesIO() as fw:
        fw.write(res.content)
        fw.seek(0)
        return pd.read_csv(fw)

def process_payout_csv(payout_df, currency, actual_hash_rate):
    payout_df["date"] = pd.to_datetime(payout_df["date"])
    payout_df = payout_df.sort_values(by="date", ascending=False)
    delta_hours = (payout_df.iloc[0]["date"] - payout_df.iloc[1]["date"]).total_seconds() / 3600
    earn_per_hour_per_hash = payout_df.iloc[0][f"amount_{currency}"] / delta_hours / actual_hash_rate
    return earn_per_hour_per_hash

def get_exchange_rate(base="USD", target="CNY"):
    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    res = get(url)
    result_dict = res.json()
    update_time = datetime.fromtimestamp(float(result_dict["time_last_updated"]))
    rate = result_dict["rates"][target]
    return {"exchange_base": base, "exchange_quote": target, "exchange_rate": rate, "update_time": update_time}

def get_currency_price_from_gateio(currency_pair, timezone="utc0"):
    use_cols = ["currency_pair", "last", "change_percentage", "base_volume", "quote_volume", "high_24h", "low_24h"]
    # timezone = 'utc0' # str | Timezone (optional) 世界时间0点，北京时间8点
    # timezone = 'utc8' # str | Timezone (optional) 北京时间0点
    configuration = gate_api.Configuration(host="https://api.gateio.ws/api/v4")
    api_client = gate_api.ApiClient(configuration)
    api_instance = gate_api.SpotApi(api_client)
    api_response = api_instance.list_tickers(currency_pair=currency_pair, timezone=timezone)
    res_dict = api_response[0].to_dict()
    res_dict = {key: res_dict[key] for key in use_cols}
    res_dict.update({"update_time": datetime.now()})
    return res_dict

def get_currency_price_from_sevenseas(currency_pair):
    currency_pair = currency_pair.replace("_", "-")
    api_url = "https://www.sevenseas.exchange/api/v1"
    response = get(f"{api_url}/markets/{currency_pair}")
    data = response.json()
    return data

def calculate_power_fee_per_hour(power_w):
    new_worker_power_kwh = power_w / 1000
    power_fee_per_kwh = 0.5283
    power_fee_per_hour = new_worker_power_kwh * power_fee_per_kwh
    return power_fee_per_hour
