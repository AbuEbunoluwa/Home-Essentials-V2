"""
Masterpiece Home Essentials — FastAPI Backend
Database: PostgreSQL (via psycopg2)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
import psycopg2.extras
import os

app = FastAPI(
    title="Masterpiece Home Essentials API",
    description="E-commerce API for home essential products",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Data Models ───────────────────────────────────────────────────────────────
class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int

class Order(BaseModel):
    product_ids: List[int]
    customer_email: str

class OrderResponse(BaseModel):
    status: str
    total: float
    message: str

# ── Database ──────────────────────────────────────────────────────────────────
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "homeessentials"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def init_db():
    """Create tables and seed products if empty."""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_email TEXT NOT NULL,
            product_ids TEXT NOT NULL,
            total NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()["count"] == 0:
        seed_data = [
            ("Sectional Sofa",     "Living Room", 899.99, 5),
            ("Coffee Table",       "Living Room", 149.99, 12),
            ("Memory Foam Mattress","Bedroom",    499.00, 10),
            ("Nightstand",         "Bedroom",      75.50, 20),
            ("Air Fryer",          "Kitchen",     120.00, 15),
            ("Knife Set",          "Kitchen",      45.00, 30),
            ("Steam Iron",         "Laundry",      35.00, 25),
            ("Tool Organizer",     "Garage",       60.00,  8),
            ("Toy Storage Bin",    "Kids Room",    25.00, 50),
            ("Vacuum Cleaner",     "Cleaning",    150.00, 10),
            ("Blender",            "Kitchen",      55.00, 20),
            ("Microwave",          "Kitchen",     200.00,  8),
            ("Bed Frame",          "Bedroom",     350.00,  6),
            ("Wardrobe",           "Bedroom",     450.00,  4),
            ("Dining Table",       "Living Room", 600.00,  5),
            ("Office Chair",       "Office",      250.00, 12),
            ("Bookshelf",          "Office",      120.00, 15),
            ("Curtains",           "Living Room",  45.00, 30),
            ("Wall Clock",         "Living Room",  35.00, 25),
            ("Dish Rack",          "Kitchen",      25.00, 40),
            ("Laundry Basket",     "Laundry",      20.00, 35),
            ("Bathroom Mirror",    "Bathroom",     80.00, 18),
            ("Towel Set",          "Bathroom",     30.00, 50),
            ("Floor Lamp",         "Living Room",  95.00, 14),
            ("Smart Doorbell",     "Security",    180.00,  9),
            ("Garden Hose",        "Garage",       40.00, 22),
            ("Kids Desk",          "Kids Room",   130.00, 11),
            ("Baby Monitor",       "Kids Room",    90.00, 16),
            ("Electric Kettle",    "Kitchen",      35.00, 28),
            ("Smart Thermostat",   "Security",    220.00,  7),
        ]
        c.executemany(
            "INSERT INTO products (name, category, price, stock) VALUES (%s,%s,%s,%s)",
            seed_data
        )

    conn.commit()
    conn.close()

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    try:
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"⚠ DB init failed: {e}")

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Welcome to Masterpiece Home Essentials API",
        "docs":    "/docs",
        "health":  "/health"
    }

@app.get("/health")
def health():
    try:
        conn = get_db()
        conn.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "database": db_status, "version": "1.0.0"}

@app.get("/products", response_model=List[Product])
def get_products(category: Optional[str] = None):
    """Get all products, optionally filtered by category."""
    conn = get_db()
    c = conn.cursor()
    if category:
        c.execute("SELECT * FROM products WHERE LOWER(category)=LOWER(%s) ORDER BY id", (category,))
    else:
        c.execute("SELECT * FROM products ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    """Get a single product by ID."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)

@app.get("/categories")
def get_categories():
    """Get all unique categories."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM products ORDER BY category")
    rows = c.fetchall()
    conn.close()
    return [r["category"] for r in rows]

@app.post("/checkout", response_model=OrderResponse)
def checkout(order: Order):
    """Process an order and reduce stock."""
    conn = get_db()
    c = conn.cursor()
    total = 0.0

    for pid in order.product_ids:
        c.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = c.fetchone()
        if not product:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        if product["stock"] <= 0:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Product '{product['name']}' is out of stock")
        total += float(product["price"])
        c.execute("UPDATE products SET stock=stock-1 WHERE id=%s", (pid,))

    import json
    c.execute(
        "INSERT INTO orders (customer_email, product_ids, total) VALUES (%s,%s,%s)",
        (order.customer_email, json.dumps(order.product_ids), round(total, 2))
    )
    conn.commit()
    conn.close()

    return {
        "status":  "Success",
        "total":   round(total, 2),
        "message": f"Order confirmed for {order.customer_email}!"
    }

@app.get("/orders")
def get_orders(email: Optional[str] = None):
    """Get all orders, optionally filtered by email."""
    conn = get_db()
    c = conn.cursor()
    if email:
        c.execute("SELECT * FROM orders WHERE customer_email=%s ORDER BY created_at DESC", (email,))
    else:
        c.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
