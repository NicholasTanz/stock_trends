'''functions to utilize the Alpha Vantage API '''
# Docs: https://www.alphavantage.co/documentation/

from StockTrends.config import AlphaVantage_API_KEY
#from config import AlphaVantage_API_KEY
from datetime import datetime
import requests
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import pandas as pd

# TODO: Add Error Handling for functions. 
AlphaVantage_API_Key = AlphaVantage_API_KEY
BaseURL = "https://www.alphavantage.co/query"

def Create_Graph_And_Stats_On_AlphaVantageDataSet(dataSet, isIntraday:bool=False):
    """Creates a graph and generates basic statistics

    Args:
        dataSet: time series json data from Alpha Vantage API call.
        isIntraday: flag that should be True when passing Intraday data. 
    
    Returns:
        Dict: dictonary containing graph data, and statistics.
    """ 

    if(isIntraday):
        format_string = "%Y-%m-%d %H:%M:%S"
    else:
        format_string = "%Y-%m-%d"

    x_values = []
    y_values = []

    for date, innerDataDict in dataSet.items():
        y_values.append(float(innerDataDict["1. open"]))
        x_values.append(datetime.strptime(date, format_string))
    
    # Generate Stats. 
    stats = {
    'mean':np.mean(y_values),
    'stdev':np.std(y_values),
    'median':np.median(y_values),
    'max':np.max(y_values),
    'min':np.min(y_values)
    }

    df = pd.DataFrame({'Date': x_values, 'Price': y_values})

    # Create Graph
    plt.figure(figsize=(12, 8))

    # Plot original data + ma's
    plt.scatter(df['Date'], df['Price'], label='Original Data', color='#007acc', linewidth=1.5)

    # Calculate moving averages
    df['MA_5'] = df['Price'].rolling(window=5).mean()
    df['MA_10'] = df['Price'].rolling(window=10).mean()
    df['MA_15'] = df['Price'].rolling(window=15).mean()

    if(isIntraday):
        plt.plot(df['Date'], df['MA_5'], label='5-min MA', color='#FF6F61', linestyle='--', linewidth=1)
        plt.plot(df['Date'], df['MA_10'], label='10-min MA', color='#8B0000', linestyle='--', linewidth=1)
        plt.plot(df['Date'], df['MA_15'], label='15-min MA', color='#228B22', linestyle='--', linewidth=1)        
    else:
        plt.plot(df['Date'], df['MA_5'], label='5-Day MA', color='#FF6F61', linestyle='--', linewidth=1)
        plt.plot(df['Date'], df['MA_10'], label='10-Day MA', color='#8B0000', linestyle='--', linewidth=1)
        plt.plot(df['Date'], df['MA_15'], label='15-Day MA', color='#228B22', linestyle='--', linewidth=1)

    plt.xlabel('Date', fontsize=14, color='#444444') 
    plt.ylabel('Price', fontsize=14, color='#444444')
    plt.title('Stock Price Analysis', fontsize=24, color='#333333', fontweight='bold', fontfamily='sans-serif')

    # Add grid with subtle lines
    plt.grid(True, linestyle='-', linewidth=0.5, alpha=0.1)

    # Remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Set background color with a gradient effect
    plt.gca().set_facecolor('#F7F7F7')

    plt.xticks(fontsize=12, color='#666666')
    plt.yticks(fontsize=12, color='#666666')

    plt.legend(loc='upper left', fontsize=12, edgecolor='#333333', facecolor='#F7F7F7')

    plt.gca().patch.set_edgecolor('black')
    plt.gca().patch.set_linewidth(1)
    plt.gca().patch.set_facecolor('none')

    # Save Plot
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return {'plot':plot_data, 'stats':stats}

def Get_Stock_Data(ticker:str, timeInterval:str, use_mock_data:bool=False):
    """ utilizes Alpha Vantage API to gather stock data. 

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
        timeInterval: time interval must be 'Daily', 'Weekly', or 'Monthly'.
        use_mock_data: data utilized for testing. 

    Returns:
        Dict: dictonary containing graph data, and statistics.
    """ 
    
    if(timeInterval == "Daily"):
        function_param = "TIME_SERIES_DAILY"
        key = "Time Series (Daily)"
    elif(timeInterval == "Weekly"):
        function_param = "TIME_SERIES_WEEKLY"
        key = "Weekly Time Series"
    elif(timeInterval == "Monthly"):
        function_param = "TIME_SERIES_MONTHLY"
        key = "Monthly Time Series"

    if(use_mock_data):
        request = requests.get(f'https://www.alphavantage.co/query?function={function_param}&symbol=IBM&apikey=demo')
    else:
        params = {
            'function':f'TIME_SERIES_{function_param}',
            'symbol':ticker,
            'apikey':AlphaVantage_API_Key
        }

        request = requests.get(BaseURL, params=params)

    # parse output
    data = request.json()[key]

    return Create_Graph_And_Stats_On_AlphaVantageDataSet(data)

def Get_Intraday_Data_On_Stock(ticker: str, timeInterval:int=5, use_mock_data: bool=False):
    """ utilizes Alpha Vantage API to gather intraday stock data. 

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
        timeInterval: time interval (in minutes) must be 1, 5, 10, 15, 30, 60.
        use_mock_data: data utilized for testing. 

    Returns:
        List: list containing opening prices at the given timeInterval above.
    """     
    
    if(use_mock_data):
        request = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo')
    else:
        params = {
            'function':'TIME_SERIES_INTRADAY',
            'symbol':ticker,
            'interval':timeInterval,
            'apikey':AlphaVantage_API_Key
        }

        request = requests.get(BaseURL, params=params)
    
    
    # parse output
    data = request.json()[f"Time Series ({str(timeInterval)}min)"]

    return Create_Graph_And_Stats_On_AlphaVantageDataSet(data, True)

def Get_News(ticker: str, sector: str, use_mock_data: bool=False):
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


    if(use_mock_data):
        request = requests.get('https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo')
    else:
        params = {
            'function':"NEWS_SENTIMENT",
            'tickers':ticker,
            'apikey':AlphaVantage_API_Key
        }
        request = requests.get(BaseURL, params=params)

    # parse output
    json = request.json()
    output = []
    number_articles = 20 if int(json['items']) >= 20 else json['items']
    for idx in range(number_articles):
        current_article = json["feed"][idx]
        article_output = {"summary":current_article["summary"],
                          "time_published":current_article["time_published"],
                          "url":current_article["url"], 
                          "overall_sentiment_score":current_article["overall_sentiment_score"],
                          "overall_sentiment_label":current_article["overall_sentiment_label"]
                         }
        
        output.append(article_output)

    return output

def Get_US_Market_Data(use_mock_data: bool=False):
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

    if(use_mock_data):
        test_URLS = [
            f"{BaseURL}?function=CPI&interval=monthly&apikey=demo",
            f"{BaseURL}?function=INFLATION&apikey=demo",
            f"{BaseURL}?function=RETAIL_SALES&apikey=demo",
            f"{BaseURL}?function=UNEMPLOYMENT&apikey=demo",
            f"{BaseURL}?function=REAL_GDP&interval=annual&apikey=demo",
            f"{BaseURL}?function=TREASURY_YIELD&interval=monthly&maturity=10year&apikey=demo",
            f"{BaseURL}?function=FEDERAL_FUNDS_RATE&interval=monthly&apikey=demo"
        ]
        for Key, URL in zip(functions, test_URLS):
            request = requests.get(URL)
            us_market_data[Key] = request.json()["data"][0]

    else:
        for function in functions:
            params = {
                'function':function,
                'apikey':AlphaVantage_API_Key
            },

            request = requests.get(BaseURL, params=params)
            us_market_data[function] = request.json()["data"][0]

    return us_market_data

def Get_Ticker_Suggestions(user_input: str, use_mock_data:bool=False):
    """ utilizes Alpha Vantage API to recommend tickers. 

    Args:
        user_input: user input into search box. 
        use_mock_data: data utilized for testing. 

    Returns:
        List: list of suggested tickers #NOTE: tickers aren't limited to US-Stocks. 
    """


    if(use_mock_data):
        request = requests.get('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey=demo')
    
    else:
        params = {
            'function':"SYMBOL_SEARCH",
            'keywords':user_input,
            "apikey":AlphaVantage_API_KEY
        }

        request = requests.get(BaseURL, params=params)

    data = request.json()["bestMatches"]

    output = []

    for match in data:
        output.append(match["1. symbol"])
    
    return output