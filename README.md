#### StockTrends
* Stock data app created with Flask, Python, SQLite, Tiingo and AlphaVantage API.

## Setup Instructions

# 1. Clone the Repository

```bash
git clone https://github.com/NicholasTanz/StockTrends/
```

# 2. Set API Keys
-  create a file named `config.py` in the stockTrends repo.
-  create two variables as follows in `config.py`:
```python
-  AlphaVantage_API_KEY = ["your alphaVantage Key"](https://www.alphavantage.co/)
-  Tiingo_API_KEY = ["your Tiingo Key"](https://www.tiingo.com/kb/article/where-to-find-your-tiingo-api-token/)
```

# 2. Initialize the Database

Navigate to the project directory and run the following:

```bash
# Run the command below in the parent directory of the cloned repo.
# (i.e. if the repo location is in user/myUser/StockTrends, you would run this command in user/myUser). 
flask --app StockTrends init-db
```

# 3. Start the Application

Now start the application by running the following command:

```bash
# again, in the parent directory. 
flask --app StockTrends run
```

You should now be able to access it at `http://localhost:5000`.
