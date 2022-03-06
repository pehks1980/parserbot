from django.db import models

# Create your models here.
#parser task thread

class ParseTask(models.Model):
    task = models.CharField(max_length=30, blank=True, null=True)
    is_done = models.BooleanField(blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True) # time when it started
    finished_at = models.DateTimeField(auto_now=True) # time when it finished
    page_idx = models.PositiveIntegerField(verbose_name='начальная страница', default=0)
    page_count = models.PositiveIntegerField(verbose_name='Количество страниц', default=0)
    db_updated = models.BooleanField(blank=False, default=False)
    is_error = models.BooleanField(blank=False, default=False)

#car_site:
class CarAdGroup(models.Model):
   # task_id = models.ForeignKey(ParseTask, on_delete=models.CASCADE)
    task_id = models.PositiveIntegerField(verbose_name='Task id', default=0)
    name = models.CharField(verbose_name='Group name', max_length=63, blank=True) #auto.ru max+length - number of symbols!
    region = models.CharField(verbose_name='Регион', max_length=24, blank=True)   # region
    description = models.TextField(verbose_name='Description', blank=True)
    status = models.BooleanField(verbose_name='Статус', blank=True, default=True)  # активно/неактивно
    records_number = models.PositiveIntegerField(verbose_name='Количество полученных обьяв', default=0) #number of ads in one run

    main_link = models.TextField(verbose_name='стартовая ссылка', blank=True)
    main_link_param = models.CharField(verbose_name='?=параметры ссылки', max_length=63, blank=True)
    page_idx = models.PositiveIntegerField(verbose_name='начальная страница', default=0)
    page_count = models.PositiveIntegerField(verbose_name='Количество страниц', default=0)


#The auto_now_add will set the timezone.now() only when the instance is created,
#and auto_now will update the field everytime the save method is called.

#car_ad:

class CarAds(models.Model):
    group_id = models.ForeignKey(CarAdGroup, on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name='Статус', blank=True, default=True)  # активно/неактивно

    title = models.TextField(verbose_name='Заголовок объявления')
    price = models.PositiveIntegerField(verbose_name='Цена', default=0)
    price_currency = models.CharField(verbose_name='Валюта', max_length=3, blank=True)
    region_idx = models.PositiveIntegerField(verbose_name='индекс региона URLS', default=0)

    ad_link = models.TextField(verbose_name='Ссылка на объявление', unique=True)
    img_link = models.TextField(verbose_name='Ссылка на изображение', blank=True)

    transmission = models.CharField(verbose_name='Тип трансмиссии', max_length=24, blank=True)

    production_date = models.PositiveIntegerField(verbose_name='Дата выпуска', default=0)

    fuel_type = models.CharField(verbose_name='Тип топлива', max_length=24, blank=True)
    color = models.CharField(verbose_name='Цвет кузова', max_length=24, blank=True)
    brand = models.CharField(verbose_name='Brand name', max_length=24, blank=True)

# "brand" "RENAULT"
# "color" "серый"
# "fuelType" "бензин"
# "image" "https://avatars.mds.yandex.net/get-autoru-vos/2165505/a2c808e6c99167e9f1724e45324d7fd1/320x240"
# "name" 	"Renault Logan I" <> title
# "productionDate" "2004"
# "vehicleTransmission" "механическая"
# "price" "209000"
# "priceCurrency" "RUB"
# "url" "https://auto.ru/cars/used/sale/renault/logan/1098526412-3b4ec908/"


