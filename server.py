import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
WEBAPP_URL = os.getenv('WEBAPP_URL', '')

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения!")

if not WEBAPP_URL:
    logging.warning("WEBAPP_URL не задан! Кнопка 'Открыть Гримуар' не будет работать корректно.")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Aiogram bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============== TELEGRAM BOT HANDLERS ==============

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Handle /start command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📖 Открыть Гримуар",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])
    
    await message.answer(
        "⚔️ *Добро пожаловать в мир Теней Эльдории!*\n\n"
        "🎲 Откройте Гримуар, чтобы узнать правила игры, "
        "погрузиться в атмосферу тёмного фэнтези или оставить свой отзыв.",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    """Handle /help command"""
    await message.answer(
        "📜 *Команды бота:*\n\n"
        "/start - Открыть главное меню\n"
        "/help - Показать справку\n"
        "/rules - Краткие правила игры",
        parse_mode='Markdown'
    )

@dp.message(Command("rules"))
async def rules_command(message: types.Message):
    """Handle /rules command"""
    await message.answer(
        "⚔️ *Краткие правила Теней Эльдории:*\n\n"
        "1️⃣ Соберите отряд из 2-5 героев\n"
        "2️⃣ Исследуйте подземелья и сражайтесь с монстрами\n"
        "3️⃣ Собирайте артефакты и улучшайте персонажей\n"
        "4️⃣ Победите Тёмного Владыку!\n\n"
        "📖 Полные правила доступны в Гримуаре.",
        parse_mode='Markdown'
    )

async def main():
    """Run the Telegram bot"""
    logger.info(f"🤖 Telegram бот запущен. WebApp URL: {WEBAPP_URL}")
    await dp.start_polling(bot)

# ============== MAIN ==============

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
