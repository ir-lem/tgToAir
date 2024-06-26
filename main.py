import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import re

# Включение логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = '7280017760:AAEquoXbi7zi3slt88jXstv9-4VRJCtEc8Q'
AIRTABLE_API_KEY = 'patH7lvSZ5rVA0dgH.4a485411ee16338594ef91d59d4657191f7a2db32f3b7df900334c68c23bf25b'
AIRTABLE_BASE_ID = 'apppB06vApm5KLOYs'
AIRTABLE_TABLE_NAME = 'tgToAir'

def add_item_to_airtable(link, item, price):
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'fields': {
            'Link': link,
            'Item': item,
            'Price': price,
            'Real Price': '',
            'Status': '',
            'Comments': ''
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.status_code == 200

def update_comments_in_airtable(link, comment):
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    # Fetch the records first
    response = requests.get(url, headers=headers)
    records = response.json().get('records', [])
    
    for record in records:
        if record['fields'].get('Link') == link:
            record_id = record['id']
            current_comments = record['fields'].get('Comments', '')
            updated_comments = f"{current_comments}\n{comment}"
            data = {
                'fields': {
                    'Comments': updated_comments
                }
            }
            response = requests.patch(f'{url}/{record_id}', json=data, headers=headers)
            return response.status_code == 200
    return False

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправьте ссылку на пост, чтобы добавить товары в Airtable.')

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if text.startswith('http'):
        link = text
        # Здесь вам нужно будет получить текст поста
        # Примерный формат: "Товар1 — 1000₽\nТовар2 — 1500₽"
        post_text = "Товар1 — 1000₽\nТовар2 — 1500₽"  # Замените на реальный текст поста
        items = post_text.split('\n')
        for item in items:
            match = re.match(r'(.+?) — (\d+)', item)
            if match:
                item_name = match.group(1).strip()
                price = match.group(2).strip()
                add_item_to_airtable(link, item_name, price)
        update.message.reply_text('Товары добавлены в Airtable.')
    else:
        if any(word in text.lower() for word in ['бронирую', 'забронирую', 'букаю', 'забукаю', 'заберу', 'броню']):
            update_comments_in_airtable(context.user_data['current_link'], text)
            update.message.reply_text('Комментарий добавлен в Airtable.')

def main() -> None:
    """Запуск бота."""
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
