import logging

import requests

import telegram

import time

from dotenv import load_dotenv

from http import HTTPStatus

load_dotenv()

PRACTICUM_TOKEN = 'AQAAAAA-IasbAAYckSaOJjEn-kDmukhNLA-_4NA'
TELEGRAM_TOKEN = '2093395141:AAF3PGObc08tWDQ9cTrzC6GadcnP_ZCn4tc'
TELEGRAM_CHAT_ID = '1454224325'

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(name)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Функция для отправки вообщений."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    logger.info(f'Отправлено сообщение: "{message}"')


def get_api_answer(current_timestamp):
    """Делаю запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == HTTPStatus.OK:
        response = response.json()
        return response
    raise ValueError('что-то пошло не так!')


def check_response(response):
    """Проверяю ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError('Неверный тип данных в отевете API.')
    homeworks = response.get('homeworks')
    if homeworks is None:
        raise ValueError('Домашние работы отсутствуют!')
    if type(homeworks) is not list:
        raise TypeError('Неверный тип данных для домашних заданий')
    return homeworks
    keys = ['status', 'homework_name']
    for key in keys:
        if key not in homeworks:
            message = f'Ключа {key} нет в ответе API'
            raise KeyError(message)


def parse_status(homework):
    """Извлекаю из информации о домашней работе статус этой работы."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    verdict = HOMEWORK_STATUSES[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяю TOKEN на корректность."""
    TOKENS = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    NO_TOKEN = ('В переменных окружения нет {const}')
    IF_TOKENS_EXISTS = True
    for const in TOKENS:
        if globals()[const] is None:
            logger.critical(NO_TOKEN.format(const=const))
            IF_TOKENS_EXISTS = False
        return IF_TOKENS_EXISTS


def main():
    """Описываю основную логику работы программы."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(ENDPOINT, current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
