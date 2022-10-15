import os
import re
from os import path

from bs4 import BeautifulSoup

from utils import get_html, read_csv_as_list

brand_list_url_format = 'https://www.p9.com.tw/Wine/BrandList.aspx?WineTypeId=%s&CountryId=%s'


class BrandExtractor:
    def __init__(self, type_id, country_id):
        self.type_id = type_id
        self.country_id = country_id
        self.brand_list_url = brand_list_url_format % (type_id, country_id)
        self.brand_list_file_path = f'csv/{type_id}/{country_id}/brand.csv'

    def get_all_brands(self):
        if path.exists(self.brand_list_file_path):
            return self.read_brand_as_list()

        html = get_html(self.brand_list_url)
        soup = BeautifulSoup(html, 'html.parser')

        # <a class="a9" href="ProductList.aspx?BrandId=56&WineTypeId=1&AreaId=1">卡爾里拉 Caol Ila(8)</a>
        href_regex = f"ProductList\.aspx\?BrandId=(\d+)&WineTypeId={self.type_id}&AreaId=-?\d+"
        name_regex = re.compile(r"[^\(\)]+\((\d+)\)")

        brands = []
        for brand_a in soup.find_all('a', href=re.compile(href_regex)):
            branch_match = re.match(href_regex, brand_a['href'])
            brand_id = branch_match.group(1)

            # 卡爾里拉 Caol Ila(8)
            brand_text = brand_a.text
            brand_name_match = re.match(name_regex, brand_text)
            if brand_name_match:
                alcohol_number = brand_name_match.group(1)
                brand_name = re.sub(r"\(\d+\)", '', brand_text)


                brand_names = brand_name.split(' ')

                if len(brand_names) > 1:
                    ch_name = brand_names[0]
                    en_name = brand_names[1]
                else:
                    ch_name = ''
                    en_name = brand_names[0]

                brands.append((brand_id, ch_name, en_name, alcohol_number))

        os.makedirs(os.path.dirname(self.brand_list_file_path), exist_ok=True)
        with open(self.brand_list_file_path, 'w') as f:
            for brand_id, ch_name, en_name, alcohol_number in brands:
                f.write(f"{brand_id},{ch_name},{en_name},{alcohol_number}\n")

        return brands

    def read_brand_as_list(self):
        return read_csv_as_list(self.brand_list_file_path)

if __name__ == "__main__":
    extractor = BrandExtractor(1, 1)
    brands = extractor.get_all_brands()
    print(brands)
