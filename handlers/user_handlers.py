from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, LabeledPrice, PreCheckoutQuery,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)
import json

from services.product_service import get_all_products, get_product_by_id
from database.db import create_order, get_user_orders, update_order_status, get_order_by_id
from bot.config import PAYMENT_TOKEN, WEBAPP_URL

router = Router()

def get_webapp_keyboard():
    """Returns a ReplyKeyboard with a WebApp button."""
    if WEBAPP_URL:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="💄 Open Glamour Beauty", web_app=WebAppInfo(url=WEBAPP_URL))]],
            resize_keyboard=True
        )
    return None

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Standard Products", callback_data="show_products")],
        [InlineKeyboardButton(text="📦 My Orders", callback_data="my_orders")]
    ])

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle the /start command."""
    welcome_text = (
        f"Hello, {message.from_user.first_name}! 👋\n\n"
        "Welcome to ✨ **Glamour Beauty** ✨.\n\n"
        "You can browse our mini-app using the button below (if configured), or use the standard menu:"
    )
    webapp_kb = get_webapp_keyboard()
    if webapp_kb:
        await message.answer(welcome_text, reply_markup=webapp_kb)
        await message.answer("Or use standard options:", reply_markup=get_main_menu())
    else:
        await message.answer(welcome_text, reply_markup=get_main_menu())

@router.message(F.web_app_data)
async def process_web_app_data(message: Message, bot: Bot):
    """Handles checkout data sent back from the Web App."""
    if not PAYMENT_TOKEN:
        await message.answer("Payment is not configured by admin yet!")
        return

    data = message.web_app_data.data
    try:
        cart_items = json.loads(data)
    except Exception:
        await message.answer("Failed to process cart data.")
        return
        
    if not cart_items:
        await message.answer("Your cart is empty.")
        return

    total_cents = 0
    order_details = ""
    
    for item in cart_items:
        p_id = item['id']
        qty = item['qty']
        product = await get_product_by_id(p_id)
        if product:
            item_price_cents = int(product['price'] * 100) * qty
            total_cents += item_price_cents
            order_details += f"- {product['name']} x{qty}\n"

    # Create order in DB (product_id=0 for multi-item cart)
    user_id = message.from_user.id
    order_id = await create_order(user_id, 0, total_cents / 100.0)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay with Credit Card", callback_data=f"pay_card_{order_id}")],
        [InlineKeyboardButton(text="📱 Pay with QR Code", callback_data=f"pay_qr_{order_id}")]
    ])
    
    text = (
        f"✅ **Order Created!** (Order #{order_id})\n\n"
        f"**Your Cart:**\n{order_details}\n"
        f"**Total Due:** ${total_cents / 100:.2f}\n\n"
        "Please choose your preferred payment method below:"
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data.startswith("pay_card_"))
async def process_pay_card(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    order = await get_order_by_id(order_id)
    if not order:
        await callback.answer("Order not found.", show_alert=True)
        return
        
    price_cents = int(order['price'] * 100)
    prices = [LabeledPrice(label=f"Order #{order_id}", amount=price_cents)]
    
    await callback.message.delete()
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Glamour Beauty",
        description=f"Payment for Order #{order_id}",
        payload=str(order_id),
        provider_token=PAYMENT_TOKEN,
        currency="USD",
        prices=prices,
        start_parameter=f"order_{order_id}"
    )

@router.callback_query(F.data.startswith("pay_qr_"))
async def process_pay_qr(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    order = await get_order_by_id(order_id)
    if not order:
        await callback.answer("Order not found.", show_alert=True)
        return
        
    # Generate a QR code using a free external API. 
    # This encodes the payment data (can be replaced with a real crypto wallet or bank payload)
    payment_data = f"GlamourBeauty_Order_{order_id}_Total_{order['price']}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={payment_data}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I have transferred the money", callback_data=f"confirm_qr_{order_id}")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="back_to_main")]
    ])
    
    await callback.message.delete()
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=qr_url,
        caption=(
            f"📱 **QR Code Payment**\n\n"
            f"**Order:** #{order_id}\n"
            f"**Amount Due:** ${order['price']:.2f}\n\n"
            "Please scan this QR code with your banking app or crypto wallet to pay. "
            "Once you have successfully transferred the funds, click the confirmation button below."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("confirm_qr_"))
async def process_confirm_qr(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    # Update order status to a specific QR paid status
    await update_order_status(order_id, "PAID (QR Code)")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Main Menu", callback_data="back_to_main")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(
        text=(
            f"🎉 **Thank you!**\n\n"
            f"Your payment for Order #{order_id} has been marked for review.\n"
            "We will verify your transfer and process your cosmetics shortly."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# --- STANDARD HANDLERS ---

@router.callback_query(F.data == "show_products")
async def process_show_products(callback: CallbackQuery):
    products = await get_all_products()
    keyboard = []
    
    for product in products:
        btn_text = f"{product['name']} - ${product['price']:.2f}"
        cb_data = f"buy_{product['id']}"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=cb_data)])
        
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")])
    
    await callback.message.edit_text(
        "Here are our available products:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data.startswith("buy_"))
async def process_buy_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = await get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return

    # Updated standard flow to also use the new dual-payment routing
    user_id = callback.from_user.id
    order_id = await create_order(user_id, product_id, product['price'])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay with Credit Card", callback_data=f"pay_card_{order_id}")],
        [InlineKeyboardButton(text="📱 Pay with QR Code", callback_data=f"pay_qr_{order_id}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="show_products")]
    ])
    
    text = (
        f"You selected: **{product['name']}**\n"
        f"Price: **${product['price']:.2f}**\n\n"
        "How would you like to pay?"
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment_info = message.successful_payment
    order_id = int(payment_info.invoice_payload)
    
    await update_order_status(order_id, "PAID (Credit Card)")
    
    text = (
        f"🎉 **Payment Successful!**\n\n"
        f"Your order #{order_id} has been fully paid.\n"
        f"Total Charge: {payment_info.total_amount / 100:.2f} {payment_info.currency}\n"
        "Thank you for shopping at Glamour Beauty!"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu())

@router.callback_query(F.data == "my_orders")
async def process_my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders = await get_user_orders(user_id)
    
    if not orders:
        text = "You don't have any orders yet."
    else:
        text = "📦 **Your Orders:**\n\n"
        for order in orders:
            if order['product_id'] == 0:
                product_name = "Shopping Cart"
            else:
                product = await get_product_by_id(order['product_id'])
                product_name = product['name'] if product else "Unknown"
            
            text += f"• Order #{order['id']} | {product_name} | ${order['price']:.2f} | Status: {order['status']}\n"
            
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback: CallbackQuery):
    welcome_text = (
        f"Hello, {callback.from_user.first_name}! 👋\n\n"
        "Welcome back to the main menu. Please choose an option:"
    )
    await callback.message.edit_text(welcome_text, reply_markup=get_main_menu())
