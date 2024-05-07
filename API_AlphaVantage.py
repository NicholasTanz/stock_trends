'''functions to utilize the Alpha Vantage API '''
# Docs: https://www.alphavantage.co/documentation/

import config
import requests

AlphaVantage_API_Key = config.AlphaVantage_API_KEY
BaseURL = "https://www.alphavantage.co/query"


# TODO: Implement Error Handling and Improve docstrings. 

def Get_News_On_Stock(ticker):
    ''' Returns the latest news on a given stock. 
    '''
    params = {
        'function':"NEWS_SENTIMENT",
        'tickers':ticker,
        'apikey':AlphaVantage_API_Key
    }

    request = requests.get(BaseURL, params=params)

    

    return request

def Get_Intraday_Data_On_Stock(ticker, timeInterval=5):
    ''' Returns the Intraday data on a given stock. (timeInterval is in mins)''' 
    params = {
        'function':'TIME_SERIES_INTRADAY',
        'symbol':ticker,
        'interval':timeInterval,
        'apikey':AlphaVantage_API_Key
    }

    request = requests.get(BaseURL, params=params)
    return request

def Get_Daily_Data_On_Stock(ticker):
    ''' Returns the Daily data on a given stock. ''' 
    params = {
        'function':'TIME_SERIES_DAILY',
        'symbol':ticker,
        'apikey':AlphaVantage_API_Key
    }

    request = requests.get(BaseURL, params=params)
    return request

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

if __name__ == "__main__":
    assert(Get_News_On_Stock("AAPL").status_code == 200)
    assert(Get_Intraday_Data_On_Stock("AAPL").status_code == 200)
    assert(Get_Daily_Data_On_Stock("AAPL").status_code == 200)
    assert(Get_Weekly_Data_On_Stock("AAPL").status_code == 200)
    assert(Get_Monthly_Data_On_Stock("AAPL").status_code == 200)
    assert(Get_Quote_Endpoint("AAPL").status_code == 200)
    assert(Get_Search_Stocks("AAPL").status_code == 200)