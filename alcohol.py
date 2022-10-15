import os
import re
import time
from dataclasses import dataclass
from os import path

from bs4 import BeautifulSoup

from alcohol_brand import get_all_brands_by_type_and_country, BrandExtractor
from alcohol_country import get_all_country_id_by_type, CountryExtractor
from utils import get_html, read_csv_as_list

alcohol_list_url_format = 'https://www.p9.com.tw/Wine/ProductList.aspx?BrandId=%s&WineTypeId=%s'
alcohol_url_format = 'https://www.p9.com.tw/Wine/ProductDetail.aspx?id=%s'

class AlcoholExtractor:
    def __init__(self, type_id, country_id, brand_id):
        self.type_id = type_id
        self.country_id = country_id
        self.alcohol_list_url = alcohol_list_url_format % (brand_id, type_id)
        self.alcohol_ids_file_path = f'csv/{type_id}/{country_id}/alcohol_id_{brand_id}.csv'
        self.alcohols_file_path = f'csv/{type_id}/{country_id}/alcohol_{brand_id}.csv'

    def get_alcohols(self):
        if path.exists(self.alcohols_file_path):
            return read_csv_as_list(self.alcohols_file_path)

        alcohol_ids = self.get_alcohol_ids()
        alcohols = []

        for alcohol_id in alcohol_ids:
            alcohol = self.get_alcohol_by_id(alcohol_id)
            alcohols.append(alcohol)

        with open(self.alcohols_file_path, 'w') as f:
            for alcohol in alcohols:
                f.write(f"{';'.join(alcohol)}\n")

        return alcohols

    def get_alcohol_ids(self):
        if path.exists(self.alcohol_ids_file_path):
            return read_csv_as_list(self.alcohol_ids_file_path)

        url = self.alcohol_list_url
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        href_regex = re.compile(r'ProductDetail\.aspx\?id=(\d+)')
        alcohol_ids = []
        for alcohol_a in soup.find_all('a', attrs={'href': href_regex, 'class': 'a11'}):
            alcohol_id = re.match(href_regex, alcohol_a['href']).group(1)
            alcohol_ids.append(alcohol_id)

        os.makedirs(os.path.dirname(self.alcohol_ids_file_path), exist_ok=True)
        with open(self.alcohol_ids_file_path, 'w') as f:
            for alcohol_id in alcohol_ids:
                f.write(f"{alcohol_id}\n")

        return self.read_alcohol_ids()

    def read_alcohol_ids(self):
        alcohol_id_list = read_csv_as_list(self.alcohol_ids_file_path)
        alcohol_ids = []
        for row in alcohol_id_list:
            alcohol_ids.append(row[0])

        return alcohol_ids

    def get_alcohol_by_id(self, alcohol_id):
        url = alcohol_url_format % alcohol_id
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        ch_name = soup.find('a', id='ContentBody_hlkProductName').text
        en_name = soup.find('a', id='ContentBody_hlkEngName').text

        attr_to_regex = {
            'type': re.compile(r'類\s+別：(.*)'),
            'year': re.compile(r'年\s+份：(.*)'),
            'region': re.compile(r'產\s+區：(.*)'),
            'volume': re.compile(r'容\s+量：(.*)'),
            'abv': re.compile(r'酒精成份：(.*)'),
            'manufacturer': re.compile(r'製\s+造\s+商：(.*)'),
            'ingredient': re.compile(r'主要原料：(.*)'),
            'grape_type': re.compile(r'葡萄種類：(.*)'),
            'limit': re.compile(r'限\s+量：(.*)'),
        }

        alcohol_dict = {}
        for attr in attr_to_regex:
            alcohol_dict[attr] = ''


        for attribute_td in soup.findAll('td', {'class': 'txtsize_011'}):
            text = attribute_td.text
            for attr in attr_to_regex:
                match = re.match(attr_to_regex[attr], text)
                if match:
                    alcohol_dict[attr] = match.group(1)
                    break

        ret = list(alcohol_dict.values())
        ret.insert(0, alcohol_id)
        ret.insert(1, ch_name)
        ret.insert(2, en_name)

        return ret

def get_all_alcohols_by_type(type_id):
    country_extractor = CountryExtractor(type_id)
    country_ids = country_extractor.get_all_country_ids()
    print(country_ids)
    for country_id in country_ids:
        brand_extractor = BrandExtractor(type_id, country_id)
        brands = brand_extractor.get_all_brands()

        for brand in brands:
            alcohol_extractor = AlcoholExtractor(type_id, country_id, brand[0])
            alcohol_extractor.get_alcohol_ids()

if __name__ == "__main__":
    get_all_alcohols_by_type(2)
