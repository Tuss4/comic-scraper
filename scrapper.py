from bs4 import BeautifulSoup
import urllib.request


ADDR = "https://www.marvel.com/comics/calendar/week/2019-02-24?byZone=marvel_site_zone&offset=0&tab=comic&formatType=issue&isDigital=0&byType=date&dateStart=2019-02-24&dateEnd=2019-03-02&orderBy=release_date+desc&limit=300&count=41"


def get_the_latest_titles():
    page = urllib.request.urlopen(ADDR).read()
    soup = BeautifulSoup(page, 'html.parser')
    titles = soup.findAll('h5')
    for title in titles:
        print(title.text.strip())
    return


if __name__ == "__main__":
    get_the_latest_titles()
