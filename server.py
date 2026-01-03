import os
import logging
import asyncio
from flask import Flask, request, jsonify, send_from_directory
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
CHANNEL_ID = os.getenv('CHANNEL_ID', '')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:3000')
PORT = int(os.getenv('PORT', 3000))

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения!")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='public', static_url_path='')

# Initialize Aiogram bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============== FLASK ROUTES ==============

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files"""
    return send_from_directory('public', path)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Handle feedback submissions from WebApp"""
    try:
        data = request.get_json()
        
        name = data.get('name', 'Аноним')
        msg_type = data.get('type', 'review')
        message = data.get('message', '')
        username = data.get('username', '')
        
        if not message or message.strip() == '':
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
        if not CHANNEL_ID:
            logger.warning('CHANNEL_ID не задан, невозможно отправить сообщение.')
            return jsonify({'error': 'Ошибка конфигурации сервера'}), 500
        
        # Format message
        type_emoji = '⭐' if msg_type == 'review' else '💡'
        type_name = 'Отзыв' if msg_type == 'review' else 'Предложение'
        username_str = f' (@{username})' if username else ''
        
        report = f"""📜 *Новая запись в летописи*

{type_emoji} *Тип:* {type_name}
👤 *Автор:* {name}{username_str}

📝 *Сообщение:*
{message}"""
        
        # Send to Telegram using new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(bot.send_message(
                chat_id=CHANNEL_ID,
                text=report,
                parse_mode='Markdown'
            ))
        finally:
            loop.close()
        
        return jsonify({'success': True, 'message': 'Ваше сообщение отправлено!'})
        
    except Exception as e:
        logger.error(f'Ошибка отправки сообщения: {e}')
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

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

def run_flask():
    """Run Flask server"""
    logger.info(f"🏰 Сервер запущен на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

async def run_bot():
    """Run the Telegram bot"""
    logger.info("🤖 Telegram бот запущен")
    await dp.start_polling(bot)

# ============== MAIN ==============

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run bot in main thread
    asyncio.run(run_bot())
