from flask import Flask, render_template, redirect, url_for, request, g, session, flash
from StockTrends.API_AlphaVantage import Get_News, Get_Intraday_Data_On_Stock, Get_Stock_Data
from StockTrends.db import get_user_positions, get_userID, get_user, register_user, update_balance, register_user_stock_purchase, update_user_stock_purchase, delete_user_stock_purchase

from StockTrends.API_Tiingo import Get_Current_Stock_Price
from werkzeug.security import check_password_hash
from . import db
import os

# TODO: add blueprints for the stock and industry section to help cleanup. 
# TODO: add login feature to have user history and recommendations. 

def create_app(test_config=None):
    # create application and basic config. 
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'StockTrends.sqlite')
    )
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # init database
    db.init_app(app)
    
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
                output_news_data = Get_News(str(ticker), True)

            if(selected_last_30_day_prices):
                output_price_data = Get_Stock_Data(str(ticker), 'Daily', True)

            if(selected_intraday_data):
                output_intraday_data = Get_Intraday_Data_On_Stock(str(ticker), 5, True) #NOTE: intraday require subscription to AlphaVantage API.          

            return render_template('stocks.html', 
                       output_news_data=output_news_data, 
                       output_price_data=output_price_data, 
                       output_intraday_data=output_intraday_data)
        
        return render_template('stocks.html')
    
    # Option for Paper Trading   
    @app.route('/PaperTrade')
    def paper_trade():
        return render_template("papertrade.html")


    # Login page
    @app.route('/login', methods=('GET', 'POST'))
    def login():
        if request.method == 'POST':
            # login logic
            username = request.form['username']
            password = request.form['password']
            error = None

            userID = get_userID(username)[0]
            user = get_user(userID)

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            # No error - user can be logged in.
            if error == None:
                session.clear()
                session['user_id'] = user['id']

                balance = user['balance']
                positions = get_user_positions(session['user_id'])
                return render_template("auth.html", balance=balance, username=username, positions=positions)

            return render_template("login.html", error=error)

        # simply return page.
        return render_template('login.html')
    

    # Register Page
    @app.route('/register', methods=('GET', 'POST'))
    def regsiter():
        if request.method == 'POST':
            # register user
            username = request.form['username']
            password = request.form['password']
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                try:
                    register_user(username, password)
                    return redirect(url_for("login"))
                except db.IntegrityError:
                    error = f"User {username} is already registered, please select another username."

            return render_template('register.html', error=error)
            
        
        return render_template("register.html")

    # Deposit Page
    @app.route('/deposit', methods=('POST',))
    def deposit():
        user = get_user(session['user_id'])
        user_balance = float(request.form['amount']) + user['balance']
        update_balance(session['user_id'], user_balance)

        return render_template('auth.html', username=user['username'], balance=user_balance)

    #  Purchase / Sell stock page
    @app.route('/purchase', methods=('POST',))
    def stock_options():
        ticker = request.form['ticker']
        share_amount = float(request.form['shares'])
        stock_price = Get_Current_Stock_Price(str(ticker))
        user = get_user(session['user_id'])
        user_balance = user['balance']

        if(request.form['action'] == 'purchase'):
            new_balance = user_balance - (stock_price * share_amount)
            
            # User cannot purchase stock (insufficient funds)
            if(new_balance < 0):
                return render_template('auth.html', username=user['username'], error='Insufficient funds.', balance=user['balance'])

            update_balance(session['user_id'], new_balance)
            register_user_stock_purchase(session['user_id'], share_amount, stock_price, ticker)


            positions = get_user_positions(session['user_id'])
            return render_template('auth.html', username=user['username'], balance=new_balance, positions=positions)

        else:
            # need to check if they have enough shares. 
            user_positions = get_user_positions(session['user_id'])
            total_shares = 0
            potential_delete_shares = []
            successful_deletion = False
            for position in user_positions:
                if position['stock_symbol'] == ticker:
                    total_shares += position['shares']
                    
                    # check to see if there is enough shares
                    if(total_shares >= share_amount):
                        remaining_shares = (total_shares - share_amount)
                        successful_deletion = True

                        # if remaining shares left, update count for last position.
                        if(remaining_shares != 0):
                            update_user_stock_purchase(position['id'], remaining_shares)

                        # delete remaining positions.
                        for position in potential_delete_shares:
                            delete_user_stock_purchase(position['id'])

                    potential_delete_shares.append(position)

            if(successful_deletion):
                new_balance = (share_amount * stock_price) + user['balance']
                update_balance(user['id'], new_balance)

                user_positions = get_user_positions(user['id'])
                return render_template('auth.html', username=user['username'], balance=new_balance, positions=user_positions)
            else:
                user_positions = get_user_positions(user['id'])
                return render_template('auth.html', username=user['username'], balance=user['balance'], error='Insufficient shares.', positions=user_positions)


    return app