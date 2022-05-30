# -*- coding: UTF-8 -*-
# create on 20220201
# author @ Qizhong Deng

import pandas as pd
import requests
import re
from anole import UserAgent
from bs4 import BeautifulSoup as bs


def get_html(url, headers):
    schema = "http://www.stats.gov.cn/"
    while True:
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                print("Get into the page successfully")
                html = response.content.decode('utf-8-sig')
                return html

        except requests.exceptions.MissingSchema as e:
            print('Unvalid url:', e)
            url = schema + url
            print('Corrected to', url)
            continue

        except UnicodeError as e:
            print('UnicodeError:', e)
            return None


def parse_html(html):
    tables = pd.read_html(html, index_col=0)[1:-1]

    # 对不同表头结构进行分别处理
    for idx, table in enumerate(tables):
        if idx == 0:
            table.columns = table.iloc[2]
            table = table.iloc[3:, :]
        else:
            table.columns = table.iloc[1]
            table = table.iloc[2:, :]

        tables[idx] = table

    return tables


if __name__ == "__main__":
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    url = 'http://www.stats.gov.cn/tjsj/zxfb/202201/t20220130_1827161.html'
    # html = get_html(url, headers)

    # ==== For Testing ==== #
    # with open('../test_htmls/pmi_html.txt', 'w') as file:
    #     file.write(html)

    with open('../test_htmls/pmi_html.txt', 'r') as file:
        html = file.read()
    
    tables = parse_html(html)
    print(tables)

    
    

