# -*- coding: UTF-8 -*-
# created on 2022-01-12 17:33
# author @Qizhong Deng
# tested by python 3.8.6


import requests
import datetime
import pandas as pd

from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright


def get_html(url):
    """抓取传入url页面并返回html"""
    try:
        with sync_playwright() as p:
            browser = p.webkit.launch()  # 启用webkit浏览器访问
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)  # 等待网页加载
            html = bs(page.content(), features='lxml')
            browser.close()
        print('Get into the website successfully!')
    except RuntimeError as e:
        print('Failed...', e)

    # For testing
    with open("eastmoney_html.txt", 'w') as file:
        file.write(html.prettify())

    return html




if __name__ == "__main__":
    url = 'https://data.eastmoney.com/cjsj/gdp.html'
    html = get_html(url)

    print(html)





