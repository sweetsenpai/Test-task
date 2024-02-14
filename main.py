from flask import Flask, request
from flask_ngrok import run_with_ngrok
import requests
from DB import Deal_data, session
from google_sheets import append_sheet
import os
from dotenv import load_dotenv
load_dotenv()

webhook_url = os.environ.get('WEBHOOK')

app = Flask(__name__)
run_with_ngrok(app)


@app.route("/")
def hello():
    return "Hello Geeks!! from Google Colab"


@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        deal_id = str(request.get_data()).split('%5')[4].split('=')[1].replace('&', '').replace('ts', '')
        deal = requests.get(f'{webhook_url}crm.deal.get?ID={deal_id}').json()['result']
        comment_text = deal['COMMENTS']

        contact_id = deal['CONTACT_ID']
        contact = requests.get(f'{webhook_url}crm.contact.get?ID={contact_id}').json()['result']
        contact_fio = [contact['NAME'], contact['SECOND_NAME'], contact['LAST_NAME']]
        contact_fio = [str(i or '') for i in contact_fio]
        contact_fio = ' '.join(contact_fio)
        contact_phone = contact['PHONE'][0]['VALUE']

        data = [contact_fio, contact_phone, comment_text]

        session.add(Deal_data(fio=contact_fio, phone=contact_phone, comment=comment_text))
        session.commit()
        session.close()
        append_sheet(data)
        return 'Webhook recived'


if __name__ == "__main__":
    app.run()
