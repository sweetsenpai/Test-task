from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

db_path = 'sqlite:///test_task.db'
Base = declarative_base()


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


if not os.path.exists(db_path):
    engine = create_engine('sqlite:///psprof.db', echo=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
else:
    engine = create_engine(db_path, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()