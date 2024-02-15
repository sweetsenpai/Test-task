# Test task

## Python скрип для получение оповещения от Битрикс24 о создании новой сделке, записи ФИО и номера телефона клиента, а так же комментария в google sheets и БД.  
 
> ### Сервер
> Для того чтобы установить исходящий вебхук от Битрикс24 и получать от него сообщения о создании новой сделки, необходим сервер и публичный адрес.
> Самым простым решением для такой задачи будет `flask`  в связки с `ngrok`, для более простой связки этих двух состовляющих используется библиотека `flask_ngrok`.
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
 В качестве БД был выбран `sqlite` из-за простоты и легковестности. Для взаимодействия с БД используется библиотека `sqlalchemy`.

 Импортируем все необходимые зависимости в файл `DB.py` и с создаем объект конструкта `declarative_base()` для создания схемы бд.
```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

db_path = 'sqlite:///test_task.db'
Base = declarative_base()
```
Описываем структуру нашей будущей таблицы БД.

```python
class Deal_data(Base):
    __tablename__ = 'deal_data'
    data_id = Column(name='deal_id', type_=Integer, primary_key=True)
    fio = Column(name='name', type_=String)
    phone = Column(name='phone', type_=String)
    comment = Column(name='comment', type_=String)

    def __int__(self, fio, phone, comment):
        self.fio = fio
        self.phone = phone
        self.comment = comment

    def __repr__(self):
        return f'{self.data_id}, {self.fio}, {self.phone}, {self.comment}'
```

Проверяем существует ли файл с нашей БД, если существует то создаем объект `Session` и подключаемся к БД, если нет, то сначала создаем БД и далее подключаемся к ней. 
```python
if not os.path.exists(db_path):
    engine = create_engine('sqlite:///psprof.db', echo=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
else:
    engine = create_engine(db_path, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
```

Теперь в файле `main.py` записываем полученную информацию от Битрикс24 в БД.
```python
session.add(Deal_data(fio=contact_fio, phone=contact_phone, comment=comment_text))
session.commit()
session.close()
```

 ### Google Sheets
