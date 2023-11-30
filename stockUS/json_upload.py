import boto3
import glob
import os

# AWS 자격 증명 정보 설정
aws_access_key_id = '{aws_access_key_id}'
aws_secret_access_key = '{aws_secret_access_key}'

# 업로드할 파일 경로 지정
local_folder_path = 'stockUS/rawData'
file_pattern = '*.json'

# S3 버킷 지정
bucket_name = 'hackathon2023stockvalue'

def local_to_s3():
    try:
        # Boto3 클라이언트 생성
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # 파일들 가져오기
        local_file_list = glob.glob(os.path.join(local_folder_path, file_pattern))

        # 파일 업로드
        for file_path in local_file_list:
            file_name = os.path.basename(file_path)

            object_key = 'stock_json_file/' + file_name  # S3에 저장할 파일의 객체 키 설정

            with open(file_path, 'rb') as file:
                s3_client.upload_fileobj(file, bucket_name, object_key)

        print("파일 업로드 완료")

    except Exception as e:
        print("파일 업로드 실패:", e)