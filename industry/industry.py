# -*- coding: UTF-8 -*-
# create on 2022-01-18 16:31
# author @Qizhong Deng

import pandas as pd
import requests
import re
from datetime import datetime
from anole import UserAgent
from bs4 import BeautifulSoup as bs
from index import INDEX_MAP

# 显示所有列，所有行
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


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


def parse_search_page(html):
    """获取检索页面所有工业增长值相关url"""
    soup = bs(html, features='lxml')
    titles = soup.find_all('font', {"class": "cont_tit03"})
    target_urls = [re.search("urlstr = '(.*?)';", str(title.script)).group(1) for title in titles]
    next_page_url = soup.find('a', class_='next-page').get('href')

    return target_urls, next_page_url


def parse_html(html):
    """Extract tables and release date from the html"""
    if html is None:  # might be a pdf page
        return

    soup = bs(html, features='lxml')
    table = pd.read_html(html, index_col=1, na_values='…')[1]
    table.columns = [table.iloc[0], table.iloc[1]]

    # take first two rows as multi-col index
    table = table.iloc[2:].reset_index(drop=False)
    table.set_index(1, inplace=True)
    table = table.iloc[:, 1:]
    print(table)

    # extract release date
    title = soup.find('h2', class_='xilan_tit').get_text()
    date_info = soup.find_all('font',
            {'style': 'float:left;width:560px;text-align:right;margin-right:60px;'})[0].get_text()
    date_str = re.search("时间：(.*)", date_info, flags=re.DOTALL).group(1).strip()
    release_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M').date()

    # extract report date
    report_dt = datetime(release_dt.year - (release_dt.month == 1), release_dt.month - 1 or 12, 1).date()  # 上个月1号
    # report_dt = re.search("(\d+)年(\d+)", title).group(1, 2)
    # report_dt = datetime.strptime(''.join(report_dt), '%Y%m').date()

    return title ,table, release_dt, report_dt


def parse_table(table, idx_map: dict):
    """
    Remove unneccessary rows and convert
    undesirable string format to float
    """
    # 去除nan字段
    nan_rows = table.isnull().all(axis=1)
    table = table.loc[~nan_rows]

    # 全角->半角转换
    idx = table.index.to_list()
    idx = DBC2SBC(idx)

    # 根据提前定义字典统一字段名称
    for i, ix in enumerate(idx):
        if ix in idx_map.keys():
            idx[i] = idx_map[ix]

    # 去除'其中：'
    for i, ix in enumerate(idx):
        try:
            idx[i] = re.search(':([\u4e00-\u9fa5].*)', ix).group(1)
        except AttributeError:
            idx[i] = ix

    table.index = idx

    # 重命名列
    try:
        rename_cols = ['本月值', '本月同比', '累计值', '累计同比']
        if len(table.columns) == len(rename_cols) + 1:
            table = table.iloc[:, 1:]
        table.columns = rename_cols
    except ValueError:
        rename_cols = ['累计值', '累计同比']
        if len(table.columns) == len(rename_cols) + 1:
            table = table.iloc[:, 1:]
        table.columns = rename_cols

    # convert string to float
    for col in table.columns:
        table[col] = table[col].str.extract('((\-|\+)?\d+(\.\d+)?)')[0]
        table[col] = table[col].astype('float64')

    return table


def DBC2SBC(ustring_list):
    '''全角转半角'''
    ustring_list = list(map(lambda x: x.strip(), ustring_list))
    normal_str_list=[]
    for i in range(len(ustring_list)):
        rstring = ""
        for uchar in ustring_list[i]:
            if uchar == " ":  # ignore empty space
                continue

            inside_code = ord(uchar)
            if inside_code == 0x3000:
                inside_code = 0x0020
            else:
                inside_code -= 0xfee0
                if not (0x0021 <= inside_code and inside_code <= 0x7e):
                    rstring += uchar
                    continue
                rstring += chr(inside_code)
        normal_str_list.append(rstring)

    return normal_str_list


def redesign_table(table, release_dt, report_dt):
    df_dict = {'公布日': release_dt, '截止日': report_dt}

    for col in table.columns:
        for idx in table.index:
            data = table.loc[idx, col]
            attr_name = '_'.join([idx, col])
            df_dict[attr_name] = data

    df = pd.DataFrame(df_dict, index=[0])
    df = df.dropna(axis=1)

    return df


def test():
    # ===== For testing ===== #
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    savepath = '../test_htmls/industry_html.txt'
    url = 'http://www.stats.gov.cn/tjsj/zxfb/201603/t20160312_1330113.html'  # for testing
    # html = get_html(url, headers=headers)
    # with open(savepath, 'w') as file:
        # file.write(html)
    with open(savepath, 'r') as file:
        html = file.read()

    try:
        title, table, release_dt, report_dt = parse_html(html)
        table = parse_table(table, INDEX_MAP)
        output = redesign_table(table, release_dt, report_dt)
    except Exception as e:
        print('===Errors detected:', e)
        print(f'Skipping the page {title}')

    output.to_csv('20160201.csv', index=False)

    print(output.T)
    

def main(page_num: int, bypass_pages: list=None):
    """
    Main loop of the crawler

    Params
    ------
    - page_num: int
        Total number of page to scrape 
    - bypass_pages: list
        List of page number that you widh the program to ignore 
    """
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    search_page_url = 'http://www.stats.gov.cn/was5/web/search?page=1&channelid=288041&orderby=-DOCRELTIME&was_custom_expr=DOCTITLE%3D%28like%28%E5%B7%A5%E4%B8%9A%E5%A2%9E%E5%8A%A0%E5%80%BC%29%2Fsen%29&perpage=10&outlinepage=10'
    schema = "http://www.stats.gov.cn/was5/web/"
    skip_pages = []
    
    for i in range(page_num):
        results = pd.DataFrame()

        print(f'Fetching urls in page {i + 1}...')
        search_page_html = get_html(search_page_url, headers)
        urllist, next_page_url = parse_search_page(search_page_html)
        search_page_url = schema + next_page_url

        # 跳过页面
        if bypass_pages and i + 1 in bypass_pages:
            print(f'Bypassing page {i + 1}')
            continue

        for n, url in enumerate(urllist[:2]):

            print(f'Page number: {n + 1}')
            table_html = get_html(url, headers)
            title, table, release_dt, report_dt = parse_html(table_html)

            try:
                table = parse_table(table, INDEX_MAP)
                output = redesign_table(table, release_dt, report_dt)
                results = pd.concat([results, output], ignore_index=True)
            except Exception as e:
                print('===Errors detected:', e)
                print(f'Skipping the page {title}')
                skip_pages.append(title)

                continue

        print("Collected all tables, going to next page...")
        results.to_csv(f'../data/industry_growth_page{i + 1}.csv', index=False)

    print('All done!')


if __name__ == "__main__":
    bypass_pages = list(range(1, 11))
    # main(11, bypass_pages=bypass_pages)
    test()

    


