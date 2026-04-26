import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
