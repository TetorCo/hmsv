from json_upload import local_to_s3

import requests
import datetime
import json

class stockUs():

    def __init__(self):

        self.today = datetime.date.today()
        self.today = self.today.strftime('%Y%m%d')  ## QuickFS date format => YYYYMMDD
        self.apiKey = '{quickfs.apikey}'
        self.header = {'x-qfs-api-key': self.apiKey}

        ## rawData/usAllCompany.json(미국에 상장된 모든 회사)에 데이터가 존재하는지 확인 ##
        self.addAllCompany()

        ## 현 날짜 기준으로 새롭게 상장된 회사가 있는지 체크 ##
        self.loadNewCompany()

        ## local에 저장된 파일을 s3에 저장
        local_to_s3()


    def addAllCompany(self):
        ## 현재 상장된 모든 회사의 재무제표를 하나의 JSON에 모아놓는 함수.

        with open('./rawData/usAllCompany.json', 'r', encoding='utf-8') as totalCompanyFile:
            companyList = json.load(totalCompanyFile)

            if len(companyList['data']) == 0:

                temp = requests.get(f'https://public-api.quickfs.net/v1/companies/US/NASDAQ', headers=self.header)
                temp = json.loads(temp.content)

                with open('./rawData/usAllCompany.json', 'w', encoding='utf-8') as file:

                    json.dump(temp, file, indent=4)


    def loadNewCompany(self):

        self.newCompany = requests.get(f'https://public-api.quickfs.net/v1/companies/updated/{self.today}/US', headers=self.header).content
        self.newCompanyJson = json.loads(self.newCompany)  ## json 문자열을 파싱해서 가져오기 때문에 loads 사용.

        if self.newCompanyJson['count'] == 0:
            print(f'{self.today}에는 새로 상장한 회사는 없습니다.')

        else:
            print(f'{self.today}에 새로 상장한 회사는 총 {self.newCompanyJson["count"]}개입니다. 데이터를 추가합니다.')
            print(self.newCompanyJson['data'])

            with open('stockUS/usAllCompany.json', 'r', encoding='utf-8') as file:
                exist_data = json.load(file)

            exist_data["data"].extend(self.newCompanyJson["data"])

            with open('stockUS/usAllCompany.json', 'w', encoding='utf-8') as file:
                json.dump(exist_data, file, indent=4)


    def loadData(self):
        ### 나스닥에 상장된 회사 재무재표 데이터를 우선 로컬에 json 파일로 저장하기. / s3 저장 염두
        usAllCompanyList = []

        with open('stockUS/usAllCompany.json', 'r', encoding='utf-8') as file:

            cl = json.load(file)
            usAllCompanyList.extend(cl['data'])
        
        for company in usAllCompanyList:

            financialFile = requests.get(f'https://public-api.quickfs.net/v1/data/all-data/{company}?api_key={apiKey}')
            financialFile = json.loads(financialFile.content)

            with open(f'stockUS/rawData/{financialFile["data"]["metadata"]["symbol"]}.json', 'w', encoding='utf-8') as savePath:

                json.dump(financialFile, savePath, indent=4)


    def apiUsage(self):

        print(requests.get('https://public-api.quickfs.net/v1/usage', headers=self.header).content)


if __name__ == "__main__":

    apiKey = '{}'
    stock = stockUs()