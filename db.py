import sqlite3
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
    
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_user_positions(user_id: int):
    """ gets all of the user's current stock positions. 

    Args:
        user_id: id from user table
    
    Returns:
        Dict: dictonary with the following keys.
            * purchase_price (float)
            * stock_symbol (str)
            * shares (int)
            * id (int)
    """ 
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

def get_userID(username: str):
    db = get_db()

    return db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone()

def get_user(user_id: int):
    db = get_db()

    return db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()


def register_user(username: str, password:str) -> None:
    db = get_db()

    db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    db.commit()

def update_balance(user_id: int, new_balance: float):
    """ updates a user's balance. 

    Args:
        user_id: id from user table
        new_balance: new balance.
    """ 
    db = get_db()
    db.execute(
            'UPDATE user SET balance = ? where id = ?',
            (new_balance, user_id)
        )
    
    db.commit()

def register_user_stock_purchase(user_id: int, share_amount: int, stock_price: float, ticker: str):
    """ creates an entry for a stock purchase by a user in the SQLite DB. 

    Args:
        user_id: id from user table
        share_amount: amount of shares purchased.
        stock_price: price of stock when bought.
        ticker: stock bought
    """
    db = get_db()

    db.execute(
        'INSERT INTO user_stocks (user_id, shares, purchase_price, stock_symbol) VALUES (?, ?, ?, ?)',
        (user_id, share_amount, stock_price, ticker)
    )
    db.commit()

def update_user_stock_purchase(stock_purchase_id:int, remaining_shares: int):
    """ updates a user's stock purchase.  

    Args:
        stock_purchase_id.
        remaining_shares: shares left after selling a stock. 

    """ 

    db = get_db()
    
    db.execute(
        'UPDATE user_stocks SET shares = ? where id = ?',
        (remaining_shares, stock_purchase_id)
    )
    db.commit()

def delete_user_stock_purchase(stock_purchase_id:int):
    """ Deletes a user's stock purchase.  

    Args:
        stock_purchase_id.

    """ 
    db = get_db()
    
    db.execute(
        'DELETE FROM user_stocks WHERE id = ?',
        (stock_purchase_id,)
    )
    db.commit()