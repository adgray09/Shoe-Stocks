from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

SHOE_ID_KEY = "ID"
SHOE_NAME_KEY = "Shoe"
GOAT_URL_KEY = "GOAT"
STOCKX_URL_KEY = "StockX"


def scrape(driver, url):    
    driver.get(url)

    # soupify
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    return soup

def get_price_from_goat_soup(soup):
    return soup.find('span', {'class': "ProductTitlePaneActions__BuyPrice-l1sjea-4 fZVosI"}).get_text()

def get_price_from_stockx_soup(soup):
    return soup.find("div", {"class": "en-us stat-value stat-small"}).get_text()

def create_driver(): 
    # selenium options
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36")

    # Chrome driver
    driver = webdriver.Chrome('/Users/alexstraphouse/dev/drivers/chromedriver', chrome_options=options)
    # place a wait so that data loads
    driver.implicitly_wait(15)
    return driver

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    return gspread.authorize(creds)

def get_price_records_sheet(client):
    return client.open('shoes').worksheet('price_records')

def get_shoes(client):
    return client.open('shoes').worksheet('shoes').get_all_records()

def add_price_record(sheet, shoe_id, website, price):
    today = date.today()
    current_date = today.strftime("%m/%d/%y")
    row = [current_date, shoe_id, website, price]    
    sheet.append_row(row)

def get_all_prices():
    driver = create_driver()
    client = get_gspread_client()
    shoes = get_shoes(client)
    price_records = get_price_records_sheet(client)
    
    for shoe_data in shoes:
        shoe_id = shoe_data[SHOE_ID_KEY]
        
        # get info from goat
        goat_url = shoe_data[GOAT_URL_KEY]
        goat_results = scrape(driver, goat_url)
        goat_price = get_price_from_goat_soup(goat_results)
        add_price_record(price_records, shoe_id, "GOAT", goat_price)
        # get info from stockx
        stockx_url = shoe_data[STOCKX_URL_KEY]
        stockx_results = scrape(driver, stockx_url)
        stockx_price = get_price_from_stockx_soup(stockx_results)
        add_price_record(price_records, shoe_id, "StockX", stockx_price)

get_all_prices()


