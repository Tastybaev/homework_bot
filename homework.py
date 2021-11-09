import logging

import requests

import telegram

import time


PRACTICUM_TOKEN = 'AQAAAAA-IasbAAYckSaOJjEn-kDmukhNLA-_4NA'
TELEGRAM_TOKEN = '2093395141:AAF3PGObc08tWDQ9cTrzC6GadcnP_ZCn4tc'
CHAT_ID = 1454224325

logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s'
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
    """функция для отправки вообщений"""
    bot.send_message(chat_id=CHAT_ID, text=message)


def get_api_answer(url, current_timestamp):
    date = {'from_date': current_timestamp}
    response = requests.get(url, headers=HEADERS, params=date)
    if response.status_code == 200:
        response = response.json()
        return response
    raise ValueError('что-то пошло не так!')


def parse_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_response(response):
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
            bot.send_message(CHAT_ID, message)
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
