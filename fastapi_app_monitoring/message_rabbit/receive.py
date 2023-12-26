from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pika
import json
import os
import dotenv

dotenv.load_dotenv()

## RabbitMQ Setting
rabbitmq_host = 'host.docker.internal'
user_queue = 'user_queue'
model_queue = 'model_queue'

## PostgresSQL Setting
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_db = os.getenv('POSTGRES_DB')
postgres_host = 'host.docker.internal'  # docker container name
postgres_port = os.getenv('POSTGRES_PORT')

## SQLAlchemy Engine Setting
db_url = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
engine = create_engine(db_url)

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

# 모델 정의
Base = declarative_base()

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

class User(Base):
    __tablename__ = 'user_info_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey('company.id'))
    dr = Column(Integer)
    tgr = Column(Integer)
    mos = Column(Integer)
    stock_price = Column(Integer)
    count_stock = Column(Integer)

class Model(Base):
    __tablename__ = 'model_predict_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey('company.id'))
    company_value = Column(Integer)
    collect_stock = Column(Integer)
    safe_stock = Column(Integer)
    over_percent_stock = Column(Integer)
    model_aic = Column(Integer)

# RabbitMQ 연결 설정
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=user_queue)


def user_table(body):
    # RabbitMQ로부터 메시지 수신
    message = json.loads(body.decode('utf-8'))

    # PostgreSQL에 데이터 저장
    user_input_data = User(
        company_id = message['company_id'],
        dr = message['dr'],
        tgr = message['tgr'],
        mos = message['mos'],
        stock_price = message['stock_price'],
        count_stock = message['count_stock']
    )

    session.add(user_input_data)
    session.commit()


def model_table(body):
    message = json.loads(body.decode('utf-8'))

    model_predict_data = Model(
        company_id = message['company_id'],
        company_value = message['company_value'],
        collect_stock = message['collect_stock'],
        safe_stock = message['safe_stock'],
        over_percent_stock = message['over_percent_stock'],
        model_aic = message['model_aic']
    )

    session.add(model_predict_data)
    session.commit()

# RabbitMQ에서 메시지 수신 대기
channel.basic_consume(queue=user_queue, on_message_callback=user_table, auto_ack=True)

channel.basic_consume(queue=model_queue, on_message_callback=model_table, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()