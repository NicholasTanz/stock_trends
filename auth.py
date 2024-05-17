from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from StockTrends.db import (
     get_user_positions, get_userID, get_user, register_user, update_balance, register_user_stock_purchase, update_user_stock_purchase, delete_user_stock_purchase, get_db
)
from StockTrends.API_Tiingo import Get_Current_Stock_Price


# TODO: add feature to display past queries from "Stocks" option. 
# TODO: add password requirements (Ex: 8 chars, 1 upper, 1 num, 1 special.)

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Login Page. 
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # login logic
        username = request.form['username']
        password = request.form['password']
        db = get_db()
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
            return render_template("auth/authorized.html", balance=balance, username=username, positions=positions)

        return render_template("auth/login.html", error=error)

    # simply return page.
    return render_template('auth/login.html')

# Register Page. 
@bp.route('/register', methods=('GET', 'POST'))
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
            except:
                error = f"User {username} is already registered, please select another username."
            else:
                return redirect(url_for("auth.login"))

        return render_template('auth/register.html', error=error)
        
    
    return render_template("auth/register.html")

# Logout Page - redirect to main page.
@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Paper Trading Page
@bp.route('/PaperTrade')
def paper_trade():
    return render_template("auth/login.html", error="Please sign in to paper trade.")

# Deposit Logic
@bp.route('/deposit', methods=('POST',))
def deposit():
    user = get_user(session['user_id'])
    user_balance = float(request.form['amount']) + user['balance']
    update_balance(session['user_id'], user_balance)

    return render_template('auth/authorized.html', username=user['username'], balance=user_balance)


# Purchase / Selling Logic:
@bp.route('/purchase', methods=('POST',))
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
            return render_template('auth/authorized.html', username=user['username'], error='Insufficient funds.', balance=user['balance'])

        update_balance(session['user_id'], new_balance)
        register_user_stock_purchase(session['user_id'], share_amount, stock_price, ticker)


        positions = get_user_positions(session['user_id'])
        return render_template('auth/authorized.html', username=user['username'], balance=new_balance, positions=positions)

    else:
        # need to check if they have enough shares. 
        user_positions = get_user_positions(session['user_id'])
        total_shares = 0
        potential_delete_shares = []
        successful_deletion = False

        print(user_positions)
        # 1 position: 100 shares - sell 100 shares
        for position in user_positions:
            if position['stock_symbol'] == ticker:
                total_shares += position['shares']
                potential_delete_shares.append(position)
                
                # check to see if there is enough shares
                if(total_shares >= share_amount):
                    remaining_shares = (total_shares - share_amount)
                    print(remaining_shares)
                    successful_deletion = True

                    # if remaining shares left, update count for last position and remove from deleting.
                    if(remaining_shares != 0):
                        update_user_stock_purchase(position['id'], remaining_shares)
                        del potential_delete_shares[-1] 
                    
                    # delete all positions
                    for position in potential_delete_shares:
                        delete_user_stock_purchase(position['id'])

        if(successful_deletion):
            new_balance = (share_amount * stock_price) + user['balance']
            update_balance(user['id'], new_balance)

            user_positions = get_user_positions(user['id'])
            return render_template('auth/authorized.html', username=user['username'], balance=new_balance, positions=user_positions)
        else:
            user_positions = get_user_positions(user['id'])
            return render_template('auth/authorized.html', username=user['username'], balance=user['balance'], error='Insufficient shares.', positions=user_positions)


