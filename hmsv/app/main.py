import numpy as np
import pandas as pd
import numpy_financial as npf

import app.func
import app.connect_s3
import app.crawling_stock_code
import message_rabbit.send
import message_rabbit.company_name_check

from datetime import datetime
from dateutil.relativedelta import relativedelta


class arima:

    def __init__(self, stock_name, dr, tgr, mos, stock_price, count_stock):
        ## stock_name을 받아서 s3에 해당 파일이 있는지 확인 아니라면 크롤링 코드 실행.
        stock = app.connect_s3.connect_s3(stock_name)

        if stock == None:

            stock_name = app.crawling_stock_code.search(stock_name)
            stock = app.connect_s3.connect_s3(stock_name)
            
            if stock is None:

                raise ValueError("오류가 발생했습니다.")

        self.stock = stock

        self.annual_month = self.stock["data"]["financials"]["annual"]["period_end_date"][0].split("-")[1]
        self.revenue = self.stock["data"]["financials"]["quarterly"]["revenue"]
        self.cf_cfo = self.stock["data"]["financials"]["quarterly"]["cf_cfo"]
        self.cfi_ppe_net = self.stock["data"]["financials"]["quarterly"]["cfi_ppe_net"]
        self.ppe_net = self.stock["data"]["financials"]["quarterly"]["ppe_net"]
        self.period_end_date = self.stock["data"]["financials"]["quarterly"]["period_end_date"]  # 분기 별 year-month

        self.dr = dr  # 할인율
        self.tgr = tgr  # 영구 성장률
        self.mos = mos  # 안전 마진
        self.stock_price = stock_price  # 현재 주식 가격
        self.count_stock = count_stock  # 발행된 총 주식 개수
        self.cash = self.stock["data"]["financials"]["annual"]["cash_and_equiv"][-1]  # 현금 보유량
        self.total_debt = (
            self.stock["data"]["financials"]["annual"]["st_debt"][-1]
            + self.stock["data"]["financials"]["annual"]["lt_debt"][-1]
        )  # 전체 부채
        self.net_debt = np.abs(self.total_debt) - self.cash  # 잉여 현금

        self.arima_model_aic = None


    def predict(self):

        ### Start ###
        quater_index, annual_index = self.make_train_data()
        model_pred_count, pred_index = self.cal_pred_count(annual_index[-1])
        future_annual_index = self.cal_annual_count(annual_index[-1])
        final_index = annual_index + future_annual_index

        original_df = pd.DataFrame()

        for column_name in ["revenue", "cf_cfo", "cfi_ppe_net", "ppe_net"]:
            
            df = self.extract_data(quater_index, column_name)

            if original_df.empty:

                original_df = pd.DataFrame(
                    df[f"{column_name}"], index=quater_index, columns=[f"{column_name}"]
                )

            else:

                temp_df = pd.DataFrame(
                    df[f"{column_name}"], index=quater_index, columns=[f"{column_name}"]
                )

                original_df = pd.concat([original_df, temp_df], axis=1)

        # original_df = original_df / 1000000  ## 단위 변환

        #### modeling & predctions ####
        pred_data_df = pd.DataFrame()

        for i in original_df.columns:

            arima_model = app.func.useAutoArima(original_df[f"{i}"])
            self.arima_model_aic = arima_model.aic()  ## 예측모델의 AIC

            pred_data = app.func.predictionData(arima_model, model_pred_count)

            ## 예측한 데이터 df로 만들기
            if pred_data_df.empty:
                
                pred_data_df = pd.DataFrame(
                    pred_data[0], index=pred_index, columns=[f"{i}"]
                )

            else:

                temp_pred_df = pd.DataFrame(
                    pred_data[0], index=pred_index, columns=[f"{i}"]
                )

                pred_data_df = pd.concat([pred_data_df, temp_pred_df], axis=1)

        ## 기존의 데이터와 모델이 예측한 데이터 합치기 -> 분기 별 데이터
        total_df = pd.concat([original_df, pred_data_df])

        ## 합친 분기 별 데이터에서 연간 별 데이터로 변환
        sum_data = []

        for idx in range(0, len(total_df), 4):

            sum_data.append(total_df.iloc[idx : idx + 4].sum())

        test_groupby = total_df.groupby(pd.factorize(total_df.index)[0] // 4).sum()
        test_groupby.index = final_index   # type: ignore

        annual_df = pd.DataFrame(sum_data, index=final_index, columns=total_df.columns)
        annual_df["ppe_net"] = total_df["ppe_net"]

        test_groupby["ppe_net"] = total_df["ppe_net"]

        final_data = self.cal_shareholder_shares(test_groupby)

        if final_data != False:

            model_result_data = self.cal_company_stock(
                    final_data,
                    self.dr,
                    self.tgr,
                    self.mos,
                    self.stock_price,
                    self.count_stock,
            )

            ### DB Load Part
            ## Company Code Check
            # company_id = message_rabbit.company_name_check.check(self.stock["data"]["metadata"]["symbol"])

            ## Metrics Send
            # message_rabbit.send.rabbitMQ(company_id,
            #     self.dr, self.tgr, self.mos, self.stock_price, self.count_stock,
            #     model_result_data["company_value"], model_result_data["collect_stock"], model_result_data["safe_stock"], model_result_data["over_percent_stock"],
            #     self.arima_model_aic)
            message_rabbit.send.company_name_and_arima_model_aic(
                self.stock["data"]["metadata"]["symbol"],
                self.arima_model_aic
            )
            
            return (
                self.stock["data"]["metadata"]["name"],
                model_result_data["company_value"],
                model_result_data["collect_stock"],
                model_result_data["safe_stock"],
                model_result_data["over_percent_stock"],
                self.stock_price
            )
        
        else:
            return False

    ## 모델 학습에 필요한 데이터 정리
    def make_train_data(self):

        quarter_index = []
        annual_index = []

        for date in self.stock["data"]["financials"]["annual"]["period_end_date"]:
            static_year_month = date
            temp_list = [date]
            date = datetime.strptime(date, "%Y-%m")

            for _ in range(3):
                date = date + relativedelta(months=-3)
                check_date = date.strftime("%Y-%m")

                if check_date in self.period_end_date:
                    temp_list.insert(0, date.strftime("%Y-%m"))

            if len(temp_list) == 4:
                quarter_index.extend(temp_list)
                annual_index.append(static_year_month)

        return quarter_index, annual_index

    ## 데이터 추출
    def extract_data(self, quarter_date_list, column_name):

        ## make empty df
        empty_df = pd.DataFrame(index=quarter_date_list, columns=[column_name])

        ## 추출할 데이터 가져온 후 df로 만들기
        original_data = self.stock["data"]["financials"]["quarterly"][f"{column_name}"]
        original_df = pd.DataFrame(original_data, index=self.period_end_date)

        ## make train data
        for train_date in empty_df.index:
            if train_date in original_df.index:
                empty_df.loc[train_date, f"{column_name}"] = original_df.loc[
                train_date, 0
                ]

        return empty_df

    ## arima model이 예측해야 하는 개수 구하기
    def cal_pred_count(self, last_year_month):

        last_annual = datetime.strptime(last_year_month, "%Y-%m")

        cnt = 0
        pred_quater_index = []

        goal_year = datetime.today().year + 9

        while True:

            month = last_annual + relativedelta(months=3)
            month = month.strftime("%Y-%m")

            if month != str(goal_year) + "-" + self.annual_month:

                last_annual = datetime.strptime(month, "%Y-%m")
                pred_quater_index.append(month)

                cnt += 1

            else:

                pred_quater_index.append(month)

                cnt += 1

                break

        return cnt, pred_quater_index


    def cal_annual_count(self, last_data):

        last_data = datetime.strptime(last_data, "%Y-%m")

        pred_annual_index = []

        goal_year = datetime.today().year + 9

        while True:

            year = last_data + relativedelta(years=1)
            year = year.strftime("%Y-%m")

            if year != str(goal_year) + "-" + self.annual_month:

                last_data = datetime.strptime(year, "%Y-%m")
                pred_annual_index.append(year)

            else:

                pred_annual_index.append(year)
                break

        return pred_annual_index


    def cal_shareholder_shares(self, data):

        ## 1. 매출 대비 유형 자산 비율
        ### 유형 자산(ppe_net) / 매출액(revenue)
        div_ppe_net_revenue = []

        for idx in range(len(data["revenue"])):

            div_ppe_net_revenue.append(data["ppe_net"][idx] / data["revenue"][idx])

        ## 2. 작년 대비 매출 증가액
        ### 매출액[-1] - 매출액[-2]
        revenue_inc_cash = data["revenue"][-1] - data["revenue"][-2]

        ## 3. 작년 성장 자본 지출 금액 / Growth Capital Expenditure Amount Last Year
        ### 작년 대비 매출 증가액 * 매출 대비 유형 자산 비율 평균
        growth_amount_last_year = revenue_inc_cash * np.mean(div_ppe_net_revenue)

        ## 4. 작년 유지 자본 지출 금액 / Last Year's Capital Expenditure Amount
        ### 전체 자본 지출 금액[-1] - 작년 성장 자본 지출 금액
        cea_last_year = np.abs(data["cfi_ppe_net"][-1]) - growth_amount_last_year

        ## 5. 작년 유지 자본 지출 비중 / Last Year's Maintenance Capital Expenditure Share
        ### 작년 유지 자본 지출 금액 / 전체 자본 지출 금액[-1]
        mces = cea_last_year / np.abs(data["cfi_ppe_net"][-1])

        if mces < 0:
            return False

        ## 6. 유지 자본 지출 금액 / Maintenance Capital Expenditure Amount
        ### 유지 자본 지출 비중 X 전체 자본 지출
        meca = []

        for row_data in data["cfi_ppe_net"]:

            # print(np.abs(row_data), mces)
            meca.append((np.abs(row_data) * mces))

        ## 7. 주주 수익
        ### 영업 현금 흐름 = 유지 자본 지출 금액
        shareholder_benefit = []

        for idx in range(len(meca)):

            shareholder_benefit.append(data["cf_cfo"][idx] - meca[idx])

        return shareholder_benefit


    def cal_company_stock(self, data, dr, tgr, mos, stock_price, count_stock):
        
        ## 잔존 가치 / salvage value
        ### 가장 마지막 년도의 주주 수익 * (1+영구 성장률) / (할인율 - 영구 성장률)
        salvage_value = (data[-1] * (1 + (tgr / 100))) / ((dr - tgr) / 100)

        ## 현재 내재 가치
        ### npv(할인율, data[-10:]) + pv(할인율, 10, 0, -내재가치) - 잉여 현금
        company_value = (
            npf.npv(dr / 100, data[-10:])
            + npf.pv(dr / 100, 10, 0, -salvage_value)
            - (self.net_debt / 1000000)
        )

        ## 기업의 적정 주가
        ### (현재 내재 가치 * 1000000) / 전체 주식 개수
        collect_stock = company_value / count_stock

        ## 기업의 안전 마진 적정 주가
        ### 기업의 적정 주가 / (안전 마진 / 100)
        safe_stock = collect_stock * (mos / 100)

        ## 기업의 적정 주가 대비 현재 주가
        over_percent_stock = (stock_price / safe_stock) - 1

        company_value = int(company_value)
        collect_stock = round(collect_stock, 2)
        safe_stock = round(safe_stock, 2)
        over_percent_stock = round(over_percent_stock, 2) * 100

        result = {
            "company_value": company_value,
            "collect_stock": collect_stock,
            "safe_stock": safe_stock,
            "over_percent_stock": over_percent_stock,
        }

        return result


if __name__ == "__main__":
    test = arima("애플", 15, 3, 50, 196, 15821950000)
    print(test.predict())
    # a, b = test.make_train_data()

    # print(a, len(a))
    # print(b, len(b))
    # print(test.revenue)
