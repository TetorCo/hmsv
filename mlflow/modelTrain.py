from pmdarima import auto_arima, model_selection

import json
import os

import numpy as np
import mlflow


ARTIFACT_PATH = "model"
mlflow.set_tracking_uri("http://127.0.0.1:5001")

os.environ["AWS_ACCESS_KEY_ID"] = "{AWS_ACCESS_KEY_ID}"
os.environ["AWS_SECRET_ACCESS_KEY"] = "{AWS_SECRET_ACCESS_KEY}"


with mlflow.start_run():

    ## Training Data Load
    with open('/Users/taebeomkim/coding/deProject/stockUS/rawData/AAPL.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    ## 매출액 / Revenue
    ## 영업 현금 흐름 / cf_cfo
    ## 전체 자본 지출 / cfi_ppe_net
    ## 유형 자산 / ppe_net
    train_list = ["revenue", "cf_cfo", "cfi_ppe_net", "ppe_net"]

    train, test = model_selection.train_test_split(
        data["data"]["financials"]["quarterly"][train_list[0]], train_size=0.8)

    print("Training AutoARIMA model...")
    arima = auto_arima(
        train,
        error_action="ignore",
        trace=False,
        suppress_warnings=True,
        maxiter=5,
        seasonal=True,
        m=12,
    )

    print("Model trained. \nExtracting parameters...")
    parameters = arima.get_params(deep=True)

    metrics = {x: getattr(arima, x)() for x in ["aic"]}

    predictions = arima.predict(n_periods=30, return_conf_int=False)

    mlflow.pmdarima.log_model(
        pmdarima_model=arima, artifact_path=ARTIFACT_PATH
    )
    mlflow.log_params(parameters)
    mlflow.log_metrics(metrics)
    model_uri = mlflow.get_artifact_uri(ARTIFACT_PATH)

    print(f"Model artifact logged to: {model_uri}")

    loaded_model = mlflow.pmdarima.load_model(model_uri)

    forecast = loaded_model.predict(30)

    print(f"Forecast: \n{forecast}")