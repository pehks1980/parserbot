
import csv

URL = "https://auto.ru/moskva/cars/used/"

URLS = [
    'https://auto.ru/sankt-peterburg/cars/used/',
    'https://auto.ru/moskva/cars/used/',
    'https://auto.ru/nizhniy_novgorod/cars/used/',
    'https://auto.ru/ekaterinburg/cars/used/',
    'https://auto.ru/kaliningrad/cars/used/',
]

URL_PARAM = '?sort=fresh_relevance_1-desc&page='

URL_PARAMS = [
    '?sort=fresh_relevance_1-desc&page='
]

HOST = 'https://auto.ru'

HOST_TITLE = 'Авто.ру: купить, продать и обменять машину'

FILE = 'cars.csv'
FILE_NAME = 'cars'

LOG = 'err_log.txt'

DEFAULT_PIC = 'https://default.pic'

USERAGENTS = 'useragents.txt'
USERPROXIES = 'proxies.txt'

mp_adv_counter = 0

useragents = []
userproxies= []

HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'accept': '*/*',
    }

# dump collected dict data to csv
def save_csv1(DATA, path):
    with open(path, 'w') as f_n:  # write from dict
        fieldnames1 = list(DATA[0].keys())
        F_N_WRITER = csv.DictWriter(f_n, fieldnames=fieldnames1,
                                    quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
        # take 1st itme's keys as fieldnames
        F_N_WRITER.writeheader()  # write them down
        # print('header-->',fieldnames1)

        for d in DATA:
            #    print ('row-->',d)
            F_N_WRITER.writerow(d)


def read_csv1(path):
    all_cars = []
    with open(path, 'r') as f_n:  # ordered dict #QUOTE NONNUMERIC in READ mode gets didgts in '1230.0' format
        F_N_READER = csv.DictReader(f_n, quoting=csv.QUOTE_MINIMAL, delimiter=';')
        for row in F_N_READER:
            row['price'] = int(row['price'])  # change type on fly -)
            row['production_date'] = int(row['production_date'])
            all_cars.append(row)

    return all_cars


