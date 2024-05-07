from flask import Flask, render_template, redirect, url_for, request
from StockTrends.API_AlphaVantage import Get_News_On_Stock, Get_Intraday_Data_On_Stock, Get_Daily_Data_On_Stock

# TODO: add blueprints for the stock and industry section to help cleanup. 
# TODO: add login feature to have user history and recommendations. 

def create_app(test_config=None):
    # create application and basic config. 
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # home page 
    @app.route('/')
    def basic():
        return render_template('base.html')

    # Stocks page
    @app.route('/stocks', methods=('GET','POST'))
    def stock_home_page():
        if request.method == 'POST':
            ticker = request.form['stock_ticker']
            selected_news_articles = 'news_articles' in request.form
            selected_last_30_day_prices = 'last_30_day_prices' in request.form
            selected_intraday_data = 'intraday_data' in request.form

            # Error Handling - checking if the user selected at least one checkbox option and a ticker.
            if(ticker == '' or (not selected_intraday_data and not selected_last_30_day_prices and not selected_news_articles)):
                return render_template('stocks.html', error_message="Please enter a single stock ticker and select at least one option from the drop-down.")

            # Calling API and generating output as needed.
            output_news_data = False
            output_price_data = False
            output_intraday_data = False
            
            # NOTE: assumption is that the client will supply a valid ticker. 
            if(selected_news_articles):
                output_news_data = Get_News_On_Stock(str(ticker))

            if(selected_last_30_day_prices):
                output_price_data = Get_Daily_Data_On_Stock(str(ticker))

            if(selected_intraday_data):
                #output_intraday_data = Get_Intraday_Data_On_Stock(str(ticker)) #NOTE: intraday require subscription to AlphaVantage API.          
                pass

            return render_template('stocks.html', 
                       output_news_data=output_news_data, 
                       output_price_data=output_price_data, 
                       output_intraday_data=output_intraday_data)
        
        return render_template('stocks.html')

    return app