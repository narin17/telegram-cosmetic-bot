import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from bot.config import BOT_TOKEN
from database.db import init_db
from handlers import user_handlers, admin_handlers
from services.product_service import get_all_products

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def get_products_api(request):
    """API endpoint for WebApp to fetch products."""
    products = await get_all_products()
    return web.json_response([dict(p) for p in products])

async def serve_index(request):
    """Serve the WebApp HTML file."""
    return web.FileResponse('webapp/index.html')

async def on_startup(app):
    """Start polling in the background when the web server starts."""
    asyncio.create_task(dp.start_polling(bot))

async def init_web_app():
    """Initialize aiohttp web server."""
    app = web.Application()
    app.router.add_get('/api/products', get_products_api)
    app.router.add_get('/', serve_index)
    app.on_startup.append(on_startup)
    return app

def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logging.error("BOT_TOKEN is not set correctly in environment variables!")
        return

    # Create event loop
    loop = asyncio.get_event_loop()
    
    # Initialize DB synchronously wrapping
    loop.run_until_complete(init_db())

    # Include routers
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    # Start web app
    app = loop.run_until_complete(init_web_app())
    logging.info("Starting Web App on http://0.0.0.0:8080")
    web.run_app(app, host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
