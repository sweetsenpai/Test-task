# Test task

## Python скрип для получение оповещения от Битрикс24 о создании новой сделке, записи ФИО и номера телефона клиента, а так же комментария в google sheets и БД.  
 
 ### Сервер
 Для того чтобы установить исходящий вебхук от Битрикс24 и получать от него сообщения о создании новой сделки, необходим сервер и публичный адрес.
 Самым простым решением для такой задачи будет flask  в связки с ngrok, для более простой связки этих двух состовляющих используется библиотека `flask_ngrok`.
```python
from flask import Flask, request
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)

if __name__ == "__main__":
    app.run()
```
 ### Получение информации от Битрикс24
 Для сбора заданной иформации от Битрикс24 необходимо получить id нового заказа из оповещение от вебхука.
```python
# получаем post метод от Битрикс24 и декодируем сообщение для получение id новой сделки
deal_id = str(request.get_data()).split('%5')[4].split('=')[1].replace('&', '').replace('ts', '')
```
После того как мы вытащили id новго заказа, с помощью входящего вебхука и REST API получаем от  Битрикс24 коментарий о новой сделке и id клиента привязаного к ней.
```python
deal = requests.get(f'{webhook_url}crm.deal.get?ID={deal_id}').json()['result']
        comment_text = deal['COMMENTS']
        # получаем id клиента 
        contact_id = deal['CONTACT_ID']
```
Далее делаем повторный запрос к Битрикс24 уже для получения данных о клиенте.
```python
contact = requests.get(f'{webhook_url}crm.contact.get?ID={contact_id}').json()['result']
        contact_fio = [contact['NAME'], contact['SECOND_NAME'], contact['LAST_NAME']]
        # избавляемся от None значений в ФИО, если такие имеются 
        contact_fio = [str(i or '') for i in contact_fio]
        contact_fio = ' '.join(contact_fio)
        contact_phone = contact['PHONE'][0]['VALUE']
        data = [contact_fio, contact_phone, comment_text]
```

 ### База данных