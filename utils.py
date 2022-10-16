import csv
from urllib.request import Request, urlopen
import ssl


def read_csv_as_list(path, delimiter=','):
    with open(path, newline='\n') as f:
        reader = csv.reader(f, delimiter=delimiter)
        return list(reader)

def write_to_csv(path, list):
    with open(path, "w", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerows(list)

def get_html(url):
    req = Request(url)
    print(f'fetch {url}')
    context = ssl._create_unverified_context()
    return urlopen(req, context=context).read()
