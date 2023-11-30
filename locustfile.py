from locust import HttpUser, task, between

import time
import random

class QuicksstartUser(HttpUser):

    wait_time = between(1, 5)

    # @task(1)
    # def home_page(self):
    #     self.client.get('/')

    @task
    def arima_test(self):
        stock_list = ['apple', 'msft', 'amazon', 'tesla']
        dr_list = [15, 10, 8, 20, 30]
        tgr_list = [3, 5, 10, 7, 20]
        mos_list = [50, 20, 45, 60, 15]
        price_list = [190, 160, 187, 210, 80]
        count_list = [15821950000, 20000000000, 30000400050, 50000020]

        stock = random.choice(stock_list)
        dr = random.choice(dr_list)
        tgr = random.choice(tgr_list)
        mos = random.choice(mos_list)
        price = random.choice(price_list)
        count = random.choice(count_list)

        self.client.post('/predict',
                        data={
                            'stockname': stock,
                            'dr': str(dr),
                            'tgr': str(tgr),
                            'mos': str(mos),
                            'price': str(price),
                            'count': str(count),
                        })


    # def on_start(self):
    #     print('Start Locust!')