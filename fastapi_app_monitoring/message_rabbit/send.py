import pika
import json

def rabbitMQ(stock_name,
            dr, tgr, mos, stock_price, count_stock,
            company_value, collect_stock, safe_stock, over_percent_stock,
            model_aic):

    ## RabbitMQ Setting
    # host.docker.internal
    rabbitmq_host = 'host.docker.internal'
    rabbitmq_queue = 'stock_queue'

    # RabbitMQ 연결 설정
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=5672))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)

    # 생성할 데이터
    data_to_send = {
        'stock_name': stock_name,
        'dr': dr,
        'tgr': tgr,
        'mos': mos,
        'stock_price': stock_price,
        'count_stock': count_stock,
        'company_value': company_value,
        'collect_stock': collect_stock,
        'safe_stock': safe_stock,
        'over_percent_stock': over_percent_stock,
        'model_aic': model_aic
    }

    # 데이터를 JSON 형태로 변환하여 RabbitMQ에 전송
    channel.basic_publish(exchange='', routing_key=rabbitmq_queue, body=json.dumps(data_to_send))

    print('Data sent to RabbitMQ successfully')

    # 연결 종료
    connection.close()