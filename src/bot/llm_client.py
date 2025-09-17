import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_SERVICE_URL = os.getenv('LLM_SERVICE_URL')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, base_url: str = LLM_SERVICE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30

    def ask_question(self, question: str) -> str:
        """Отправка запроса к LLM сервису"""
        try:
            response = self.session.post(
                f'{self.base_url}/ask',
                json={'question': question},
                timeout=30
            )
            response.raise_for_status()
            return response.json()['answer']

        except requests.exceptions.Timeout:
            logger.error('LLM service timeout')
            raise Exception('Сервис не отвечает, попробуйте позже')

        except requests.exceptions.ConnectionError:
            logger.error('LLM service connection error')
            raise Exception('Ошибка подключения к сервису')

        except requests.exceptions.HTTPError as e:
            logger.error(f'LLM service HTTP error: {e}')
            if response.status_code == 500:
                raise Exception('Внутренняя ошибка сервиса')
            else:
                raise Exception(f'Ошибка сервиса: {response.status_code}')

        except Exception as e:
            logger.error(f'Unexpected error from LLM service: {str(e)}')
            raise Exception('Неожиданная ошибка сервиса')

    def get_iam_token(self) -> str:
        """Получение IAM токена через API LLM сервиса"""
        try:
            response = self.session.get(
                f'{self.base_url}/iam-token',
                timeout=10
            )
            response.raise_for_status()
            return response.json()['iam_token']

        except requests.exceptions.Timeout:
            logger.error('IAM token request timeout')
            raise Exception('Сервис IAM токена не отвечает')

        except requests.exceptions.ConnectionError:
            logger.error('IAM token service connection error')
            raise Exception('Ошибка подключения к сервису IAM токена')

        except requests.exceptions.HTTPError as e:
            logger.error(f'IAM token HTTP error: {e}')
            if response.status_code == 500:
                raise Exception('Внутренняя ошибка сервиса IAM токена')
            else:
                raise Exception(f'Ошибка сервиса IAM токена: {response.status_code}')

        except KeyError:
            logger.error('Invalid response format from IAM token service')
            raise Exception('Неверный формат ответа от сервиса IAM токена')

        except Exception as e:
            logger.error(f'Unexpected error from IAM token service: {str(e)}')
            raise Exception('Неожиданная ошибка при получении IAM токена')
