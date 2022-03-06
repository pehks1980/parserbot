import time

from ._parser import parse
import  csv, os, re, threading
from parserapp1.models import *
from ._common import *



def parse_img_link(text):
    regex = r'^https:\/\/'
    if re.search(regex, text):  # if it starts with https:// then it means it is the right img link
        return text
    else:
        return DEFAULT_PIC

def parse_URLS_region(text):
    regex = r'^https:\/\/.+\.ru\/(.+)\/cars.+'
    if re.search(regex, text):  # if it starts with https:// then it means it is the right img link
        return re.search(regex, text).group(1).capitalize()
    else:
        return None


def updateDbTask(id, all_cars, region_idx=1, url=URLS[1], url_param=URL_PARAMS[0]):
    # updateDb for one task

    # create caradgroup record and set it with some data
    caradgroup = CarAdGroup()

    caradgroup.task_id = int(id)

    # fill out reference info
    caradgroup.name = HOST

    caradgroup.region = parse_URLS_region(url)

    caradgroup.main_link = url

    caradgroup.main_link_param = url_param
    # copy page_idx page_count from parsetask table
    task = ParseTask.objects.get(pk=id)
    caradgroup.page_idx = task.page_idx
    caradgroup.page_count = task.page_count

    caradgroup.save()

    caradgroup_id = caradgroup.pk

    added_amount = 0
    # fill db with ads of cars
    for car in all_cars:
        obj, created = CarAds.objects.get_or_create(
            ad_link=car['ad_link'],  # unique field only to check

            defaults={'group_id': caradgroup,
                      'title': car['title'],
                      'img_link': parse_img_link(car['img_link']),
                      'price': car['price'],
                      'price_currency': car['price_currency'],
                      'transmission': car['transmission'],
                      'production_date': car['production_date'],
                      'fuel_type': car['fuel_type'],
                      'color': car['color'],
                      'brand': car['brand'],
                      'region_idx' : region_idx

                      }
            # the rest will _not_  be taken in 'Already exists' comparison, but will be entered in CREATE case
        )

        if created == False:
            print(f'dup car {car["ad_link"]}')
        else:
            obj.save()
            added_amount = added_amount + 1
        # Any keyword arguments passed to get_or_create() — except an optional one called defaults
        # — will be used in a get() call. If an object is found,
        # get_or_create() returns a tuple of that object and False.

        # carad = CarAds(group_id=caradgroup)
        # carad.title = car['title']
        # carad.ad_link = car['ad_link']
        # carad.img_link = car['img_link']
        # carad.price = car['price']
        # carad.price_currency = car['price_currency']
        # carad.transmission = car['transmission']
        # carad.production_date = car['production_date']
        # carad.fuel_type = car['fuel_type']
        # carad.color = car['color']
        # carad.brand = car['brand']
        # carad.save()

    # update caradroup with set length
    caradgroup = CarAdGroup.objects.get(pk=caradgroup_id)

    caradgroup.records_number = added_amount

    caradgroup.save()

    print(f' task = {id}, added {added_amount} car ads...')

#API call P&U task
def ParseAndUpdateDb(page_idx, page_count, region_idx, url_params_idx, use_proxy=False):
    #start thread for parsing
    task = ParseTask()

    task.page_idx = page_idx
    task.page_count = page_count

    task.save()

    t = threading.Thread(target=ParseUpdateDbThread,args=[task.id,page_idx,page_count, region_idx, url_params_idx, use_proxy])
    t.setDaemon(True)
    t.start()

    return task

#API call P&U task thread func
def ParseUpdateDbThread(id,page_idx,page_count, region_idx, url_params_idx, use_proxy):
    print("Received P&U task", id)
    time.sleep(1)

    task = ParseTask.objects.get(pk=id)

    abs_path = os.path.dirname(__file__)  # absolute dir to parserapp1 (including)

    all_cars = parse(id,page_idx, page_count, abs_path, use_proxy=use_proxy, use_headless=True, main_link=URLS[region_idx],
                     main_link_param=URL_PARAMS[url_params_idx])

    if all_cars:# if we have any ads
        #save_csv1(all_cars, f'{abs_path}/{FILE_NAME}_{id}.csv')
        task.is_done = True
        for _ in range(5):
            try:
                task.save()
                break
            except:
                time.sleep(5)
                #db is locked wait for some time
                #and try again

        #update db here
        print("Update Db for P&U task = ", task.id)

        task = ParseTask.objects.get(pk=task.id)

        time.sleep(9)

        if task.db_updated == False and task.is_done == True:
            for _ in range(5):
                try:
                    updateDbTask(task.id, all_cars, region_idx, URLS[region_idx], URL_PARAMS[url_params_idx])
                    task.db_updated = True
                    task.save()
                    break
                except:
                    #wait for some time and try again
                    time.sleep(10)

            print("db was updated for P&U task = ", task.id)

    else:
        print(f'task P&U = {id} error')
        task.is_error = True
        task.save()

    print("Finishing P&U task", id)