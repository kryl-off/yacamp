import logging
import jwt
import requests
import time
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

SERVICE_ACCOUNT_ID = os.getenv('SERVICE_ACCOUNT_ID')
KEY_ID = os.getenv('KEY_ID')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
FOLDER_ID = os.getenv('FOLDER_ID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MODERATION_SERVICE_URL = os.getenv('MODERATION_SERVICE_URL')
PRECHECK_SERVICE_URL = os.getenv("PRECHECK_SERVICE_URL")




logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class YandexGPTBot:
    def __init__(self):
        self.iam_token = None
        self.token_expires = 0

    def get_iam_token(self):
        """Получение IAM-токена (с кэшированием на 1 час)"""
        if self.iam_token and time.time() < self.token_expires:
            return self.iam_token

        try:
            now = int(time.time())
            payload = {
                'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
                'iss': SERVICE_ACCOUNT_ID,
                'iat': now,
                'exp': now + 3600
            }

            encoded_token = jwt.encode(
                payload,
                PRIVATE_KEY,
                algorithm='PS256',  # алгоритм шифрования, который мы передаем
                headers={'kid': KEY_ID}
            )

            response = requests.post(
                'https://iam.api.cloud.yandex.net/iam/v1/tokens',
                json={'jwt': encoded_token},
                timeout=10
            )

            if response.status_code != 200:
                raise Exception(f'Error generating token: {response.text}')

            token_data = response.json()
            self.iam_token = token_data['iamToken']
            self.token_expires = now + 3500  # На 100 секунд меньше срока действия

            logger.info('IAM token generated successfully')
            return self.iam_token

        except Exception as e:
            logger.error(f'Error generating IAM token: {str(e)}')
            raise

    def ask_gpt(self, question):
        """Запрос к Yandex GPT API"""
        try:
            iam_token = self.get_iam_token()

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {iam_token}',
                'x-folder-id': FOLDER_ID
            }

            data = {
                'modelUri': f'gpt://{FOLDER_ID}/yandexgpt-lite',
                'completionOptions': {
                    'stream': False,
                    'temperature': 0.6,
                    'maxTokens': 2000
                },
                'messages': [
                    {
                        'role': 'user',
                        'text': question
                    }
                ]
            }

            response = requests.post(
                'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f'Yandex GPT API error: {response.text}')
                raise Exception(f'Error API: {response.status_code}')

            return response.json()['result']['alternatives'][0]['message']['text']

        except Exception as e:
            logger.error(f'Error in ask_gpt: {str(e)}')
            raise


yandex_bot = YandexGPTBot()

def precheck_text(text: str) -> bool:
    """Запрос к PreCheck сервису для проверки регулярками"""
    try:
        response = requests.post(f"{PRECHECK_SERVICE_URL}/precheck", json={"text": text}, timeout=5)
        response.raise_for_status()
        return response.json().get("malicious", False)
    except Exception as e:
        logger.error(f"Ошибка PreCheck: {str(e)}. Пропускаем проверку.")
        return False  # fail-safe


def check_malicious(text: str) -> bool:
    """Запрос на модератор-сервис"""
    try:
        response = requests.post(f'{MODERATION_SERVICE_URL}/moderate', json={'text': text}, timeout=10)
        response.raise_for_status()
        return response.json().get('malicious', False)
    except Exception as e:
        logger.error(f'Ошибка при проверке модерации: {str(e)}. Пропускаем проверку.')
        return False  # fail-safe: разрешаем запрос


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        'Привет! Я бот для работы с Yandex GPT. Просто напиши мне свой вопрос'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if not user_message.strip():
        await update.message.reply_text('Пожалуйста, введите вопрос')
        return
    
    if check_malicious(user_message):
        await update.message.reply_text(
            'Ваш запрос не может быть обработан по соображениям безопасности.'
        )
        return

    if precheck_text(user_message):
        await update.message.reply_text(
            'Ваш запрос заблокирован на этапе предварительной проверки.'
        )
        return

    if check_malicious(user_message):
        await update.message.reply_text(
            'Ваш запрос не может быть обработан по соображениям безопасности.'
        )
        return

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        response = yandex_bot.ask_gpt(user_message)
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
        yandex_bot.get_iam_token()
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
