import os
import re
from os import path

from bs4 import BeautifulSoup

from utils import get_html, read_csv_as_list

class CountryExtractor:
    def __init__(self, type_id):
        self.type_id = type_id
        self.country_list_url = 'https://www.p9.com.tw/Wine/WineCountry.aspx?WineTypeId=%s' % self.type_id
        self.country_ids_path = f'csv/{self.type_id}/country.csv'

    def get_all_country_ids(self):
        if path.exists(self.country_ids_path):
            return self.read_country_ids()

        url = self.country_list_url
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        regex = f"BrandList\.aspx\?WineTypeId={self.type_id}&CountryId=(\d+)"

        country_ids = []
        for country_a in soup.find_all('a', href=re.compile(regex)):
            country_match = re.match(regex, country_a['href'])
            country_id = country_match.group(1)
            country_ids.append(country_id)

        os.makedirs(os.path.dirname(self.country_ids_path), exist_ok=True)
        with open(self.country_ids_path, 'w') as f:
            for country_id in country_ids:
                f.write(f"{country_id}\n")

        return self.read_country_ids()

    def read_country_ids(self):
        country_id_list = read_csv_as_list(self.country_ids_path)
        country_ids = []
        for row in country_id_list:
            country_ids.append(row[0])

        return country_ids

if __name__ == "__main__":
    extractor = CountryExtractor(1)
    country_ids = extractor.get_all_country_ids()
    print(country_ids)

