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
    logger.error('Не получет ответс АPI сервера.')
    raise ValueError('что-то пошло не так!')


def check_response(response):
    """Проверяю ответ API на корректность."""
    if type(response) is not dict:
        logger.error('Неверный тип данных в отевете API.')
        raise TypeError('Неверный тип данных в отевете API.')
    homeworks = response.get('homeworks')
    if homeworks is None:
        logger.error('Домашние работы отсутствуют!')
        raise ValueError('Домашние работы отсутствуют!')
    if type(homeworks) is not list:
        logger.error('Неверный тип данных для домашних заданий')
        raise TypeError('Неверный тип данных для домашних заданий')
    logger.info('Ваша домашняя работа.')
    return homeworks


def parse_status(homework):
    """Извлекаю из информации о домашней работе статус этой работы."""
    status = homework.get('status')
    if status not in HOMEWORK_STATUSES:
        logger.error('статус неизвестен')
        raise KeyError('статус неизвестен')
    verdict = HOMEWORK_STATUSES[status]

    homework_name = homework.get('homework_name')
    if homework_name is None:
        logger.error('Названия работы неизвестно')
        raise KeyError('Названия работы неизвестно')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяю TOKEN на корректность."""
    token_list = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    result = True
    for token in token_list:
        if token is None:
            logger.critical('Проблемы с переменными окружения')
            result = False
    logger.info('Проверка Токена прошла успешно!')
    return result


def main():
    """Описываю основную логику работы программы."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            logger.info('')
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
