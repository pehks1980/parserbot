# imports
import sys
from datetime import datetime
from random import choice, uniform, randint
from time import sleep


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import os

from ._common import *

# make a list of intersting links
# count = pages number


def get_all_links(url,url_params,page_idx,page_count):

    links = []

    for page in range(page_idx, page_idx + page_count):
        # https: // auto.ru / moskva / cars / used /?sort = fresh_relevance_1 - desc & page = 2
        link = f'{url}{url_params}{page}'

        links.append(link)

    return links


# get ads from one page
def get_items(id,soup):
    items = []

    try:
       # items = soup.find('div', class_='ListingCars-module__list')
        #updated 16.07.2020 slight change of structure of site
        items = soup.findAll('div', class_='ListingCars-module__listingItem')
    except Exception as e:
        with open(LOG, "a", encoding="utf8") as file:
            file.write(f'task={id} str(e) auto.ru class = ListingCars-module__list\n')
    return items


# get data from a html page
def get_content(id,html, abs_path):
    soup = BeautifulSoup(html, 'html.parser')

    #print(soup.text)


    items = get_items(id,soup)

    cars = []
    # find all tags 'meta' and put it in dict elem
    try:
        for item in items:
            # make a new line dict
            elem = {}
            name_t = False
            for i in item.findAll('meta'):
                # print(i.get("content", None), i.get("itemprop", None))
                # only one tage 'name' needs to be parsed another is skept
                if i.get("itemprop", None) == 'name' and name_t == False:
                    elem[f'{i.get("itemprop", None)}'] = f'{i.get("content", None)}'
                    name_t = True
                # other then name goes directly copied to dict elem
                if i.get("itemprop", None) != 'name':
                    elem[f'{i.get("itemprop", None)}'] = f'{i.get("content", None)}'

            # add cars if anything was parsed
            if elem:
                # recode to format fields in model (types as well)
                #additional check for int data is needed
                if elem['price'] == 'None':
                    elem['price'] = '0'

                if elem['productionDate']=='None':
                    elem['productionDate'] = '0'

                cars.append(
                    {'title': elem['name'],
                     'ad_link': elem['url'],
                     'img_link': elem['image'],
                     'price': int(elem['price']),
                     'price_currency': elem['priceCurrency'],
                     'transmission': elem['vehicleTransmission'],
                     'production_date': int(elem['productionDate']),
                     'fuel_type': elem['fuelType'],
                     'color': elem['color'],
                     'brand': elem['brand'],
                     }
                )
                # cars.append(elem)

                # group_id = models.ForeignKey(CarAdGroup, on_delete=models.CASCADE)
                # status = models.BooleanField(verbose_name='Статус', blank=True, default=True)  # активно/неактивно
                #
                # title = models.TextField(verbose_name='Заголовок объявления')
                # price = models.PositiveIntegerField(verbose_name='Цена', default=0)
                # price_currency = models.CharField(verbose_name='Валюта', max_length=3, blank=True)
                #
                # ad_link = models.TextField(verbose_name='Ссылка на объявление', blank=True)
                # img_link = models.TextField(verbose_name='Ссылка на изображение', blank=True)
                #
                # transmission = models.CharField(verbose_name='Тип трансмиссии', max_length=24, blank=True)
                #
                # production_date = models.PositiveIntegerField(verbose_name='Дата выпуска', default=0)
                #
                # fuel_type = models.CharField(verbose_name='Тип топлива', max_length=24, blank=True)
                # color = models.CharField(verbose_name='Цвет кузова', max_length=24, blank=True)
                # brand = models.CharField(verbose_name='Brand name', max_length=24, blank=True)

                # "brand" "RENAULT"
                # "color" "серый"
                # "fuelType" "бензин"
                # "image" "https://avatars.mds.yandex.net/get-autoru-vos/2165505/a2c808e6c99167e9f1724e45324d7fd1/320x240"
                # "name"    "Renault Logan I" <> "title"
                # "productionDate" "2004"
                # "vehicleTransmission" "механическая"
                # "price" "209000"
                # "priceCurrency" "RUB"
                # "url" "https://auto.ru/cars/used/sale/renault/logan/1098526412-3b4ec908/"

    except Exception as e:
        with open(f'{abs_path}/{LOG}', "a", encoding="utf8") as file:
            file.write(f'{datetime.now()} task={id} {str(e)} auto.ru meta(itemprop, content) {item}\n')
            return []

    # print(cars)
    print(f' task={id} получено {len(cars)} обьявлений')
    return cars

    # print (cars)


# setup and get chrome driver
def get_driver(id,ch_options, abs_path):
    try:
        # abs_path='/home/user/stazh/parserbot/parserapp1'
        exec_path = str(abs_path).replace('parserbot/parserapp1', '') + 'venv/bin/chromedriver'
        print(exec_path)
        driver = webdriver.Chrome(options=ch_options, executable_path=exec_path)
        # driver = webdriver.Chrome(options=ch_options)
    except Exception as exception:
        # Output unexpected Exceptions.
        with open(f'{abs_path}/{LOG}', "a", encoding="utf8") as file:
            file.write(f'{datetime.now()} task={id}  : chrome driver : {str(exception)} \n')
            print(f'task={id}  : chrome driver : {str(exception)}')
            # driver.quit()
            sys.exit(1)

    try:
        driver.get(HOST)
        # must be 'Авто.ру: купить, продать и обменять машину'
        #wait for 9 seconds this is the test for proxy - it should open first page with page 'title'
        driver.implicitly_wait(9)
        # check if first page is opened
        assert HOST_TITLE in driver.title
    except AssertionError as error:
        driver.quit()
        print(f'task={id} driver or proxy is dead.. ({ch_options.arguments[0]})')
        # exit with None
        return None
    except Exception as exception:
        # Output unexpected Exceptions.
        with open(f'{abs_path}/{LOG}', "a", encoding="utf8") as file:
            file.write(f'{datetime.now()} task={id}  : chrome driver : {str(exception)} \n')

        print(exception)
        # driver.quit()
        sys.exit(1)

    return driver

def setup_driver(id,abs_path,use_proxy,use_headless):
    # web_driver - chromium/chromedriver should be installed to latest version, via snapd
    # list of open proxy servers
    print('abs=', abs_path)
    userproxies = open(f'{abs_path}/{USERPROXIES}', 'r').read().split('\n')

    # prepare webdriver ch_options
    ch_options = webdriver.ChromeOptions()
    # options.binary_location = '/usr/bin/google-chrome-unstable'

    # setting for proxy
    if use_proxy == True:
        index_proxy = randint(0, len(userproxies) - 1)
        proxy = userproxies[index_proxy]
        used_proxy_index = index_proxy
        ch_options.add_argument(f'--proxy-server={proxy}')
        print(f'task={id} webdriver chrome is using proxy {proxy} ...')

    ch_options.add_argument("--no-sandbox");
    # hidden winodow
    if use_headless == True:
        ch_options.add_argument('headless')

    # set the window size
    ch_options.add_argument('window-size=1200x600')
    # initialize the driver

    # chromedriver and chrome version needs to be exact chr_install.sh gets latest driver from google
    # snap install chromium gets latest snap for chromium
    # shuld correspond current version of chrome 1229 which can be taken when chrome://version
    # ' Executable Path	/snap/chromium/1229/usr/lib/chromium-browser/chrome <<<<<<<<'
    ch_options.add_argument('user-data-dir=/home/user/snap/chromium/1229/.config/chromium/Default')
    # ch_options.add_argument('/home/user/snap/chromium/common/chromium/Default')
    ch_options.add_experimental_option('useAutomationExtension', False)

    # as per stack of recommendation
    ch_options.add_argument("disable-infobars")
    ch_options.add_argument("--disable-extensions")
    ch_options.add_argument("--disable-gpu")
    ch_options.add_argument("--disable-dev-shm-usage")

    # print (ch_options)
    driver = None

    for _ in range(len(userproxies)):  #
        driver = get_driver(id, ch_options, abs_path)
        if driver != None:
            # target page opened successfully
            break
        else:
            if use_proxy == True:
                # proxy error change proxy
                # remove bad proxy from the list
                del userproxies[used_proxy_index]

                if userproxies == []:
                    print(f' task={id} exited : used all proxies, please update proxies list with alive')
                    # sys.exit(0)
                    return []  # exit with 0
                # get another from the list
                index_proxy = randint(0, len(userproxies) - 1)
                proxy = userproxies[index_proxy]

                used_proxy_index = index_proxy

                ch_options.arguments[0] = (f'--proxy-server={proxy}')
                print(f' task={id} webdriver chrome is using proxy {proxy} ...')

    if use_proxy and driver != None:
        # wait up to 10 seconds for the elements to become available
        driver.implicitly_wait(4)
        print(f' task={id} proxy is ok ({proxy})')

    if driver:
        print(f'task={id} chrome driver successfully started.')
    else:
        print(f'task={id} couldnot start chrome driver..')

    return driver


def parse(id,page_idx, page_count, abs_path, use_proxy=False, use_headless=False, main_link = URLS[1], main_link_param = URL_PARAM):

    driver = setup_driver(id,abs_path,use_proxy,use_headless)

    print(f'{datetime.now()} task={id} starting parsing..')

    #clicking first button before enter site 'agreement'
    try:
        agreed = driver.find_element_by_id('confirm-button')
        agreed.click()
    except:
        print(f' task={id} already clicked')

    driver.implicitly_wait(10)

    all_cars = []

    links = get_all_links(main_link, main_link_param, page_idx, page_count)

    print(f' task={id} links', links)

    #get pages from page_idx till pages_count idx starts with 1 !
    for count, page, in enumerate(links,start=1):
        print(f' task={id} parsing page {count} of {page_count} ({page})')
        for _ in  range(5):
            # open page link
            try:
                driver.get(page)
                break
            except:
                #restart chrome driver
                #wait some secs
                print(f' task={id} quit driver and restart..')
                driver.quit()
                sleep(60)
                driver = setup_driver(id,abs_path, use_proxy, use_headless)


        # make random sleep time between 'gets'
        sleep_time = uniform(1, 3) #these values adjusted manually to achieve best results
        if use_proxy == True:  # add more time in case of proxy
            wtime = 5 + 4 + sleep_time
        else:
            wtime = 5 + sleep_time

        # wait page to load
        print(f' task={id} sleep for {wtime} ...')
        driver.implicitly_wait(wtime)

        # parse page
        print(f'task = {id} parsing text on the page ...')
        cars_page = []
        try:
            cars_page = get_content(id, driver.page_source, abs_path)
        except:
            #something happened
            #skip to next page
            print(f'task = {id} coudnt parse text page ...{page} !')

        all_cars.extend(cars_page)

    print(f'{datetime.now()} task={id} всего получено {len(all_cars)} обьявлений')

    driver.quit()

    return all_cars


def main():
   #all_cars = read_csv1(FILE)
   #print(all_cars)

    page_idx = 10
    page_count = 2
    abs_path = os.path.abspath('')
    id = 1

    all_cars = parse(id, page_idx, page_count, abs_path, use_proxy=False,use_headless=True, main_link=URLS[0], main_link_param=URL_PARAMS[0] )

# save datat to file csv,
    print(all_cars)
    save_csv1(all_cars, FILE)

if __name__ == '__main__':
    main()
