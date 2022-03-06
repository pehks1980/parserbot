import random

from django.shortcuts import render

# Create your views here.


from django.template.loader import render_to_string
from django.http import JsonResponse

from ._parser import parse
from ._common import *
from .parser_db import *

import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import threading
from parserapp1.models import *
import re
import time

# def parse_start(request):
#
#     result = render_to_string('parserapp1/result.html',request=request)
#
#     return JsonResponse({'result': result})

def index(request):

   # startParseTask(request)

    return render(request, 'parserapp1/index.html', locals())

def startParseTask(request):
    #make array of pages
    page_idx = random.randint(1, 100)
    page_count = 2
    #create record for this parse task & set with run params
    print(f'clicked: page index = {page_idx}, page_count = {page_count}')

    task = ParseTask()

    task.page_idx = page_idx
    task.page_count = page_count

    task.save()

    t = threading.Thread(target=ParseTaskThread,args=[task.id,page_idx,page_count])
    t.setDaemon(True)
    t.start()
    return JsonResponse({'id':task.id,
                         'page_idx':page_idx,
                         'page_count':page_count})

def checkParseTask(request,id):
    try:
        task = ParseTask.objects.get(pk=id)
    except:
        #if we have db exception as db locked due to limited db sql lite
        return JsonResponse ({'is_done': 0,
                            'db_updated': 0,
                            'is_error': 0,
         })

    return JsonResponse({'is_done':task.is_done,
                         'db_updated':task.db_updated,
                         'is_error':task.is_error,
                         })

def ParseTaskThread(id,page_idx,page_count):
    print("Received task",id)
    #time.sleep(3)
    task = ParseTask.objects.get(pk=id)

    abs_path = os.path.dirname(__file__)#absolute dir to parserapp1 (including)

    all_cars = parse(id,page_idx, page_count, abs_path, use_proxy=True, use_headless=True, main_link=URL, main_link_param=URL_PARAM)

    if all_cars:
        save_csv1(all_cars, f'{abs_path}/{FILE_NAME}_{id}.csv')
        task.is_done = True
        task.save()
    else:
        print(f'task {id} error')

    print("Finishing task",id)


#add all outstanding csv files into the db
def updateDbAll(request):
    print("Received Update Db for All tasks (from csv)")
    ids = ParseTask.objects.all()
    _ids = []
    for id in ids:
        if id.db_updated == False and id.is_done == True:
            # read data to dict from csv
            abs_path = os.path.dirname(__file__)
            # read car data from csv task number - id
            all_cars = read_csv1(f'{abs_path}/{FILE_NAME}_{id.id}.csv')

            print(f'found new task (csv) = {id.id} updating..')

            updateDbTask(id.id, all_cars)


            id.db_updated = True
            _ids.append(id.id)
            id.save()

    print('Finished update for All tasks (from csv)')

    return JsonResponse({'res': 'successful',
                         'tasks': _ids})
#update DB with one just parsed task - id
def updateDb(request,id):
    print("Received Update Db for task = ", id)

    task = ParseTask.objects.get(pk=id)

    if task.db_updated == False and task.is_done == True:
        # read data to dict from csv
        abs_path = os.path.dirname(__file__)
        # read car data from csv task number - id
        all_cars = read_csv1(f'{abs_path}/{FILE_NAME}_{id}.csv')

        updateDbTask(id,all_cars)
        task.db_updated = True
        task.save()
        print("db was updated for task = ", id)

    return JsonResponse({'res':'successful',
                         'task': id})

#click button of P&U task
def startParseDb(request):
    page_idx = random.randint(1, 200)
    page_count = 10
    region_idx = 0 # like 'https://auto.ru/sankt-peterburg/cars/used/'
    url_params_idx = 0 #'?sort=fresh_relevance_1-desc&page='
    use_proxy=False

    #create record for this parse task & set with run params
    print (f'clicked: page index = {page_idx}, page_count = {page_count}, region = {parse_URLS_region(URLS[region_idx])}, params = {URL_PARAMS[url_params_idx]}, proxy = {use_proxy}')

    # create and run  parse and update task main function to get ads from target site
    #Page_idx - start page
    #page_count - numbr of pages
    #use_proxy - use parser via proxy (from proxies.txt)
    #region_idx - idx of region in URLS array

    task = ParseAndUpdateDb(page_idx, page_count, region_idx, url_params_idx, use_proxy=use_proxy)

    return JsonResponse({'id':task.id,
                         'page_idx':page_idx,
                         'page_count':page_count})


