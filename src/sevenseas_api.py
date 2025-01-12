import requests
api_url = 'https://www.sevenseas.exchange/api/v1'

def fetch_markets():
    try:
        response = requests.get(f'{api_url}/markets/ZEPH-USDT')
        data = response.json()
        print(data)
    except Exception as error:
        print("Error fetching market data:", error)

if __name__ == "__main__":
    fetch_markets()
