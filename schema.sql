CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  balance REAL DEFAULT 0.0
);

CREATE TABLE user_stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    shares INTEGER,
    purchase_price REAL,
    stock_symbol TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
