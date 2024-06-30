''' auth logic '''

import re
import sqlite3
from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from stock_trends.db import (
    get_user_positions,
    get_user_id,
    get_user,
    register_user,
    update_balance,
    register_user_stock_purchase,
    update_user_stock_purchase,
    delete_user_stock_purchase)
from stock_trends.api_tiingo import get_current_stock_price

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Login Page.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    ''' clarify docstring'''
    if request.method == 'POST':
        # login logic
        username = request.form['username']
        password = request.form['password']
        error = None

        user_id = get_user_id(username)[0]
        user = get_user(user_id)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # No error - user can be logged in.
        if error is None:
            session.clear()
            session['user_id'] = user['id']

            balance = user['balance']
            positions = get_user_positions(session['user_id'])
            return render_template(
                "auth/authorized.html",
                balance=balance,
                username=username,
                positions=positions)

        return render_template("auth/login.html", error=error)

    # simply return page.
    return render_template('auth/login.html')

# Password Validation logic min: (8 chars, 1-upper, 1-lower, and 1 number)


def valid_password(password):
    ''' clarify docstring'''
    # Define the regex pattern
    password_pattern = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$')

    # Check if the password matches the pattern
    return password_pattern.match(password)

# Register Page.
@bp.route('/register', methods=('GET', 'POST'))
def regsiter():
    ''' clarify docstring'''
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
            if not valid_password(password):
                return render_template(
                    'auth/register.html',
                    error="Please enter a valid password.")
            try:
                register_user(username, password)
            except sqlite3.IntegrityError:
                error = f"User {username} is already registered, please select another username."
            else:
                return redirect(url_for("auth.login"))

        return render_template('auth/register.html', error=error)

    return render_template("auth/register.html")

# Logout Page - redirect to main page.


@bp.route('/logout')
def logout():
    ''' clarify docstring'''
    session.clear()
    return redirect('/')

# Paper Trading Page


@bp.route('/PaperTrade')
def paper_trade():
    ''' clarify docstring'''
    return render_template(
        "auth/login.html",
        error="Please sign in to paper trade.")

# Deposit Logic


@bp.route('/deposit', methods=('POST',))
def deposit():
    ''' clarify docstring'''
    user = get_user(session['user_id'])
    user_balance = float(request.form['amount']) + user['balance']
    update_balance(session['user_id'], user_balance)

    return render_template(
        'auth/authorized.html',
        username=user['username'],
        balance=user_balance)


# Purchase / Selling Logic:
@bp.route('/purchase', methods=('POST',))
def stock_options():
    ''' clarify docstring'''
    ticker = request.form['ticker']
    share_amount = float(request.form['shares'])
    stock_price = get_current_stock_price(str(ticker))
    user = get_user(session['user_id'])
    user_balance = user['balance']

    if request.form['action'] == 'purchase':
        new_balance = user_balance - (stock_price * share_amount)

        # User cannot purchase stock (insufficient funds)
        if new_balance < 0:
            return render_template(
                'auth/authorized.html',
                username=user['username'],
                error='Insufficient funds.',
                balance=user['balance'])

        update_balance(session['user_id'], new_balance)
        register_user_stock_purchase(
            session['user_id'],
            share_amount,
            stock_price,
            ticker)

        positions = get_user_positions(session['user_id'])
        return render_template(
            'auth/authorized.html',
            username=user['username'],
            balance=new_balance,
            positions=positions)

    # need to check if they have enough shares.
    user_positions = get_user_positions(session['user_id'])
    total_shares = 0
    potential_delete_shares = []
    successful_deletion = False

    # 1 position: 100 shares - sell 100 shares
    for position in user_positions:
        if position['stock_symbol'] == ticker:
            total_shares += position['shares']
            potential_delete_shares.append(position)

            # check to see if there is enough shares
            if total_shares >= share_amount:
                remaining_shares = total_shares - share_amount
                print(remaining_shares)
                successful_deletion = True

                # if remaining shares left, update count for last position
                # and remove from deleting.
                if remaining_shares != 0:
                    update_user_stock_purchase(
                        position['id'], remaining_shares)
                    del potential_delete_shares[-1]

                # delete all positions
                for position in potential_delete_shares:
                    delete_user_stock_purchase(position['id'])

        if successful_deletion:
            new_balance = (share_amount * stock_price) + user['balance']
            update_balance(user['id'], new_balance)

            user_positions = get_user_positions(user['id'])
            print(user_positions)
            return render_template(
                'auth/authorized.html',
                username=user['username'],
                balance=new_balance,
                positions=user_positions)

        user_positions = get_user_positions(user['id'])
        return render_template(
            'auth/authorized.html',
            username=user['username'],
            balance=user['balance'],
            error='Insufficient shares.',
            positions=user_positions)
