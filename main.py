from flask import Flask, request
from flask_ngrok import run_with_ngrok
import requests
from DB import Deal_data, session
from google_sheets import append_sheet

# импорт переменных среды из файла .env
import os
from dotenv import load_dotenv
load_dotenv()
webhook_url = os.environ.get('WEBHOOK')

app = Flask(__name__)
run_with_ngrok(app)


@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        # получаем post метод от Битрикс24 и декодируем сообщение для получение id новой сделки
        deal_id = str(request.get_data()).split('%5')[4].split('=')[1].replace('&', '').replace('ts', '')
        # с помощью исходящего вебхука и полученного id сделки получаем данные о новой сделке
        deal = requests.get(f'{webhook_url}crm.deal.get?ID={deal_id}').json()['result']
        comment_text = deal['COMMENTS']
        # получаем id клиента и с помощью исходящего вебхука получаем необходимую инфу о клиенте
        contact_id = deal['CONTACT_ID']
        contact = requests.get(f'{webhook_url}crm.contact.get?ID={contact_id}').json()['result']
        contact_fio = [contact['NAME'], contact['SECOND_NAME'], contact['LAST_NAME']]
        contact_fio = [str(i or '') for i in contact_fio]
        contact_fio = ' '.join(contact_fio)
        contact_phone = contact['PHONE'][0]['VALUE']
        data = [contact_fio, contact_phone, comment_text]
        # запись в БД
        session.add(Deal_data(fio=contact_fio, phone=contact_phone, comment=comment_text))
        session.commit()
        session.close()
        # запись в гугл таблицу
        append_sheet(data)
        return 'Webhook recived'


if __name__ == "__main__":
    app.run()
