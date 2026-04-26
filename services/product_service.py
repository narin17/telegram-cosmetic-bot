from database.db import get_all_products_db, get_product_by_id_db, add_product_db, delete_product_db

async def get_all_products() -> list:
    """Return a list of all available products from the database."""
    return await get_all_products_db()

async def get_product_by_id(product_id: int) -> dict | None:
    """Retrieve a single product by its ID from the database."""
    return await get_product_by_id_db(product_id)

async def add_product(name: str, price: float):
    """Add a new product to the database."""
    await add_product_db(name, price)

async def delete_product(product_id: int):
    """Delete a product from the database."""
    await delete_product_db(product_id)
