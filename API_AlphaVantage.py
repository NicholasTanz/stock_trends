'''functions to utilize the Alpha Vantage API '''
# Docs: https://www.alphavantage.co/documentation/

from datetime import datetime
import base64
import io
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from StockTrends.config import ALPHAVANTAGE_API_KEY
# from config import ALPHAVANTAGE_API_KEY
BASE_URL = "https://www.alphavantage.co/query"

def create_graph_and_stats_on_alphavantage_data_set(
        data_set, is_intraday: bool = False):
    """Creates a graph and generates basic statistics

    Args:
        data_set: time series json data from Alpha Vantage API call.
        is_intraday: flag that should be True when passing Intraday data.

    Returns:
        Dict: dictonary containing graph data, and statistics.
    """

    if is_intraday:
        format_string = "%Y-%m-%d %H:%M:%S"
    else:
        format_string = "%Y-%m-%d"

    x_values = []
    y_values = []

    for date, inner_data_dict in data_set.items():
        y_values.append(float(inner_data_dict["1. open"]))
        x_values.append(datetime.strptime(date, format_string))

    # Generate Stats.
    stats = {
        'mean': np.mean(y_values),
        'stdev': np.std(y_values),
        'median': np.median(y_values),
        'max': np.max(y_values),
        'min': np.min(y_values)
    }

    df = pd.DataFrame({'Date': x_values, 'Price': y_values})

    # Create Graph
    plt.figure(figsize=(12, 8))

    # Plot original data + ma's
    plt.scatter(
        df['Date'],
        df['Price'],
        label='Original Data',
        color='#007acc',
        linewidth=1.5)

    # Calculate moving averages
    df['MA_5'] = df['Price'].rolling(window=5).mean()
    df['MA_10'] = df['Price'].rolling(window=10).mean()
    df['MA_15'] = df['Price'].rolling(window=15).mean()

    if is_intraday:
        plt.plot(
            df['Date'],
            df['MA_5'],
            label='5-min MA',
            color='#FF6F61',
            linestyle='--',
            linewidth=1)
        plt.plot(
            df['Date'],
            df['MA_10'],
            label='10-min MA',
            color='#8B0000',
            linestyle='--',
            linewidth=1)
        plt.plot(
            df['Date'],
            df['MA_15'],
            label='15-min MA',
            color='#228B22',
            linestyle='--',
            linewidth=1)
    else:
        plt.plot(
            df['Date'],
            df['MA_5'],
            label='5-Day MA',
            color='#FF6F61',
            linestyle='--',
            linewidth=1)
        plt.plot(
            df['Date'],
            df['MA_10'],
            label='10-Day MA',
            color='#8B0000',
            linestyle='--',
            linewidth=1)
        plt.plot(
            df['Date'],
            df['MA_15'],
            label='15-Day MA',
            color='#228B22',
            linestyle='--',
            linewidth=1)

    plt.xlabel('Date', fontsize=14, color='#444444')
    plt.ylabel('Price', fontsize=14, color='#444444')
    plt.title(
        'Stock Price Analysis',
        fontsize=24,
        color='#333333',
        fontweight='bold',
        fontfamily='sans-serif')

    # Add grid with subtle lines
    plt.grid(True, linestyle='-', linewidth=0.5, alpha=0.1)

    # Remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Set background color with a gradient effect
    plt.gca().set_facecolor('#F7F7F7')

    plt.xticks(fontsize=12, color='#666666')
    plt.yticks(fontsize=12, color='#666666')

    plt.legend(
        loc='upper left',
        fontsize=12,
        edgecolor='#333333',
        facecolor='#F7F7F7')

    plt.gca().patch.set_edgecolor('black')
    plt.gca().patch.set_linewidth(1)
    plt.gca().patch.set_facecolor('none')

    # Save Plot
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return {'plot': plot_data, 'stats': stats}


def get_stock_data(
        ticker: str,
        time_interval: str,
        use_mock_data: bool = False):
    """ utilizes Alpha Vantage API to gather stock data.

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
        time_interval: time interval must be 'Daily', 'Weekly', or 'Monthly'.
        use_mock_data: data utilized for testing.

    Returns:
        Dict: dictonary containing graph data, and statistics.
    """

    if time_interval == "Daily":
        function_param = "TIME_SERIES_DAILY"
        key = "Time Series (Daily)"
    elif time_interval == "Weekly":
        function_param = "TIME_SERIES_WEEKLY"
        key = "Weekly Time Series"
    elif time_interval == "Monthly":
        function_param = "TIME_SERIES_MONTHLY"
        key = "Monthly Time Series"

    if use_mock_data:
        request = requests.get(
            f'https://www.alphavantage.co/query?function={function_param}&symbol=IBM&apikey=demo'
            , timeout=20)
    else:
        params = {
            'function': f'TIME_SERIES_{function_param}',
            'symbol': ticker,
            'apikey': ALPHAVANTAGE_API_KEY
        }

        request = requests.get(BASE_URL, params=params, timeout=20)

    # parse output
    data = request.json()[key]

    return create_graph_and_stats_on_alphavantage_data_set(data)


def get_intraday_data_on_stock(
        ticker: str,
        time_interval: int = 5,
        use_mock_data: bool = False):
    """ utilizes Alpha Vantage API to gather intraday stock data.

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
        time_interval: time interval (in minutes) must be 1, 5, 10, 15, 30, 60.
        use_mock_data: data utilized for testing.

    Returns:
        List: list containing opening prices at the given time_interval above.
    """

    if use_mock_data:
        request = requests.get(
            'https://www.alphavantage.co/query?function=\
            TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo'
            , timeout=20)
    else:
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': ticker,
            'interval': time_interval,
            'apikey': ALPHAVANTAGE_API_KEY
        }

        request = requests.get(BASE_URL, params=params, timeout=20)

    # parse output
    data = request.json()[f"Time Series ({str(time_interval)}min)"]

    return create_graph_and_stats_on_alphavantage_data_set(data, True)


def get_news(ticker: str, use_mock_data: bool = False):
    """ utilizes Alpha Vantage API to gather news and sentiment of a stock and/or sector.

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
        sector: options: "finance", "life_sciences", "technology", "manufacturing", "blockchain".
        use_mock_data: data utilized for testing.

    Returns:
        List: list of dictonaries, with each dictonary containing the following keys:
            * summary
            * time_published
            * url
            * overall_sentiment_score
            * overall_sentiment_label
    """

    if use_mock_data:
        request = requests.get(
            'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo'
            , timeout=20)
    else:
        params = {
            'function': "NEWS_SENTIMENT",
            'tickers': ticker,
            'apikey': ALPHAVANTAGE_API_KEY
        }
        request = requests.get(BASE_URL, params=params, timeout=20)

    # parse output
    json = request.json()
    output = []
    number_articles = 20 if int(json['items']) >= 20 else json['items']
    for idx in range(number_articles):
        current_article = json["feed"][idx]
        article_output = {
            "summary": current_article["summary"],
            "time_published": current_article["time_published"],
            "url": current_article["url"],
            "overall_sentiment_score": current_article["overall_sentiment_score"],
            "overall_sentiment_label": current_article["overall_sentiment_label"]}

        output.append(article_output)

    return output


def get_us_market_data(use_mock_data: bool = False):
    """ utilizes Alpha Vantage API to gather US Market data.

    Args:
        use_mock_data: data utilized for testing.

    Returns:
        Dict: dictonary with the following keys:
            * CPI
            * Inflation
            * Retail Sales
            * Unemployment Rate
            * Real GDP
            * Treasury Yield
            * Rate
    """
    us_market_data = {}
    functions = ["CPI",
                 "INFLATION",
                 "RETAIL_SALES",
                 "UNEMPLOYMENT",
                 "REAL_GDP",
                 "TREASURY_YIELD",
                 "FEDERAL_FUNDS_RATE"
                 ]

    if use_mock_data:
        test_urls = [
            f"{BASE_URL}?function=CPI&interval=monthly&apikey=demo",
            f"{BASE_URL}?function=INFLATION&apikey=demo",
            f"{BASE_URL}?function=RETAIL_SALES&apikey=demo",
            f"{BASE_URL}?function=UNEMPLOYMENT&apikey=demo",
            f"{BASE_URL}?function=REAL_GDP&interval=annual&apikey=demo",
            f"{BASE_URL}?function=TREASURY_YIELD&interval=monthly&maturity=10year&apikey=demo",
            f"{BASE_URL}?function=FEDERAL_FUNDS_RATE&interval=monthly&apikey=demo"]
        for key, url in zip(functions, test_urls):
            request = requests.get(url, timeout=20)
            us_market_data[key] = request.json()["data"][0]

    else:
        for function in functions:
            params = {
                'function': function,
                'apikey': ALPHAVANTAGE_API_KEY
            }

            request = requests.get(BASE_URL, params=params, timeout=20)
            us_market_data[function] = request.json()["data"][0]

    return us_market_data


def get_ticker_suggestions(user_input: str, use_mock_data: bool = False):
    """ utilizes Alpha Vantage API to recommend tickers.

    Args:
        user_input: user input into search box.
        use_mock_data: data utilized for testing.

    Returns:
        List: list of suggested tickers #NOTE: tickers aren't limited to US-Stocks.
    """

    if use_mock_data:
        request = requests.get(
            'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey=demo'
            , timeout=20)

    else:
        params = {
            'function': "SYMBOL_SEARCH",
            'keywords': user_input,
            "apikey": ALPHAVANTAGE_API_KEY
        }

        request = requests.get(BASE_URL, params=params, timeout=20)

    data = request.json()["bestMatches"]

    output = []

    for match in data:
        output.append(match["1. symbol"])

    return output
