import os
from datetime import datetime, timedelta
import sqlite3

# Determine paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'data'))
DB_PATH = os.path.join(DATA_DIR, 'database.db')

def init_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL,
            purchase_date TEXT NOT NULL,
            is_final_sale BOOLEAN NOT NULL,
            FOREIGN KEY(user_id) REFERENCES Users(id)
        )
    ''')

    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM Users')
    if cursor.fetchone()[0] > 0:
        print("Database already initialized with data.")
        conn.close()
        return

    # Insert Users
    users_data = [
        ('Alice Smith', 'alice@example.com'),
        ('Bob Jones', 'bob@example.com'),
        ('Charlie Brown', 'charlie@example.com'),
        ('Diana Prince', 'diana@example.com'),
        ('Evan Wright', 'evan@example.com'),
        ('Shiva', 'shiva@mail.com'),
        ('Krishna', 'krishna@mail.com')
    ]
    cursor.executemany('INSERT INTO Users (name, email) VALUES (?, ?)', users_data)

    # Insert Orders
    now = datetime.now()
    orders_data = [
        (1, 'Wireless Mouse', 25.99, 'delivered', (now - timedelta(days=5)).isoformat(), False),
        (6, 'damroo', 12.00, 'delivered', (now - timedelta(days=5)).isoformat(), False),
        (7, 'flute', 50.00, 'delivered', (now - timedelta(days=5)).isoformat(), False),
        (1, 'Mechanical Keyboard', 120.00, 'delivered', (now - timedelta(days=40)).isoformat(), False), # Over 30 days
        (2, 'Gaming Monitor', 600.00, 'delivered', (now - timedelta(days=40)).isoformat(), False), # Over $500
        (2, 'HDMI Cable', 15.50, 'delivered', (now - timedelta(days=2)).isoformat(), False),
        (3, 'Designer Sunglasses', 150.00, 'delivered', (now - timedelta(days=12)).isoformat(), True), # Final Sale
        (3, 'T-Shirt', 20.00, 'delivered', (now - timedelta(days=1)).isoformat(), False),
        (4, 'Laptop Stand', 45.00, 'delivered', (now - timedelta(days=15)).isoformat(), False),
        (4, 'USB-C Hub', 35.00, 'delivered', (now - timedelta(days=35)).isoformat(), False), # Over 30 days
        (4, 'External Hard Drive', 80.00, 'delivered', (now - timedelta(days=5)).isoformat(), False),
        (5, 'Smart Watch', 250.00, 'delivered', (now - timedelta(days=8)).isoformat(), False),
        (5, 'Watch Band', 30.00, 'delivered', (now - timedelta(days=8)).isoformat(), False),
        (1, 'Webcam', 75.00, 'delivered', (now - timedelta(days=20)).isoformat(), False),
        (2, 'Microphone', 110.00, 'delivered', (now - timedelta(days=4)).isoformat(), False),
        (3, 'Clearance Sneakers', 60.00, 'delivered', (now - timedelta(days=14)).isoformat(), True), # Final Sale
        (5, 'Premium Laptop', 1200.00, 'delivered', (now - timedelta(days=6)).isoformat(), False) # Over $500
    ]
    cursor.executemany('''
        INSERT INTO Orders (user_id, item_name, price, status, purchase_date, is_final_sale)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', orders_data)

    conn.commit()
    conn.close()
    print("Database initialized and populated with mock data.")

if __name__ == '__main__':
    init_db()
