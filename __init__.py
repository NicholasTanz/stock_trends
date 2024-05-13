from flask import Flask, render_template, redirect, url_for, request, g, session, flash
from StockTrends.API_AlphaVantage import Get_News_On_Stock, Get_Intraday_Data_On_Stock, Get_Stock_Data
from StockTrends.db import get_db
from StockTrends.API_Tiingo import Get_Current_Stock_Price
from werkzeug.security import check_password_hash, generate_password_hash
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
                output_news_data = Get_News_On_Stock(str(ticker), True)

            if(selected_last_30_day_prices):
                output_price_data = Get_Stock_Data(str(ticker), 'Daily', True)

            if(selected_intraday_data):
                output_intraday_data = Get_Intraday_Data_On_Stock(str(ticker), 5, True) #NOTE: intraday require subscription to AlphaVantage API.          

            return render_template('stocks.html', 
                       output_news_data=output_news_data, 
                       output_price_data=output_price_data, 
                       output_intraday_data=output_intraday_data)
        
        return render_template('stocks.html')
    
    # Industries Page.
    # TODO: Implmentation should be very similar to stocks page.
    @app.route('/industries')
    def industries_home_page():
        return render_template('industries.html')

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
            db = get_db()
            error = None

            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            # No error - user can be logged in.
            if error == None:
                session.clear()
                session['user_id'] = user['id']

                balance = db.execute(
                    'SELECT balance FROM user where username = ?', (username,)
                ).fetchone()
                
#                positions = get_user_positions(session['user_id'])

                return render_template("auth.html", balance=balance[0], username=username)

            return render_template("login.html", error=error)

        # simply return page.
        return render_template('login.html')
    

    # Register Page
    # TODO: add password requirements (Ex: 8 chars, 1 upper, 1 num, 1 special.)
    @app.route('/register', methods=('GET', 'POST'))
    def regsiter():
        if request.method == 'POST':
            # register user
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                try:
                    db.execute(
                        "INSERT INTO user (username, password) VALUES (?, ?)",
                        (username, generate_password_hash(password)),
                    )
                    db.commit()
                except db.IntegrityError:
                    error = f"User {username} is already registered, please select another username."
                else:
                    return redirect(url_for("login"))

            return render_template('register.html', error=error)
            
        
        return render_template("register.html")

    # Deposit Page
    @app.route('/deposit', methods=('POST',))
    def deposit():
        db = get_db()

        user = db.execute(
                'SELECT * FROM user WHERE id = ?', (session['user_id'],)
            ).fetchone()

        user_balance = float(request.form['amount']) + user['balance']

        db.execute(
            'UPDATE user SET balance = ? where id = ?',
            (user_balance, session['user_id'])
        )
        db.commit()

        return render_template('auth.html', username=user['username'], balance=user_balance)

    # Purchase stock page
    # TODO: clear up logic between sell and purchase
    @app.route('/purchase', methods=('POST',))
    def purchase_stock():
        ticker = request.form['ticker']
        share_amount = float(request.form['shares'])
        stock_price = Get_Current_Stock_Price(str(ticker))

        db = get_db()

        user = db.execute(
            'SELECT * from user WHERE id = ?', (session['user_id'],)
        ).fetchone()

        user_balance = user['balance']

        if(request.form['action'] == 'purchase'):
            new_balance = user_balance - (stock_price * share_amount)
            
            # User cannot purchase stock (insufficient funds)
            if(new_balance < 0):
                return render_template('auth.html', username=user['username'], error='Insufficient funds.', balance=user['balance'])

            db.execute(
                'UPDATE user SET balance = ? where id = ?',
                (new_balance, session['user_id'])
            )
            db.commit()


            db.execute(
                'INSERT INTO user_stocks (user_id, shares, purchase_price, stock_symbol) VALUES (?, ?, ?, ?)',
                (session['user_id'], share_amount, stock_price, ticker)
            )
            db.commit()

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
                            db.execute(
                                'UPDATE user_stocks SET shares = ? where id = ?',
                                (remaining_shares, position['id'])
                            )
                            db.commit()

                        # delete remaining positions.
                        for position in potential_delete_shares:
                            db.execute(
                                'DELETE FROM user_stocks WHERE id = ?',
                                (position['id'],)
                            )
                            db.commit()

                    potential_delete_shares.append(position)

            if(successful_deletion):
                new_balance = (share_amount * stock_price) + user['balance']
                db.execute(
                    'UPDATE user SET balance = ? where id = ?',
                    (new_balance, user['id'])
                )
                db.commit()

                user_positions = get_user_positions(user['id'])
                return render_template('auth.html', username=user['username'], balance=new_balance, positions=user_positions)
            else:
                user_positions = get_user_positions(user['id'])
                return render_template('auth.html', username=user['username'], balance=user['balance'], error='Insufficient shares.', positions=user_positions)


    return app

# TODO: move functions to seperate file later. 
def get_user_positions(user_id: int):
    db = get_db()

    positions = db.execute(
        'SELECT * FROM user_stocks WHERE user_id = ? ', (user_id,)
    ).fetchall()

    cleaned_positions = []

    # each position is a row within user_stocks table defined in schema.sql
    for position in positions:
        cleaned_positions.append({'purchase_price':position['purchase_price'],
                                  'stock_symbol':position['stock_symbol'],
                                  'shares':position['shares'],
                                  'id':position['id']
                                  })

    return cleaned_positions