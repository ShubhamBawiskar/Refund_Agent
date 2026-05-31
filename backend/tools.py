import json
import os
from datetime import datetime, timedelta
from database import get_db_connection

POLICY_CACHE = None

def query_order(customer_email: str, order_id: int) -> str:
    """Queries an order by customer email and order ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT O.*, U.email, U.name
        FROM Orders O
        JOIN Users U ON O.user_id = U.id
        WHERE U.email = ? AND O.id = ?
    ''', (customer_email, order_id))
    order = cursor.fetchone()
    conn.close()
    
    if order:
        order_dict = dict(order)
        try:
            purchase_date = datetime.fromisoformat(order_dict['purchase_date'])
            order_dict['days_since_purchase'] = (datetime.now() - purchase_date).days
        except Exception:
            pass
        return json.dumps(order_dict)
    return json.dumps({"error": "Order not found or email does not match."})

def read_policy(query: str = "") -> str:
    """Reads the refund policy document from cache or disk."""
    global POLICY_CACHE
    if POLICY_CACHE is not None:
        return POLICY_CACHE

    policy_path = os.path.join(os.path.dirname(__file__), 'refund_policy.md')
    try:
        with open(policy_path, 'r') as f:
            POLICY_CACHE = f.read()
            return POLICY_CACHE
    except FileNotFoundError:
        return "Error: Refund policy document not found."

def process_refund(order_id: int) -> str:
    """Processes a refund. Includes hardcoded security checks."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return json.dumps({"error": "Order not found."})
    
    # Dual-Layer Security Constraint (CRITICAL)
    # Check Rule 1: No refunds after 30 days
    try:
        purchase_date = datetime.fromisoformat(order['purchase_date'])
        if datetime.now() - purchase_date > timedelta(days=30):
            conn.close()
            return json.dumps({"error": "SECURITY BLOCK: Order was placed more than 30 days ago. Refund denied."})
    except Exception as e:
        pass  # Fallback if date format is invalid

    # Check Rule 2: Final sale items are non-refundable
    if order['is_final_sale']:
        conn.close()
        return json.dumps({"error": "SECURITY BLOCK: Item is Final Sale. Refund denied."})
        
    # Check Rule 3: Refunds over $500 must be escalated
    if order['price'] > 500:
        conn.close()
        return json.dumps({"error": "SECURITY BLOCK: Order value exceeds $500. Escalation to human agent required."})
        
    # Process the refund (simulate by updating status)
    if order['status'] == 'refunded':
        conn.close()
        return json.dumps({"error": "Order is already refunded."})
        
    cursor.execute('UPDATE Orders SET status = "refunded" WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    
    return json.dumps({"success": f"Order {order_id} has been successfully refunded."})

# OpenAI Tool Definitions Schema
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "query_order",
            "description": "Look up the details of a specific order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_email": {
                        "type": "string",
                        "description": "The email address of the customer"
                    },
                    "order_id": {
                        "type": "integer",
                        "description": "The ID of the order"
                    }
                },
                "required": ["customer_email", "order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_policy",
            "description": "Read the company's refund policy to check the rules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional specific topic to search for in the policy."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "Process a refund for a given order ID. Will fail if policy constraints are violated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The ID of the order to refund"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
]

# Map tool names to functions
AVAILABLE_TOOLS = {
    "query_order": query_order,
    "read_policy": read_policy,
    "process_refund": process_refund,
}
