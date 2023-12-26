import pika
import json

def rabbitMQ(company_id,
            dr, tgr, mos, stock_price, count_stock,
            company_value, collect_stock, safe_stock, over_percent_stock,
            model_aic):

    ## RabbitMQ Setting
    rabbitmq_host = 'host.docker.internal'
    user_queue = 'user_queue'
    model_queue = 'model_queue'

    # RabbitMQ 연결 설정
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=5672))
    channel = connection.channel()

    # User Queue Create
    channel.queue_declare(queue=user_queue)

    # Model Queue Create
    channel.queue_declare(queue=model_queue)

    # User Input Data
    user_data = {
        'company_id': company_id,
        'dr': dr,
        'tgr': tgr,
        'mos': mos,
        'stock_price': stock_price,
        'count_stock': count_stock
    }

    # Model Metrics Data
    model_data = {
        'company_id': company_id,
        'company_value': company_value,
        'collect_stock': collect_stock,
        'safe_stock': safe_stock,
        'over_percent_stock': over_percent_stock,
        'model_aic': model_aic
    }

    # 데이터를 JSON 형태로 변환하여 RabbitMQ에 전송
    channel.basic_publish(exchange='', routing_key=user_queue, body=json.dumps(user_data))

    channel.basic_publish(exchange='', routing_key=model_queue, body=json.dumps(model_data))

    print('Data sent to RabbitMQ successfully')

    # 연결 종료
    connection.close()