# -*- coding: UTF-8 -*-

import requests
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup as bs
from anole import UserAgent


def get_html(url, header):
    """Only get GDP urls for the time being"""
    try:
        response = requests.get(url, headers=header)

        if response.status_code == 200:
            print("Get into the page successfully")
            html = response.content.decode('utf-8-sig')
            return html
    except Exception as e:
        print('Something goes wrong...', e)
        return None


def save_html(html):
    "For testing purposes"
    with open("./test_htmls/report_html.txt", "w") as file:
        file.write(html)


def get_urls(html):
    """Get GDP urls from the searching page"""
    soup = bs(html, features='lxml')
    titles = soup.find_all('font', {"class": "cont_tit03"})
    urlstrs = [re.search("urlstr = '(.*?)';", str(title.script)).group(1) for title in titles]

    return urlstrs


def parse_html(html):
    """
    Get main tables from the report

    Params
    ======
    - html: The html text file of webpage

    Returns
    =======
    - table: Dataframe of the GDP growth
    - title: Title of the page
    - dt: Datetime object of the announcement `date`and `time`
    """
    soup = bs(html, features='html5lib')
    table = pd.read_html(soup.prettify(), header=1, index_col=0)[1]

    title = soup.find('h2', class_='xilan_tit').get_text()
    date_info = soup.find('font', class_='xilan_titf').get_text()
    date_str = re.search("时间：(.*)", date_info, flags=re.DOTALL).group(1).strip()
    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')

    return table, title, dt


def parse_table(table):
    table.columns = ['Real GDP', 'YoY (%)']  # 绝对额（亿元）| 比上年同期增长（%）
    table = table.dropna(axis=0)  # 剔除空白行
    table = table.iloc[:-1]  # 不包括最后一行注释
    table = table.astype('float64')

    return table


if __name__ == "__main__":
    ua = UserAgent()
    header = {'User-Agent': ua.random}

    year = 2013
    lookup_url = f"http://www.stats.gov.cn/was5/web/search?searchscope=DOCTITLE&channelid=288041&andsen={year}+GDP+%E5%88%9D%E6%AD%A5%E6%A0%B8%E7%AE%97&total=&orsen=&exclude=&presearchword=&templet=&prepage=10&orderby=-DOCRELTIME&andsen2={year}+GDP+%E5%88%9D%E6%AD%A5%E6%A0%B8%E7%AE%97"
    # report_url = "http://www.stats.gov.cn/tjsj/zxfb/201501/t20150121_671820.html"

    # lookup_html = get_html(lookup_url, header)
    # report_url = get_urls(lookup_html)[0]
    # report_html = get_html(report_url, header)

    # ======= for testing ======= #
    # save_html(report_html)
    with open("./test_htmls/report_html.txt", "r") as file:
        report_html = file.read()

    tables, title, dt = parse_html(report_html)
    table = parse_table(tables)

    print(title)
    print(dt)
    print(table)










