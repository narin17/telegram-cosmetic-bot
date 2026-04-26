# ✨ Glamour Beauty - Telegram Mini App E-Commerce Bot

A production-ready, highly aesthetic Telegram Mini App and Bot built with Python, `aiogram` v3, `aiohttp`, and modern web technologies. This project transforms a standard Telegram bot into a fully functional, mobile-optimized cosmetic web store seamlessly integrated into the Telegram chat interface.

## 🌟 Key Features

- 🛍️ **Telegram Mini App Web Store**: A beautiful, modern, native-feeling UI for browsing cosmetics. Uses Telegram's native APIs (`tg.MainButton`, `tg.HapticFeedback`, dynamic theming).
- 🛒 **Dynamic Shopping Cart**: Users can add multiple items to their cart inside the web app and checkout with a single click.
- 💳 **Dual-Payment System**: After checkout, users can securely pay using:
  - **Native Telegram Invoices** (Credit Card processing via Stripe/others).
  - **Dynamic QR Codes** (Generates a custom QR code for external banking or crypto transfers).
- 🗄️ **Database-Driven**: Uses SQLite to manage a persistent catalog of products and user order histories.
- 🛠️ **Admin Controls**: Secure Telegram commands (`/allorders`, `/addproduct`, `/delproduct`, `/allproducts`) allowing store owners to manage the shop entirely from within Telegram.

---

## 🔄 User Flow (How It Works)

1. **Start**: The user opens the bot and sends `/start`. They are greeted with a customized menu and a prominent "💄 Open Glamour Beauty" button.
2. **Browse**: Clicking the button opens the Web App overlay. The frontend (`webapp/index.html`) fetches live products from the bot's background `aiohttp` API endpoint.
3. **Cart & Checkout**: The user taps items to add them to their cart. The native Telegram "Main Button" appears at the bottom.
4. **Data Transmission**: When the user clicks checkout, the Web App securely transmits the cart payload (JSON) back to the Python bot.
5. **Payment Routing**: The bot registers the order in the database and asks the user how they want to pay (Credit Card or QR Code).
6. **Fulfillment**: Upon successful payment or manual QR verification, the order is updated to `PAID` in the database, and the user receives a digital receipt.

---

## 🚀 Step-by-Step Installation Guide

Follow these instructions to clone and run this project on your local machine or server.

### 1. Prerequisites
- Python 3.9 or higher installed.
- A Telegram Bot Token from [BotFather](https://t.me/BotFather).
- A Test Payment Provider Token from BotFather (e.g., Stripe Test, Tranzzo Test).

### 2. Clone the Repository
Open your terminal and clone the repository:
```bash
git clone https://github.com/narin17/telegram-cosmetic-bot.git
cd telegram-cosmetic-bot
```

### 3. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies:
```bash
# Create the virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate
# Activate it (Mac/Linux)
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Rename the template `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open the `.env` file in your code editor and fill in the values:
- `BOT_TOKEN`: Your bot token from BotFather.
- `ADMIN_ID`: Your personal Telegram User ID (used for admin commands).
- `PAYMENT_TOKEN`: Your Test Payment Token from BotFather.
- `WEBAPP_URL`: *(Leave blank for now, we will set this in Step 7)*.

### 6. Seed the Database
Populate your SQLite database with the default Cosmetic products by running the seed script:
```bash
python seed_cosmetics.py
```

### 7. Expose the Web App for Telegram (Local Testing)
Telegram requires all Web Apps to be hosted on a secure `https://` connection. To test locally, you need to expose your local port `8080`.
Open a **second terminal window** and run a tunnel service like Cloudflare or Ngrok:
```bash
# If using Cloudflare (cloudflared):
cloudflared tunnel --url http://localhost:8080

# If using ngrok:
ngrok http 8080
```
Copy the generated `https://` link and paste it into your `.env` file as the `WEBAPP_URL`:
```env
WEBAPP_URL=https://your-generated-link.trycloudflare.com
```

### 8. Run the Bot
In your **first terminal** (where your virtual environment is active), start the bot:
```bash
python main.py
```
*Note: This command simultaneously starts the Telegram bot polling and the `aiohttp` web server on port 8080.*

Your bot is now live! Open Telegram, send `/start` to your bot, and open the Mini App!

---

## 🛠️ Deployment Structure
This repository is configured and ready for production deployment:
- **`Dockerfile`**: Use this to containerize the app and deploy it to services like DigitalOcean, AWS, or Railway.
- **`Procfile`**: Pre-configured for easy deployment to Heroku or Render.
- **`database/bot.db`**: Automatically created. For serverless deployments, consider swapping the SQLite connection in `db.py` for PostgreSQL.
