'''functions to utilize the Tiingo API '''
# Docs: https://www.tiingo.com/documentation/

import os
import requests
TIINGO_API_KEY = os.getenv('TIINGO_API_KEY')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {TIINGO_API_KEY}'
}

def get_current_stock_price(ticker: str):
    """ utilizes Tiingo API to return stock open price.

    # NOTE: this utilizes the EOD prices, as intraday requires a subscription.

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
        use_mock_data: data utilized for testing.

    Returns:
        float: Stock open price for given ticker.
    """

    url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
    request = requests.get(url, headers=headers, timeout=20)

    return request.json()[0]['open']
