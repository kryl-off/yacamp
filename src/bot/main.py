import os

import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from llm_client import LLMClient

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
llm_client = LLMClient()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        'Привет! Я бот для работы с Yandex GPT. Просто напиши мне свой вопрос'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_message = update.message.text

    if not user_message.strip():
        await update.message.reply_text('Пожалуйста, введите вопрос')
        return

    try:
        # Показываем статус "печатает"
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
# добавить валидатор, спросим у яндекс гпт, не содержит ли сообщение пользователя
# стоп слова или плохой контекст
        response = llm_client.ask_question(user_message)
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f'Error handling message: {str(e)}')
        await update.message.reply_text(
            'Извините, произошла ошибка при обработке вашего запроса. '
            'Пожалуйста, попробуйте позже.'
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f'Update {update} caused error {context.error}')
    if update and update.effective_message:
        await update.effective_message.reply_text(
            'Произошла ошибка. Пожалуйста, попробуйте позже.'
        )


def main():
    """Основная функция"""
    try:
        # Проверяем возможность генерации токена при запуске
        llm_client.get_iam_token()
        logger.info('IAM token test successful')

        application = Application.builder().token(TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)

        logger.info('Bot starting...')
        application.run_polling()

    except Exception as e:
        logger.error(f'Failed to start bot: {str(e)}')


if __name__ == "__main__":
    main()
