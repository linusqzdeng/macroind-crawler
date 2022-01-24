# -*- coding: UTF-8 -*-
# created on 2022-01-12 17:33
# author @Qizhong Deng
# tested by python 3.8.6


import datetime
import re
import pandas as pd

from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright

# 显示所有列，所有行
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def get_html(url):
    """抓取传入url页面并返回html"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)  # 等待网页加载

        for i in range(4):
            try:
                html = bs(page.content(), features='lxml')
                print('Get into the website successfully!')

                # For testing
                with open(f"./test_htmls/eastmoney_html{i}.txt", 'w') as file:
                    file.write(html.prettify())

                page.click("text=下一页")
                page.wait_for_timeout(1000)  # 等待网页加载

            except Exception as e:
                print(e)
                break

        browser.close()


def parse_html(html):
    """Extract tables from the html"""
    table = pd.read_html(html, header=[0, 1], index_col=0)[0]

    # convert % object to float type
    for col in table.columns:
        try:
            table[col] = table[col].str.rstrip('%').astype('float64')
        except AttributeError:
            continue

    return table


def rename_idx(idx):
    output = ''.join(re.findall('\d', idx))
    year = output[:4]
    quater = output[-1:]
    new_idx = year + 'Q' + quater

    return new_idx


def my_pct_change(col: str):
    """Customised percentage change func"""
    pass


if __name__ == "__main__":
    url = 'https://data.eastmoney.com/cjsj/gdp.html'
    # html = get_html(url)

    # construct the dataframe
    gdp = pd.DataFrame()
    for i in range(4):
        with open(f'test_htmls/eastmoney_html{i}.txt', 'r') as file:
            html = file.read()
            table = parse_html(html)
            table = table.rename(columns={'绝对值  (亿元)': '累计值', '同比  增长': '累计同比'})
            gdp = pd.concat([gdp, table], axis=0)


    # rename the index
    idx_series = pd.Series(gdp.index).apply(rename_idx)
    gdp.index = idx_series

    # extract data by years
    gdp['year'] = gdp.index.str[:4]
    gdp['quater'] = gdp.index.str[-1:]
    year_range = gdp['year'].unique()
    quater_range = gdp['quater'].unique()

    # calculate gdp for current quater (non-cum)
    main_idx = set([col[0] for col in gdp.columns.values[:-2]])  # ignore `year`, `quater`
    for year in year_range:
        year_gdp = gdp[gdp['year'] == year]

        for idx in main_idx:
            year_gdp[(idx, '本季值')] = year_gdp.loc[:, (idx, '累计值')].diff(-1).fillna(year_gdp[idx, '累计值'])
            year_gdp = year_gdp.sort_index(axis=1)
            gdp.loc[gdp['year'] == year, (idx, '本季值')] = year_gdp[(idx, '本季值')]

    gdp = gdp.sort_index(axis=1)

    # calculate QoQ change
    for quater in quater_range:
        quater_gdp = gdp[gdp['quater'] == quater]

        for idx in main_idx:
            quater_gdp[(idx, '本季同比')] = quater_gdp.loc[:, (idx, '本季值')].pct_change(-1).mul(100).fillna(quater_gdp[idx, '累计同比'])
            quater_gdp = quater_gdp.sort_index(axis=1)
            gdp.loc[gdp['quater'] == quater, (idx, '本季同比')] = quater_gdp[(idx, '本季同比')]

    gdp = gdp.sort_index(axis=1)

    gdp = gdp.round(1)
    gdp = gdp.drop(['year', 'quater'], axis=1)
    gdp.columns = ['_'.join(col).strip() for col in gdp.columns.values]  # flatten the multi-col index
    gdp.to_csv('./data/gdp.csv', index=True, index_label='季度')
    
