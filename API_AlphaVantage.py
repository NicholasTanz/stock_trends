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

AlphaVantage_API_Key = AlphaVantage_API_KEY
BaseURL = "https://www.alphavantage.co/query"

def Create_Graph_And_Stats_On_AlphaVantageDataSet(dataSet):
    """Creates a graph and generates basic statistics
    
    NOTE: only works for Daily, Weekly and Monthly datasets.

    Args:
        dataSet: time series json data from Alpha Vantage API call.
    
    Returns:
        Dict: dictonary containing graph data, and statistics.
    """ 

    x_values = []
    y_values = []
    for date, innerDataDict in dataSet.items():
        y_values.append(float(innerDataDict["1. open"]))
        x_values.append(datetime.strptime(date, "%Y-%m-%d"))
    
    # Generate Stats. 
    stats = {
    'mean':np.mean(y_values),
    'stdev':np.std(y_values),
    'median':np.median(y_values),
    'max':np.max(y_values),
    'min':np.min(y_values)
    }

    # Create Graph.
    plt.figure(figsize=(8,6))
    plt.scatter(x_values, y_values)
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.title('Stock Price')

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
    else:
        # TODO: add error handle for invalid option.
        pass

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
    json = request.json()
    output = []
    timeSeries = f"Time Series ({str(timeInterval)}min)"
    timeSeriesDict = json[timeSeries]
    
    for _, innerDict in timeSeriesDict.items():
        # innerDict is a specific point (i.e. datapoint)
        output.append(float(innerDict["1. open"]))

    return output


def Get_News_On_Stock(ticker: str, use_mock_data: bool=False):
    """ utilizes Alpha Vantage API to gather news and sentiment of a stock. 

    Args:
        ticker: Stock ticker. (Ex: AAPL, MSFT).
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
