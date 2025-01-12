# https://www.mexc.com/zh-CN/mexc-api
# l241025097@outlook.com
# cn198641S@
# Access Key: mx0vglnn25H22CzIww
# Secret Key: 208bd42dec0c4aab9eb57e8ae08b7a74

from mexc_sdk import Spot
spot = Spot(api_key="mx0vglnn25H22CzIww", api_secret="208bd42dec0c4aab9eb57e8ae08b7a74")
print(spot.ping())
