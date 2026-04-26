import aiosqlite
import logging

DB_NAME = "database/bot.db"

async def init_db():
    """Initialize the SQLite database and create tables if they do not exist."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                price REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL DEFAULT 'Skin Care'
            )
        ''')
        
        # Seed products if empty
        cursor = await db.execute("SELECT COUNT(*) FROM products")
        if (await cursor.fetchone())[0] == 0:
            await db.executemany(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                [("Basic Subscription", 9.99), ("Pro Subscription", 19.99), ("Lifetime Access", 99.99)]
            )
            logging.info("Inserted default products into database.")
            
        await db.commit()
        logging.info("Database initialized.")

# --- Orders ---

async def create_order(user_id: int, product_id: int, price: float) -> int:
    """Create a new order in the database and return its ID."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, product_id, price, status) VALUES (?, ?, ?, 'PENDING')",
            (user_id, product_id, price)
        )
        await db.commit()
        return cursor.lastrowid

async def update_order_status(order_id: int, status: str):
    """Update the status of an existing order."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
        await db.commit()

async def get_user_orders(user_id: int) -> list:
    """Retrieve all orders for a specific user."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,))
        return await cursor.fetchall()

async def get_all_orders() -> list:
    """Retrieve all orders (Admin only)."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders ORDER BY id DESC")
        return await cursor.fetchall()

async def get_order_by_id(order_id: int) -> dict | None:
    """Retrieve a single order by ID."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

# --- Products ---

async def get_all_products_db() -> list:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products")
        return await cursor.fetchall()

async def get_product_by_id_db(product_id: int) -> dict | None:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def add_product_db(name: str, price: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        await db.commit()

async def delete_product_db(product_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()
