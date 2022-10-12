import ssl
from os import path
from urllib.request import Request, urlopen
import re
from bs4 import BeautifulSoup, NavigableString

url = 'https://www.p9.com.tw/Index.aspx'
file_path = 'csv/alcohol_typ.csv'

def get_alcohol_type():
    if path.exists(file_path):
        return

    req = Request(url)
    context = ssl._create_unverified_context()
    html_page = urlopen(req, context=context).read()

    soup = BeautifulSoup(html_page, 'html.parser')

    alcohol_type = []
    whitespace_pattern = re.compile(r'\s+')
    wine_link_pattern = re.compile(r'/Wine/WineCountry.aspx\?WineTypeId=(\d+)')

    for wineSpan in soup.find_all('span', attrs={'class': 'wineClass'}):
        print(wineSpan)
        if wineSpan.text:
            ch_name = wineSpan.text
            ch_name = re.sub(whitespace_pattern, '', ch_name)
            en_str = wineSpan.next_sibling
            while not isinstance(en_str, NavigableString):
                en_str = en_str.next_sibling

            en_name = en_str.strip()
            en_name = re.sub(whitespace_pattern, '', en_name)

            wine_a = wineSpan.find_parent('a')
            wine_link_match = re.search(wine_link_pattern, wine_a['href'])
            p9_id = wine_link_match.group(1)

            alcohol_type.append((ch_name, en_name, p9_id))


    with open(file_path, 'w') as f:
        f.write('ch_name,en_name,p9_id\n')
        for ch_name, en_name, p9_id in alcohol_type:
            f.write(f"{ch_name},{en_name},{p9_id}\n")


if __name__ == "__main__":
    get_alcohol_type()
