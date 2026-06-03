import unittest
from unittest.mock import patch
import sqlite3
import json
from datetime import datetime, timedelta
import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.tools import process_refund

class ConnectionWrapper:
    """Wraps a sqlite3 connection to prevent it from being closed by code under test."""
    def __init__(self, conn):
        self._conn = conn
    def __getattr__(self, name):
        return getattr(self._conn, name)
    def close(self):
        # Do not close the underlying connection during tests
        pass

class TestRefundRules(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create Tables
        self.cursor.execute('''
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE Orders (
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
        
        # Insert test users
        self.cursor.execute("INSERT INTO Users (name, email) VALUES ('Test User', 'test@example.com')")
        
        # Insert test orders
        now = datetime.now()
        
        # Order 1: Valid for refund (under $500, under 30 days, not final sale)
        self.cursor.execute('''
            INSERT INTO Orders (id, user_id, item_name, price, status, purchase_date, is_final_sale)
            VALUES (1, 1, 'Valid Item', 50.00, 'delivered', ?, 0)
        ''', ((now - timedelta(days=10)).isoformat(),))
        
        # Order 2: Price over $500 (Rule 3 violation)
        self.cursor.execute('''
            INSERT INTO Orders (id, user_id, item_name, price, status, purchase_date, is_final_sale)
            VALUES (2, 1, 'Expensive Item', 600.00, 'delivered', ?, 0)
        ''', ((now - timedelta(days=10)).isoformat(),))
        
        # Order 3: Over 30 days old (Rule 1 violation)
        self.cursor.execute('''
            INSERT INTO Orders (id, user_id, item_name, price, status, purchase_date, is_final_sale)
            VALUES (3, 1, 'Old Item', 50.00, 'delivered', ?, 0)
        ''', ((now - timedelta(days=40)).isoformat(),))
        
        # Order 4: Final Sale (Rule 2 violation)
        self.cursor.execute('''
            INSERT INTO Orders (id, user_id, item_name, price, status, purchase_date, is_final_sale)
            VALUES (4, 1, 'Final Sale Item', 50.00, 'delivered', ?, 1)
        ''', ((now - timedelta(days=10)).isoformat(),))
        
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    @patch('app.services.tools.get_db_connection')
    def test_refund_over_500_escalation(self, mock_get_db):
        mock_get_db.return_value = ConnectionWrapper(self.conn)
        
        response = json.loads(process_refund(2))
        self.assertIn("error", response)
        self.assertIn("SECURITY BLOCK: Order value exceeds $500", response["error"])

    @patch('app.services.tools.get_db_connection')
    def test_refund_over_30_days_denied(self, mock_get_db):
        mock_get_db.return_value = ConnectionWrapper(self.conn)
        
        response = json.loads(process_refund(3))
        self.assertIn("error", response)
        self.assertIn("SECURITY BLOCK: Order was placed more than 30 days ago", response["error"])

    @patch('app.services.tools.get_db_connection')
    def test_refund_final_sale_denied(self, mock_get_db):
        mock_get_db.return_value = ConnectionWrapper(self.conn)
        
        response = json.loads(process_refund(4))
        self.assertIn("error", response)
        self.assertIn("SECURITY BLOCK: Item is Final Sale", response["error"])

    @patch('app.services.tools.get_db_connection')
    def test_valid_refund_succeeds(self, mock_get_db):
        mock_get_db.return_value = ConnectionWrapper(self.conn)
        
        response = json.loads(process_refund(1))
        self.assertIn("success", response)
        
        # Verify status updated to refunded in db
        self.cursor.execute("SELECT status FROM Orders WHERE id = 1")
        status = self.cursor.fetchone()['status']
        self.assertEqual(status, 'refunded')

if __name__ == '__main__':
    unittest.main()
