import os
import logging
import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация API
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        'Привет! Я бот с моделью Claude. Просто напишите мне сообщение, и я отвечу вам.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        'Я могу общаться с вами, используя модель Claude. Просто напишите мне сообщение!'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    try:
        # Получаем сообщение от пользователя
        user_message = update.message.text
        
        # Подготавливаем запрос к API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://t.me/your_bot_username",
            "X-Title": "Telegram Bot",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "anthropic/claude-3-sonnet",  # Используем Claude, который доступен во всех регионах
            "messages": [
                {"role": "system", "content": "Вы - полезный ассистент."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        logger.info(f"Отправляем запрос к API: {json.dumps(data, ensure_ascii=False)}")
        
        # Отправляем запрос к API
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        logger.info(f"Получен ответ от API. Статус: {response.status_code}")
        logger.info(f"Тело ответа: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"API вернул ошибку: {response.status_code} - {response.text}")
            raise Exception(f"API вернул ошибку: {response.status_code}")
            
        # Получаем ответ от модели
        response_data = response.json()
        
        if "choices" not in response_data:
            logger.error(f"Неожиданный формат ответа: {response_data}")
            raise Exception("Неожиданный формат ответа от API")
            
        if not response_data["choices"]:
            logger.error("Пустой список choices в ответе")
            raise Exception("Пустой ответ от API")
            
        if "message" not in response_data["choices"][0]:
            logger.error(f"Отсутствует поле message в ответе: {response_data['choices'][0]}")
            raise Exception("Некорректный формат ответа от API")
            
        bot_response = response_data["choices"][0]["message"]["content"]
        
        # Отправляем ответ пользователю
        await update.message.reply_text(bot_response)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при обработке сообщения: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка сети. Попробуйте позже."
        )
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при разборе JSON ответа: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка при обработке ответа от сервера. Попробуйте позже."
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже."
        )

def main():
    """Основная функция запуска бота"""
    # Токен бота
    token = "7588100365:AAE5g9hQ3GZ-pGpsyYq9fUUUJ58AujUNEdU"
    
    # Создаем приложение
    application = Application.builder().token(token).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 