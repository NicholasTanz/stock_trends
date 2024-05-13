'''functions to utilize the Tiingo API '''
# Docs: https://www.tiingo.com/documentation/

from StockTrends.config import Tiingo_API_KEY
import requests

Tiingo_API_Key = Tiingo_API_KEY

headers = {
        'Content-Type': 'application/json',
        'Authorization' : f'Token {Tiingo_API_Key}'
        }

baseURL = "https://api.tiingo.com/tiingo/daily/Meta/prices"

def Get_Current_Stock_Price(ticker:str, use_mock_data:bool=False):
    """ utilizes Tiingo API to return stock open price.

    # NOTE: this utilizes the EOD prices, as intraday requires a subscription. 

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
        use_mock_data: data utilized for testing. 

    Returns:
        float: Stock open price for given ticker. 
    """ 

    URL = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
    request = requests.get(URL, headers=headers)
    
    return request.json()[0]['open']