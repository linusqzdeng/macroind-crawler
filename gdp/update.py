# Check if the GDP data has been updated

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright
from eastmoney import get_html, parse_html



if __name__ == "__main__":
    url = 'https://data.eastmoney.com/cjsj/gdp.html'
    html = get_html(url)
    table = parse_html(html)
    print(table)