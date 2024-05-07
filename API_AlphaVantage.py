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


# TODO: Implement Error Handling and Improve docstrings / arg labels. 


def Create_Graph_And_Stats_On_AlphaVantageDataSet(alphaVantageDataSet):
    #TODO: add functionality for intraday, week, month, etc.
    ''' '''
    x_vals = []
    y_vals = []
    for (date, innerDataDict) in (alphaVantageDataSet.items()):
        y_vals.append(float(innerDataDict["1. open"]))
        x_vals.append(datetime.strptime(date, "%Y-%m-%d"))
    
    # Generate Stats. 
    stats = {
    'mean':np.mean(y_vals),
    'stdev':np.std(y_vals),
    'median':np.median(y_vals),
    'max':np.max(y_vals),
    'min':np.min(y_vals)
    }

    # Create Graph.
    plt.figure(figsize=(8,6))
    plt.scatter(x_vals, y_vals)
    plt.xlabel('Time (Days)')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.title('Stock Price')

    # Save Plot
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return {'plot':plot_data, 'stats':stats}

def Get_News_On_Stock(ticker: str, use_mock_data: bool=False):
    ''' Returns the latest news on a given stock. 

    The returned value is a list of dicts which contain the following:
    * Summary (str)
    * Date Posted (str)
    * URL (str)
    * Sentiment Score (str)
    * Sentiment Label (str)
    '''

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
    number_articles = 20 if int(json['items']) >= 20 else json['items'] # returns top 5 recent articles.
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


# NOTE: This api call requires a subscription to the AlphaVantage API. 
def Get_Intraday_Data_On_Stock(ticker: str, timeInterval=5, use_mock_data: bool=False):
    ''' Returns the Intraday data on a given stock. (timeInterval is in mins)
    
    * timeInterval: (must be 1, 5, 15, 30, or 60)
    
    The returned value is a list of ints that represent open prices, with the above
    time interval in-between each value. 
    
    ''' 
    
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

def Get_Daily_Data_On_Stock(ticker:str, use_mock_data:bool=False):
    ''' Returns the Daily data on a given stock. 
    
    The returned value is a list of the last 100 daily open values. 
    ''' 

    if(use_mock_data):
        request = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo')
    else:
        params = {
            'function':'TIME_SERIES_DAILY',
            'symbol':ticker,
            'apikey':AlphaVantage_API_Key
        }

        request = requests.get(BaseURL, params=params)

    # parse output
    data = request.json()["Time Series (Daily)"]

    return Create_Graph_And_Stats_On_AlphaVantageDataSet(data)

def Get_Weekly_Data_On_Stock(ticker):
    ''' Returns the Weekly data on a given stock. ''' 
    params = {
        'function':'TIME_SERIES_WEEKLY',
        'symbol':ticker,
        'apikey':AlphaVantage_API_Key
    }

    request = requests.get(BaseURL, params=params)
    return request

def Get_Monthly_Data_On_Stock(ticker):
    ''' Returns the Monthly data on a given stock. ''' 
    params = {
        'function':'TIME_SERIES_MONTHLY',
        'symbol':ticker,
        'apikey':AlphaVantage_API_Key
    }

    request = requests.get(BaseURL, params=params)
    return request

def Get_Quote_Endpoint(ticker):
    ''' Returns the latest quote on a given stock. ''' 
    params = {
        'function':'GLOBAL_QUOTE',
        'symbol':ticker,
        'apikey':AlphaVantage_API_Key
    }

    request = requests.get(BaseURL, params=params)
    return request

def Get_Search_Stocks(keywords):
    ''' Returns the stocks that match the given keywords. ''' 
    params = {
        'function':'SYMBOL_SEARCH',
        'keywords':keywords,
        'apikey':AlphaVantage_API_Key
    }

    request = requests.get(BaseURL, params=params)
    return request


def Get_Advanced_Analytics_On_Stock(ticker):
    ''' Returns various metrics on a given stock.'''
    pass 