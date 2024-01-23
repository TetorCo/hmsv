from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import pika
import json
import os
import dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
dotenv.load_dotenv(dotenv_path=dotenv_path)

## RabbitMQ Setting
rabbitmq_host = 'host.docker.internal'
user_queue = 'user_queue'
model_queue = 'model_queue'
model_monitoring_queue = 'model_monitoring_queue'

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

# class Company(Base):
#     __tablename__ = 'company'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String)


# class User(Base):
#     __tablename__ = 'user_input'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     company_id = Column(String, ForeignKey('company.id'))
#     dr = Column(Integer)
#     tgr = Column(Integer)
#     mos = Column(Integer)
#     stock_price = Column(Integer)
#     numbers_of_stocks = Column(Integer)


# class Model(Base):
#     __tablename__ = 'model_out_put'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     company_id = Column(String, ForeignKey('company.id'))
#     company_value = Column(Integer)
#     fair_value = Column(Integer)
#     margin_of_safety = Column(Integer)
#     percentage_difference = Column(Integer)
#     aic = Column(Integer)


class Arima_aic_analytics(Base):
    __tablename__ = 'arima_aic_analytics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String)
    arima_model_aic = Column(Integer)


# RabbitMQ 연결 설정
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=user_queue)


# def user_table(body):
#     # RabbitMQ로부터 메시지 수신
#     message = json.loads(body.decode('utf-8'))

#     # PostgreSQL에 데이터 저장
#     user_input_data = User(
#         company_id = message['company_id'],
#         dr = message['dr'],
#         tgr = message['tgr'],
#         mos = message['mos'],
#         stock_price = message['stock_price'],
#         numbers_of_stocks = message['numbers_of_stocks']
#     )

#     session.add(user_input_data)
#     session.commit()


# def model_table(body):
#     message = json.loads(body.decode('utf-8'))

#     model_predict_data = Model(
#         company_id = message['company_id'],
#         company_value = message['company_value'],
#         fair_value = message['fair_value'],
#         margin_of_safety = message['margin_of_safety'],
#         percentage_difference = message['percentage_difference'],
#         aic = message['aic']
#     )

#     session.add(model_predict_data)
#     session.commit()


def arima_model_analytics_table(_, __, ____, body):

    message = json.loads(body.decode('utf-8'))

    analytics_date = Arima_aic_analytics(
        stock_code = message['stock_code'],
        arima_model_aic = message['aic']
    )

    session.add(analytics_date)
    session.commit()

# RabbitMQ에서 메시지 수신 대기
# channel.basic_consume(queue=user_queue, on_message_callback=user_table, auto_ack=True)

# channel.basic_consume(queue=model_queue, on_message_callback=model_table, auto_ack=True)

channel.basic_consume(queue=model_monitoring_queue, on_message_callback=arima_model_analytics_table, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')

channel.start_consuming()