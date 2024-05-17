from flask import Flask, render_template
from . import auth
from . import db
from . import stocks
import os

def create_app(test_config=None):
    # create application and setup configuration. 
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'StockTrends.sqlite')
    )
    
    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # init database
    db.init_app(app)

    # Home Page. 
    @app.route('/')
    def home():
        return render_template('base.html')

    # Init auth blueprint
    app.register_blueprint(auth.bp)

    # Init stock blueprint
    app.register_blueprint(stocks.bp)

    return app