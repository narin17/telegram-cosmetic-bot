from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from database.db import get_all_orders
from bot.config import ADMIN_ID
from services.product_service import get_product_by_id, add_product, delete_product, get_all_products

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(Command("allorders"))
async def cmd_allorders(message: Message):
    """Admin command to list all orders in the system."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ You don't have permission to use this command.")
        return

    orders = await get_all_orders()
    
    if not orders:
        await message.answer("There are no orders in the database.")
        return
        
    text = "📊 **All Orders:**\n\n"
    for order in orders:
        product = await get_product_by_id(order['product_id'])
        product_name = product['name'] if product else "Unknown"
        text += (
            f"ID: {order['id']} | User: {order['user_id']} | "
            f"Product: {product_name} | Status: {order['status']}\n"
        )
        
    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            await message.answer(text[x:x+4000], parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

@router.message(Command("addproduct"))
async def cmd_addproduct(message: Message, command: CommandObject):
    """Admin command to add a product: /addproduct Name - Price"""
    if not is_admin(message.from_user.id):
        return

    if not command.args or "-" not in command.args:
        await message.answer("Usage: `/addproduct Product Name - 9.99`", parse_mode="Markdown")
        return
        
    try:
        name_part, price_part = command.args.split("-")
        name = name_part.strip()
        price = float(price_part.strip())
        
        await add_product(name, price)
        await message.answer(f"✅ Product **{name}** added successfully with price **${price:.2f}**!", parse_mode="Markdown")
    except ValueError:
        await message.answer("❌ Invalid price format. Please use a number (e.g. 9.99)")

@router.message(Command("delproduct"))
async def cmd_delproduct(message: Message, command: CommandObject):
    """Admin command to delete a product: /delproduct ID"""
    if not is_admin(message.from_user.id):
        return

    if not command.args:
        await message.answer("Usage: `/delproduct <product_id>`", parse_mode="Markdown")
        return
        
    try:
        product_id = int(command.args.strip())
        product = await get_product_by_id(product_id)
        if not product:
            await message.answer("❌ Product not found.")
            return
            
        await delete_product(product_id)
        await message.answer(f"✅ Product **{product['name']}** deleted successfully!")
    except ValueError:
        await message.answer("❌ Invalid ID format. Must be an integer.")

@router.message(Command("allproducts"))
async def cmd_allproducts(message: Message):
    """Admin command to list all products with their IDs."""
    if not is_admin(message.from_user.id):
        return
        
    products = await get_all_products()
    if not products:
        await message.answer("No products found.")
        return
        
    text = "📋 **All Products:**\n\n"
    for p in products:
        text += f"ID: `{p['id']}` | Name: {p['name']} | Price: ${p['price']:.2f}\n"
        
    await message.answer(text, parse_mode="Markdown")
