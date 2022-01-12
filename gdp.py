# -*- coding: UTF-8 -*-

import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright
from anole import UserAgent


def get_html_pw(url):
    """Return soup object from url"""
    try:
        with sync_playwright() as p:
            browser = p.webkit.launch()  # 启用webkit浏览器访问
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()
        print("Get into the page successfully")
        soup = bs(html, features='html5lib')
        return soup

    except TimeoutError:
        print("Failed...")
        return None


def get_html(url, header):
    """Only get GDP urls for the time being"""
    response = requests.get(url, headers=header)

    if response.status_code == 200:
        print("Get into the page successfully")
        html = response.content.decode('utf-8-sig')
        return html
    
    return None


def save_html(html):
    with open("./test_htmls/report_html.txt", "w") as file:
        file.write(html)


def get_urls(html):
    """Get GDP urls from the searching page"""
    soup = bs(html, features='lxml')
    titles = soup.find_all('font', {"class": "cont_tit03"})
    urlstrs = [re.search("urlstr = '(.*?)';", str(title.script)).group(1) for title in titles]

    return urlstrs


def get_table(html):
    """Get main tables from the report"""
    soup = bs(html, features='html5lib')
    tables = pd.read_html(soup.prettify(), header=1, index_col=0)

    return tables[1:]


def parse_table(table):
    table = table.dropna(axis=0)  # 空白行
    table = table.iloc[:-1]  # 不包括最后一行注释

    return table


if __name__ == "__main__":
    ua = UserAgent()
    header = {'User-Agent': ua.random}

    year = 2013
    lookup_url = f"http://www.stats.gov.cn/was5/web/search?searchscope=DOCTITLE&channelid=288041&andsen={year}+GDP+%E5%88%9D%E6%AD%A5%E6%A0%B8%E7%AE%97&total=&orsen=&exclude=&presearchword=&templet=&prepage=10&orderby=-DOCRELTIME&andsen2={year}+GDP+%E5%88%9D%E6%AD%A5%E6%A0%B8%E7%AE%97"
    report_url = "http://www.stats.gov.cn/tjsj/zxfb/201501/t20150121_671820.html"

    # lookup_html = get_html(lookup_url, header)
    # report_html = get_html(report_url, header)

    # for testing
    # save_html(report_html)
    with open("./test_htmls/report_html.txt", "r") as file:
        report_html = file.read()

    # titles = get_urls(lookup_html)
    tables = get_table(report_html)
    table = parse_table(tables[0])
    print(table)










