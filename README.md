## 프로젝트 소개
Auto-Arima Model이 예측한 기업의 미래 10년 뒤 재무재표를 바탕으로 현재 기업의 주가가 고평가인지 저평가인지 알려주는 서비스

### 목표
재무재표를 기반으로 해당 기업의 성장률을 예측하고, 현재 주가에 반영해서 주식을 구매할 때 나만의 여러 개의 가이드라인들 중 하나로 활용해 투기가 아닌 투자를 하기 위함

## 아키텍처
![hmsv_archi](https://github.com/TetorCo/hmsv/assets/76984534/00e3d6e1-7c4e-4053-89d8-3a92f3cf9f29)

## 기술 스택
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)
![mlflow](https://img.shields.io/badge/mlflow-%23d9ead3.svg?style=for-the-badge&logo=numpy&logoColor=blue)
![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)

++ Locust, AWS S3

## 성과
- A-Z까지 하나의 서비스를 제작
- Mlflow를 활용해서 Model Test를 진행하고, 결과를 저장해서 언제든지 사용할 수 있도록 MLOps 시스템을 만들 수 있는 기초를 경험
- RabbitMQ를 사용해서 메세지 브로커 시스템을 구축

## 개선할 점
- 모델의 성능이 사용할 수 없는 수준 -> 더 정밀한 데이터 분석과 Arima Model의 학습이후 추가적인 성능 향상 필요
- 완전한 MLOps 시스템 구축을 하지 못함 -> 자동으로 Model Test를 진행하고, 성능이 좋은 Model을 배포할 수 있는 시스템을 구축해야 함
