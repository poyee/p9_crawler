import os
import re
from os import path

from bs4 import BeautifulSoup

from utils import get_html, read_csv_as_list

type_list_url = 'https://www.p9.com.tw/Wine/WineCountry.aspx?WineTypeId=%s'

def get_all_country_id_by_type(type_id):
    country_ids = []
    file_path = f'csv/{type_id}/country.csv'
    if path.exists(file_path):
        country_id_list = read_csv_as_list(file_path)
        for row in country_id_list:
            country_ids.append(row[0])

        return country_ids

    url = type_list_url % type_id
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    regex = f"BrandList\.aspx\?WineTypeId={type_id}&CountryId=(\d+)"

    for country_a in soup.find_all('a', href=re.compile(regex)):
        country_match = re.match(regex, country_a['href'])
        country_id = country_match.group(1)
        country_ids.append(country_id)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        for country_id in country_ids:
            f.write(f"{country_id}\n")

    return country_id


if __name__ == "__main__":
    country_ids = get_all_country_id_by_type(1)
    print(country_ids)

