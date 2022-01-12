# 国家统计局宏观数据爬取程序
# Author: Qizhong Deng
# Date: 2022.12.07
# Tested by: Python 3.8.6

import pandas as pd
import numpy as np

from requests.packages.urllib3 import disable_warnings
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs


# Initiation
url = "http://www.stats.gov.cn/tjsj/zxfb/202112/t20211214_1825287.html"

def get_html(url):
    """抓取传入url页面并返回html"""
    try:
        with sync_playwright() as p:
            disable_warnings()  # 禁用安全请求警告
            browser = p.webkit.launch()  # 启用webkit浏览器访问
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)  # 等待网页加载
            html = page.content()
            browser.close()
        print('Get into the website successfully!')
    except RuntimeError as e:
        print('Failed...', e)

    # For testing
    # with open("html.txt", 'w') as file:
    #     file.write(html)
    return html

def read_table(html):
    """读取html内的表格"""
    dfs = pd.read_html(html, header=0, index_col=0)  # 取页面内的第一个表
    # df.to_csv('test.csv')

    return dfs[1]


if __name__ == '__main__':
    # html = get_html(url)

    # For testing
    with open("html.txt", 'r') as file:
        html = file.read()
    
    df = read_table(html)

    print(df.loc['办公楼'])