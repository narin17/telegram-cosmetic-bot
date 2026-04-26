import asyncio
from database.db import DB_NAME
import aiosqlite

async def seed_cosmetics():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DROP TABLE IF EXISTS products")
        await db.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        
        # 12 Beautiful Cosmetic Products mapped directly from your image reference
        cosmetics = [
            ("SilkSculpt Serum", 35.00, "Skin Care"),
            ("SilkSkin Serum", 48.00, "Skin Care"),
            ("Argan Glow Hair Oil", 63.00, "Hair Care"),
            ("Nephrolepis Body Care", 45.00, "Body Care"),
            ("Smooth Foundation", 20.00, "Makeup"),
            ("Smooth Body Cream", 30.00, "Body Care"),
            ("AquaAura Wellness", 30.00, "Body Care"),
            ("Velvet Rose Lipstick", 10.00, "Makeup"),
            ("Herbal Haven Soap", 10.00, "Body Care"),
            ("Essence Body Gel", 30.00, "Body Care"),
            ("HydraLuxe Serum", 20.00, "Skin Care"),
            ("OceanMist Moisturizer", 20.00, "Skin Care")
        ]
        
        await db.executemany(
            "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
            cosmetics
        )
        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed_cosmetics())
