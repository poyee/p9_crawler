import os
import re
import traceback
from os import listdir

import mysql.connector

from alcohol_brand import BrandExtractor
from alcohol_country import CountryExtractor
from utils import read_csv_as_list


class AlcoholDbUpdater:
    def __init__(self):
        self.connect = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            port=3308,
            password='drunk',
            database='alcohol'
        )

    def update_brand(self, brand):
        print(brand)


    def update_types(self):
        sql = 'INSERT IGNORE INTO alcohol_type(ch_name, en_name, id)' \
              'VALUES (%s, %s, %s)' \


        with self.connect.cursor() as cursor:
            alcohol_types = read_csv_as_list(f'csv/alcohol_typ.csv')
            cursor.executemany(sql, alcohol_types)
            self.connect.commit()

    def update_countries(self, country_ids):
        sql = 'INSERT IGNORE INTO alcohol_country(id)' \
              'VALUES (%s)' \

        data = []
        for country_id in country_ids:
            data.append([country_id])

        with self.connect.cursor() as cursor:
            cursor.executemany(sql, data)
            self.connect.commit()

    def update_brands(self, type_id, country_id):
        path = f'csv/{type_id}/{country_id}/brand.csv'
        brands = read_csv_as_list(path)

        data = []
        for brand in brands:
            brand = brand[:-1]
            brand.append(country_id)
            data.append(brand)

        sql = 'INSERT IGNORE INTO alcohol_brand(id, ch_name, en_name, country_id)' \
              'VALUES (%s, %s, %s, %s)' \

        with self.connect.cursor() as cursor:
            cursor.executemany(sql, data)
            self.connect.commit()

    def update_alcohols(self, type_id, brand_id, alcohols):
        sql = """INSERT IGNORE INTO brand_alcohol(id, ch_name, en_name, raw_type, produce_year, production_region, 
              volume, abv, manufacturer, ingredient, grape_type, limitation,
              alcohol_type_id, alcohol_brand_id)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        abv_regex = re.compile(r'([\d\.]+)\s*%')
        volume_regex = re.compile(r'(d+)\s*ml')
        data = []
        for alcohol in alcohols:
            # print(alcohol)
            # abv = alcohol[7]
            # abv_match = re.match(abv_regex, abv)
            # if abv_match:
            #     alcohol[7] = float(abv_match.group(1))
            # else:
            #     alcohol[7] = 0

            # volume = alcohol[6]
            # volume_match = re.match(volume_regex, volume)
            # if volume_match:
            #     alcohol[6] = int(volume_match.group(1))
            # else:
            #     alcohol[6] = 0

            alcohol.append(type_id)
            alcohol.append(brand_id)
            data.append(alcohol)

        with self.connect.cursor() as cursor:
            cursor.executemany(sql, data)
            self.connect.commit()

def update_db_by_type(type_id):
    db_updater = AlcoholDbUpdater()

    alcohol_regex = re.compile('alcohol_(\d+).csv')

    type_id_dir = f'csv/{type_id}'
    country_ids = get_id_files(type_id_dir)
    db_updater.update_countries(country_ids)

    for country_id in country_ids:
        country_dir = f'{type_id_dir}/{country_id}'

        db_updater.update_brands(type_id, country_id)

        for alcohol_file in os.listdir(country_dir):
            match = re.match(alcohol_regex, alcohol_file)
            if match:
                brand_id = match.group(1)
                alcohols = read_csv_as_list(f'{country_dir}/{alcohol_file}', delimiter=';')
                db_updater.update_alcohols(type_id, brand_id, alcohols)



def get_id_files(dir_path):
    return [f for f in listdir(dir_path) if f.isnumeric()]

def update_types():
    updater = AlcoholDbUpdater()
    updater.update_types()


if __name__ == "__main__":
    # update_types()
    update_db_by_type(2)
