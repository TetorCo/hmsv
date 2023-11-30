from celery import Celery
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import pika
import json

## RabbitMQ Setting
rabbitmq_host = 'localhost'
rabbitmq_queue = 'stock_queue'

## PostgresSQL Setting
postgres_user = 'postgres'
postgres_password = 'postgres'
postgres_db = 'postgres'
postgres_host = 'localhost'  # docker container name
postgres_port = 5433

## SQLAlchemy Engine Setting
db_url = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
engine = create_engine(db_url)

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

# 모델 정의
Base = declarative_base()

class Message(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_name = Column(String)
    dr = Column(Integer)
    tgr = Column(Integer)
    mos = Column(Integer)
    stock_price = Column(Integer)
    count_stock = Column(Integer)
    company_value = Column(Integer)
    collect_stock = Column(Integer)
    safe_stock = Column(Integer)
    over_percent_stock = Column(Integer)
    model_aic = Column(Integer)

celery = Celery('rabbitmq_to_postgresql',
            broker=f'amqp://guest:guest@{rabbitmq_host}:5672/',
            backend=f'{db_url}')

@celery.task
def test(text):
    print(text)
    return text


if __name__ == "__main__":
    test("he")