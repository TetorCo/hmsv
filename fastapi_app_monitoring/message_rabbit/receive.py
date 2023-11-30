from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pika
import json

## RabbitMQ Setting
rabbitmq_host = 'host.docker.internal'
rabbitmq_queue = 'stock_queue'

## PostgresSQL Setting
postgres_user = 'postgres'
postgres_password = 'postgres'
postgres_db = 'postgres'
postgres_host = 'host.docker.internal'  # docker container name
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

# RabbitMQ 연결 설정
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue)

def callback(ch, method, properties, body):
    # RabbitMQ로부터 메시지 수신
    message = json.loads(body.decode('utf-8'))

    # PostgreSQL에 데이터 저장
    new_message = Message(stock_name=message['stock_name'],
            dr=message['dr'],
            tgr=message['tgr'],
            mos=message['mos'],
            stock_price=message['stock_price'],
            count_stock=message['count_stock'],
            company_value=message['company_value'],
            collect_stock=message['collect_stock'],
            safe_stock=message['safe_stock'],
            over_percent_stock=message['over_percent_stock'],
            model_aic=message['model_aic'])

    session.add(new_message)
    session.commit()

# RabbitMQ에서 메시지 수신 대기
channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()