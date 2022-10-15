import os
import re
import time
from dataclasses import dataclass
from os import path

from bs4 import BeautifulSoup

from alcohol_brand import get_all_brands_by_type_and_country
from alcohol_country import get_all_country_id_by_type
from utils import get_html, read_csv_as_list

alcohol_list_url = 'https://www.p9.com.tw/Wine/ProductList.aspx?BrandId=%s&WineTypeId=%s'
alcohol_url = 'https://www.p9.com.tw/Wine/ProductDetail.aspx?id=%s'

def get_alcohol_ids_by_type_by_brand(type_id, country_id, brand_id):
    file_path = f'csv/{type_id}/{country_id}/{brand_id}/alcohol_id.csv'
    if path.exists(file_path):
        return read_csv_as_list(file_path)

    url = alcohol_list_url % (brand_id, type_id)
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    href_regex = re.compile(r'ProductDetail\.aspx\?id=(\d+)')
    alcohol_ids = []
    for alcohol_a in soup.find_all('a', attrs={'href': href_regex, 'class': 'a11'}):
        alcohol_id = re.match(href_regex, alcohol_a['href']).group(1)
        alcohol_ids.append(alcohol_id)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        for alcohol_id in alcohol_ids:
            f.write(f"{alcohol_id}\n")

    return alcohol_ids


def get_alcohols_by_type_by_brand(type_id, country_id, brand_id):
    file_path = f'csv/{type_id}/{country_id}/{brand_id}/alcohol.csv'
    if path.exists(file_path):
        return read_csv_as_list(file_path)

    alcohol_ids = get_alcohol_ids_by_type_by_brand(type_id, country_id, brand_id)
    alcohols = []

    for alcohol_id in alcohol_ids:
        if isinstance(alcohol_id, list):
            alcohol_id = alcohol_id[0]

        alcohol = get_alcohol_by_id(alcohol_id)
        alcohols.append(alcohol)

    with open(file_path, 'w') as f:
        for alcohol in alcohols:
            f.write(f"{';'.join(alcohol)}\n")

    return alcohols


def get_alcohol_by_id(alcohol_id):
    url = alcohol_url % alcohol_id
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')

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

    return ret

def get_all_alcohols_by_type(type_id):
    country_ids = get_all_country_id_by_type(type_id)
    for country_id in country_ids:
        brands = get_all_brands_by_type_and_country(type_id, country_id)

        for brand in brands:
            get_alcohols_by_type_by_brand(type_id, country_id, brand[0])

if __name__ == "__main__":
    get_all_alcohols_by_type(1)
