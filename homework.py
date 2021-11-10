import logging

import requests

import telegram

import time


PRACTICUM_TOKEN = 'AQAAAAA-IasbAAYckSaOJjEn-kDmukhNLA-_4NA'
TELEGRAM_TOKEN = '2093395141:AAF3PGObc08tWDQ9cTrzC6GadcnP_ZCn4tc'
TELEGRAM_CHAT_ID = 1454224325

logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
    format='%(asctime)s, %(name)s, %(levelname)s, %(message)s'
)

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
RETRY_TIME = 300
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена, в ней нашлись ошибки.'
}


def send_message(bot, message):
    """Функция для отправки вообщений."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(url, current_timestamp):
    """Делаю запрос к единственному эндпоинту API-сервиса."""
    date = {'from_date': current_timestamp}
    response = requests.get(url, headers=HEADERS, params=date)
    if response.status_code == 200:
        response = response.json()
        return response
    raise ValueError('что-то пошло не так!')


def parse_status(homework):
    """Извлекаю из информации о домашней работе статус этой работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    send_message(bot, message)


def check_response(response):
    """Проверяю ответ API на корректность."""
    homeworks = response.get('homeworks')
    homework_status = homeworks[0].get('status')
    if 'homeworks' in response:
        if homeworks:
            if homework_status in HOMEWORK_STATUSES:
                return homeworks
            raise ValueError('Статус домашней работы незадокментирован!')
        raise ValueError('Домашние работы отсутствуют!')
    raise ValueError('Ошибка! Что-то не то с сайтом.')


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
            bot.send_message(TELEGRAM_CHAT_ID, message)
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
