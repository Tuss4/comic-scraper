from bs4 import BeautifulSoup
import urllib.request
from datetime import timedelta, date
import json


DATE_FMT = "%Y-%m-%d"


ADDR = "https://www.marvel.com/comics/calendar/week/{0}?byZone=marvel_site_zone&offset=0&tab=comic&formatType=issue&isDigital=0&byType=date&dateStart={1}&dateEnd={2}&orderBy=release_date+desc&limit=300&count=41"


def get_sun_to_sat():
    today = date.today()
    dow_int = int(today.strftime('%w'))
    sunday = None
    if dow_int == 0:
        sunday = date.today()
    else:
        sunday = date.today - timedelta(days=dow_int)
    saturday = sunday + timedelta(days=6)
    fmt_sun = sunday.strftime(DATE_FMT)
    fmt_sat =  saturday.strftime(DATE_FMT)
    return fmt_sun, fmt_sun, fmt_sat


def get_the_latest_titles():
    url = ADDR.format(*get_sun_to_sat())
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page, 'html.parser')
    titles = soup.findAll('h5')
    latest = [title.text.strip() for title in titles]
    return latest


def main_handler(event, context):
    return {
        'statusCode': 200,
        'body': dict(latest_comics=get_the_latest_titles())
    }
