import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta


API_URL = "https://www.dccomics.com/proxy/search?page=1&type=comic&startdate={0}&enddate={1}"

def get_timestamps():
    today = date.today()
    tdt = datetime(today.year, today.month, today.day)
    dow_int = int(today.strftime('%w'))
    monday = None
    if dow_int < 1:
        monday = tdt + timedelta(days=1)
    else:
        monday = tdt - timedelta(days=dow_int-1)
    friday = monday + timedelta(days=4)
    print(monday, friday)
    return monday.timestamp(), friday.timestamp()


def get_weekly_url():
    timestamps = get_timestamps()
    return API_URL.format(*timestamps)


def get_data():
    r = requests.get(get_weekly_url())
    print("THE HEADERS: ", r.headers)
    return r.json()

def sanitize_text(txt):
    return txt.replace('&', 'and')

def get_titles():
    data = get_data()['results']
    keys = list(data.keys())
    titles = []
    for k in keys:
        title = sanitize_text(data[k]['fields']['title'][0])
        titles.append(title)
    return titles

def get_title_str():
    return ', '.join(get_titles())
