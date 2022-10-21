from sqlalchemy import create_engine
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.options import Options
from time import sleep
from flask import Flask
import sys

db_name = 'database'
db_user = 'username'
db_pass = 'password'
db_host = 'db'
db_port = '5432'

# Connect to the database
db_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
db = create_engine(db_string)

# Flask app
app = Flask(__name__)


def scrape_flats(page):
    """
    Scrape all flats for sale on page
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    url = f"https://www.sreality.cz/hledani/prodej/byty?strana={page}"
    browser.get(url)
    sleep(1.5)
    inner_html = browser.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(inner_html, 'lxml')

    _flats = []
    for flat in soup.findAll('div', attrs={'class': 'property ng-scope'}):
        image_url = flat.find_next('a', attrs={'class': '_2vc3VMce92XEJFrv8_jaeN'}).find_next('img').attrs['src']
        title = flat.find_next('span', attrs={'class': 'name ng-binding'}).text
        _flats.append([title, image_url])
    browser.quit()
    return _flats


def insert_to_flat_sell(_title, _image_url):
    """
    Insert flat to database
    """
    db.execute(f"INSERT INTO flat_sell VALUES ('{_title}','{_image_url}');")


def get_count_database():
    """
    :return: Counts flats in database
    """
    query = "SELECT COUNT(*) FROM flat_sell;"
    result_set = db.execute(query)
    for (r) in result_set:
        return r[0]


def get_flats() -> pd.DataFrame:
    """
    :return: All flats in database
    """
    query = "SELECT * FROM flat_sell"
    flats = db.execute(query)
    flats = pd.DataFrame(flats, columns=['title', 'image_url'])
    return flats


def clear_database():
    """
    :return: Delete all flats in database
    """
    query = f"DELETE FROM flat_sell;"
    db.execute(query)


def create_html() -> str:
    """
    Create simple page
    """
    flats = get_flats()
    flats_html = ""
    for index, flat in flats.iterrows():
        flats_html += f"<div>{flat['title']} <img src=\"{flat['image_url']}\" alt=\"\"></div>"

    html = f"<html><head></head><body>{flats_html}</body></html>"
    return html


@app.route('/')
def __init__():
    print('Application started', file=sys.stderr)

    # Start with clear DB
    clear_database()

    print('Started scraping flats', file=sys.stderr)
    flats = []
    page = 1
    # While loop, if scraping page fail
    while len(flats) < 500:
        flats += scrape_flats(page)
        print(f"Scrapped flats = {len(flats)}", file=sys.stderr)
        if len(flats) / 20 == page:
            page += 1

    # Convert to data frame
    flats = pd.DataFrame(flats, columns=['title', 'image_url'])

    # Insert flats to DB
    for index, flat in flats.iterrows():
        insert_to_flat_sell(_title=flat['title'], _image_url=flat['image_url'])

    print(f"Inserted {get_count_database()} flats to database", file=sys.stderr)
    return create_html()
