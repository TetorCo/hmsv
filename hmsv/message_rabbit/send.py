import pika
import json

# def rabbitMQ(company_id,
#             dr, tgr, mos, stock_price, numbers_of_stocks,
#             company_value, fair_value, margin_of_safety, percentage_difference,
#             aic):

#     ## RabbitMQ Setting
#     rabbitmq_host = 'host.docker.internal'
#     user_queue = 'user_queue'
#     model_queue = 'model_queue'

#     # RabbitMQ 연결 설정
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=5672))
#     channel = connection.channel()

#     # User Queue Create
#     channel.queue_declare(queue=user_queue)

#     # Model Queue Create
#     channel.queue_declare(queue=model_queue)

#     # User Input Data
#     user_data = {
#         'company_id': company_id,
#         'dr': dr,
#         'tgr': tgr,
#         'mos': mos,
#         'stock_price': stock_price,
#         'numbers_of_stocks': numbers_of_stocks
#     }

#     # Model Metrics Data
#     model_data = {
#         'company_id': company_id,
#         'company_value': company_value,
#         'fair_value': fair_value,
#         'margin_of_safety': margin_of_safety,
#         'percentage_difference': percentage_difference,
#         'aic': aic
#     }

#     # 데이터를 JSON 형태로 변환하여 RabbitMQ에 전송
#     channel.basic_publish(exchange='', routing_key=user_queue, body=json.dumps(user_data))

#     channel.basic_publish(exchange='', routing_key=model_queue, body=json.dumps(model_data))

#     print('Data sent to RabbitMQ successfully')

#     # 연결 종료
#     connection.close()


def company_name_and_arima_model_aic(stock_code, aic):

    ## RabbitMQ Setting
    rabbitmq_host = 'host.docker.internal'
    model_monitoring_queue = 'model_monitoring_queue'

    # RabbitMQ 연결 설정
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=5672))
    channel = connection.channel()

    # User Queue Create
    channel.queue_declare(queue=model_monitoring_queue)

    data = {
        "stock_code": stock_code,
        "aic": aic
    }

    channel.basic_publish(exchange='', routing_key=model_monitoring_queue, body=json.dumps(data))

    print('Data sent to RabbitMQ successfully')

    # 연결 종료
    connection.close()