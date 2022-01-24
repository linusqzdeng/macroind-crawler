from playwright.sync_api import Playwright, sync_playwright


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to https://data.eastmoney.com/cjsj/gdp.html
    page.goto("https://data.eastmoney.com/cjsj/gdp.html")

    # Click text=下一页
    page.click("text=下一页")

    # Click a:has-text("3")
    page.click("a:has-text(\"3\")")

    # Click text=下一页
    page.click("text=下一页")

    # Click text=居民消费价格指数(CPI)
    page.click("text=居民消费价格指数(CPI)")
    # assert page.url == "https://data.eastmoney.com/cjsj/cpi.html"

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

