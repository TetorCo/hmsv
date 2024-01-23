from locust import HttpUser, task, between

import time
import random

"""
시나리오
5초 마다 새로운 유저가 접속하게 되고 최대 40명의 유저가 서비스를 이용.
"""

class UserScenario(HttpUser):

    # task 실행 시 마다 5 ~ 10초 사이로 랜덤 대기.
    # 이유는? 유저가 predict 페이지에서 값을 입력하는 시간 때문.
    wait_time = between(5, 10)

    @task(2)
    def home_page(self):
        self.client.get('/')

    @task(10)
    def arima_test(self):

        weights = [0.4, 0.3, 0.2, 0.1]

        stock_list = ['apple', 'msft', 'tesla', 'amazon']
        dr_list = [15, 10, 8, 20]
        tgr_list = [3, 5, 10, 7]
        mos_list = [50, 20, 45, 60]
        price_list = [193.89, 396.51, 208, 154.78]
        shares_outstanding = [
            15461896000,
            7432262329,
            10334030586,
            3178921391]

        # 가중치를 이용해 최대한 실제 유저가 사용하는 것처럼 보이기 위함.
        stock = random.choices(stock_list, weights)[0]
        dr = random.choices(dr_list, weights)[0]
        tgr = random.choices(tgr_list, weights)[0]
        mos = random.choices(mos_list, weights)[0]

        if stock == 'apple':

            price = price_list[0]
            count = shares_outstanding[0]

        elif stock == 'msft':

            price = price_list[1]
            count = shares_outstanding[1]

        elif stock == 'tesla':

            price = price_list[2]
            count = shares_outstanding[2]

        elif stock == 'amazon':

            price = price_list[3]
            count = shares_outstanding[3]


        self.client.post('/predict',
                        data={
                            'stockname': stock,
                            'dr': str(dr),
                            'tgr': str(tgr),
                            'mos': str(mos),
                            'price': str(price), # type: ignore
                            'count': str(count), # type: ignore
                        })