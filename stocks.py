from flask import Flask, render_template, request, Blueprint
from StockTrends.API_AlphaVantage import Get_News, Get_Intraday_Data_On_Stock, Get_Stock_Data

bp = Blueprint('stocks', __name__, url_prefix='/stocks')

# Stocks page
@bp.route('/stock', methods=('GET','POST'))
def stock_home_page():
    if request.method == 'POST':
        ticker = request.form['stock_ticker']
        selected_news_articles = 'news_articles' in request.form
        selected_last_30_day_prices = 'last_30_day_prices' in request.form
        selected_intraday_data = 'intraday_data' in request.form

        # Error Handling - checking if the user selected at least one checkbox option and a ticker.
        if(ticker == '' or (not selected_intraday_data and not selected_last_30_day_prices and not selected_news_articles)):
            return render_template('stocks/stocks.html', error_message="Please enter a single stock ticker and select at least one option from the drop-down.")

        # Calling API and generating output as needed.
        output_news_data = False
        output_price_data = False
        output_intraday_data = False
        
        # NOTE: assumption is that the client will supply a valid ticker. 
        if(selected_news_articles):
            output_news_data = Get_News(str(ticker), None, True)

        if(selected_last_30_day_prices):
            output_price_data = Get_Stock_Data(str(ticker), 'Daily', True)

        if(selected_intraday_data):
            output_intraday_data = Get_Intraday_Data_On_Stock(str(ticker), 5, True)

        return render_template('stocks/stocks.html', 
                    output_news_data=output_news_data, 
                    output_price_data=output_price_data, 
                    output_intraday_data=output_intraday_data)
    
    return render_template('stocks/stocks.html')
