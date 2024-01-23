from bs4 import BeautifulSoup

import requests
import re


def search(name):

    # 구글 검색 URL
    search_url = f"https://www.google.com/search?q={name}+stock"

    pattern = r'(\w+)\((\w+)\)'

    # 검색 결과 페이지 가져오기
    response = requests.get(search_url)

    if response.status_code == 200:

        # BeautifulSoup를 사용하여 HTML 파싱
        soup = BeautifulSoup(response.content, "html.parser")

        stock_element = soup.find_all("span", class_="r0bn4c rQMQod")
        # print(stock_element)

        for i in range(len(stock_element)):

            match = re.match(pattern, stock_element[i].text)

            if match != None:
                print(match)

                stock_symbol = match.group(1)
                stock_exchange = match.group(2)

                if stock_exchange != 'NASDAQ':

                    return [None, '입력해주신 기업은 NASDAQ에 상장된 기업이 아닙니다.']

                return stock_symbol

        return [None, '기업 주식 코드를 찾을 수 없습니다.']

    else:
        print("검색 결과 페이지를 가져오는 데 실패하였습니다.")


if __name__ == "__main__":

    print(search('apple'))