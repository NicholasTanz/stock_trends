'''functions to utilize the Alpha Vantage API '''
# Docs: https://www.alphavantage.co/documentation/

from StockTrends.config import AlphaVantage_API_KEY
#from config import AlphaVantage_API_KEY
import requests

AlphaVantage_API_Key = AlphaVantage_API_KEY
BaseURL = "https://www.alphavantage.co/query"


# TODO: Implement Error Handling and Improve docstrings / arg labels. 


def Get_News_On_Stock(ticker: str, use_mock_data: bool=False):
    ''' Returns the latest news on a given stock. 

    The returned value is a list of dicts which contain the following:
    * Summary (str)
    * Date Posted (str)
    * URL (str)
    * Sentiment Score (str)
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
    number_articles = 5 if int(json['items']) >= 5 else json['items'] # returns top 5 recent articles.
    for idx in range(number_articles):
        current_article = json["feed"][idx]
        article_output = {"summary":current_article["summary"],
                          "time_published":current_article["time_published"],
                          "url":current_article["url"], 
                          "overall_sentiment_score":current_article["overall_sentiment_score"]
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
    output = []
    for _, innerDict in data.items():
        output.append(float(innerDict['1. open']))

    return output

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