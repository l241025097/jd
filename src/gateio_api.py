from __future__ import print_function
import gate_api
from gate_api.exceptions import ApiException, GateApiException
# Defining the host is optional and defaults to https://api.gateio.ws/api/v4
# See configuration.py for a list of all supported configuration parameters.
configuration = gate_api.Configuration(
    host = "https://api.gateio.ws/api/v4"
)

api_client = gate_api.ApiClient(configuration)
# Create an instance of the API class
api_instance = gate_api.SpotApi(api_client)
currency_pair = 'CFX_USDT' # str | Currency pair (optional)
timezone = 'utc0' # str | Timezone (optional) 北京时间8点
# timezone = 'utc8' # str | Timezone (optional) 北京时间0点

try:
    # Retrieve ticker information
    # api_response = api_instance.list_tickers(currency_pair=currency_pair, timezone=timezone)
    api_response = api_instance.list_currency_pairs()
    currency_list = []
    for x in api_response:
        # print(dir(x))
        if x.base.startswith("Z"):
            print(x.base, x.quote)
        # currency_list.append((x.base, x.quote))
    # print(currency_list)
except GateApiException as ex:
    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
except ApiException as e:
    print("Exception when calling SpotApi->list_tickers: %s\n" % e)
