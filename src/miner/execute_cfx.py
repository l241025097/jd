import os
import json
from datetime import datetime
from pool import (
    calculate_power_fee_per_hour,
    get_exchange_rate,
    get_worker_hash_rate,
    process_worker_hash_rate,
    get_payout_csv,
    process_payout_csv,
    get_currency_price_from_gateio
)
from utils import current_path, get_log, ComplexEncoder

def execute(log_obj):
    currency = "cfx"
    output_dir = os.path.join(current_path(), "datas", "results")
    file_name = f"{currency}_earn_{datetime.now().strftime('%Y%m%d')}.json"
    output_path = os.path.join(output_dir, file_name)
    currency_pair = f"{currency.upper()}_USDT"
    wallet_addr = "cfx:aamzd1jszcr3ufz4vudkvfym5a472h31tebtt7agm3"
    new_worker_hash_rate = 40
    new_worker_power_w = 150
    power_fee_per_hour = calculate_power_fee_per_hour(new_worker_power_w)

    return_dict = {"new_worker_hash_rate": new_worker_hash_rate, "power_fee_per_hour": power_fee_per_hour}

    exchange_dict = get_exchange_rate()
    return_dict.update(exchange_dict)
    log_obj.info(exchange_dict)
    exchange_rate = exchange_dict["exchange_rate"]

    get_worker_hash_rate(currency, "payouts", wallet_addr)
    hash_rate_dict = process_worker_hash_rate("payouts")
    return_dict.update(hash_rate_dict)
    log_obj.info(hash_rate_dict)
    actual_hash_rate = hash_rate_dict["actual_hash_rate"]

    currency_price_dict = get_currency_price_from_gateio(currency_pair)
    return_dict.update(currency_price_dict)
    log_obj.info(currency_price_dict)
    avg_currency_price = float(currency_price_dict["quote_volume"]) / float(currency_price_dict["base_volume"])

    payout_df = get_payout_csv(currency, wallet_addr)
    earn_per_hour_per_hash = process_payout_csv(payout_df, currency, actual_hash_rate)
    earn_per_day = (new_worker_hash_rate * earn_per_hour_per_hash * avg_currency_price * exchange_rate - power_fee_per_hour) * 24
    earn_dict = {"earn_per_hour_per_hash": earn_per_hour_per_hash, "avg_currency_price": avg_currency_price, "earn_per_day_CNY": earn_per_day}
    return_dict.update(earn_dict)
    log_obj.info(earn_dict)

    with open(output_path, "w") as fw:
        json.dump(return_dict, fw, cls=ComplexEncoder)

if __name__ == "__main__":
    BEGIN = datetime.now()
    APP_NAME = f"cfx_earn_{BEGIN.strftime('%Y%m%d')}"
    log_obj = get_log(APP_NAME)
    log_obj.info(f"start: {BEGIN}".center(100, "-"))
    try:
        execute(log_obj)
    except Exception as err:
        log_obj.exception(err)
    END = datetime.now()
    DURATION = (END - BEGIN).total_seconds()
    log_obj.info(f"end: {END}, duration: {DURATION:.2f} s".center(100, "-"))
