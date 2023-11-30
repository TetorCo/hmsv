# from crawling_stock_code import search

import json
import boto3


def connect_s3(file_name):

    # AWS 자격 증명 정보 설정
    aws_access_key_id = '{aws_access_key_id}'
    aws_secret_access_key = '{aws_secret_access_key}'

    # S3 버킷과 객체 키 지정
    bucket_name = 'hackathon2023stockvalue'
    # object_key = f'stock_json_file/{file_name}.json'

    try:
        # Boto3 클라이언트 생성
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # 객체 키 지정
        object_key = f'stock_json_file/{file_name}.json'

        # 객체(파일) 가져오기
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        data = response['Body'].read().decode()

        # 가져온 데이터 처리 / str -> dict
        data_dict = json.loads(data)

        # print(data_dict, len(data_dict))
        return data_dict

    except Exception as e:

        print(f"데이터 가져오기 실패 : s3에 {file_name}.json이 존재하지 않습니다.", e)

        return None


if __name__ == "__main__":

    print(connect_s3('AAPL'))