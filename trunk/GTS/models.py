# -*- coding: utf-8 -*-

#===============================================================================
# DjangoGTS project Models declarations file
# 2007-09-07: Sergeyev V.V.
#===============================================================================

from django.db import models
from django.contrib.auth.models import User

from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor 

import datetime
import time

#------------------------------------------------------------------------------ 
#Вспомогательные классы для добавления к стандартной модели User поля Account.
#Увы, наследовать модели в Джанго нельзя.
#------------------------------------------------------------------------------
class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor): # this line just can't be too long, right?
    def __get__(self, instance, instance_type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.related.model.DoesNotExist:
            obj = self.related.model(**{self.related.field.name: instance})
            obj.save()
            return obj

#------------------------------------------------------------------------------
class AutoOneToOneField(OneToOneField):
    '''
    OneToOneField, которое создает зависимый объект при первом обращении
    из родительского, если он еще не создан.
    '''
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))
        if not cls._meta.one_to_one_field:
            cls._meta.one_to_one_field = self

#------------------------------------------------------------------------------
#Main classes
#------------------------------------------------------------------------------ 
class  Account(models.Model):
    """
    Модель GPS Аккаунта. 
    В системе Аккаунт является сущностью верхнего уровня,
    на него ссылаются Пользователи, Устройства, События.
    (!!!) После создания аккаунта, его id изменять нельзя.
    """
    
    SPEED_UNITS = (
                   ('mph', 'mph'),
                   ('kph', 'kph'),
                   ('knots', 'knots'),
                   )
    
    DISTANCE_UNITS = (
                      ('Miles', 'Miles'),
                      ('Km', 'Km'),
                      ('Nm', 'Nm'),
                      )
    
    TEMPERATURE_UNITS = (
                         ('F', 'F'),
                         ('C', 'C'),
                         )
    
    id                = models.SlugField(primary_key=True, maxlength=32, help_text="Can not be changed after creation")
    description       = models.CharField("Description", maxlength="128", unique=True) # equipment description
    time_zone         = models.CharField("Time Zone", maxlength="32", blank=True)
    speed_units       = models.CharField("Speed Units", maxlength="5", choices=SPEED_UNITS, help_text="mph, kph, knots")
    distance_units    = models.CharField("Distance Units", maxlength="5", choices=DISTANCE_UNITS, help_text="Miles, Km, Nm")
    temperature_units = models.CharField("Temperature Units", maxlength="1", choices=TEMPERATURE_UNITS, help_text="F, C")

    def __str__(self):
        return self.description
    
    def __unicode__(self):
        return self.description

    class Admin:
        list_display = ('id', 'description', 'time_zone', 'speed_units', 'distance_units', 'temperature_units')

#------------------------------------------------------------------------------ 
class GTS_User(models.Model):
    """
    Модель пользователей GTS системы.
    Процедура создания жзеров для системы следующая:
    - Админ создает в админке в разделе "Auth\Users" нового юзера со всеми атрибуати включая пароль
    - в Админке, в разделе "Gts\Accounts" заводит все необходимые аккаунты
      Из фронт части убран список аккаунтов и выводится только форму редактирования текущего, как в OpenGTS
    - в Админке в разделе "Gts\Users of GTS\" создаем привязки Юзеров к аккаунтам
    """
    account = models.ForeignKey(Account, verbose_name="Account ID") # we need to extend base User model with Account  
    #user    = models.ForeignKey(User) # link to User from Django authentification system
    user     = AutoOneToOneField(User, related_name="gts_user")

    def __init__(self, *args, **kwargs):
        super(GTS_User, self).__init__(*args, **kwargs)

    def __str__(self):
        return  '%s - %s' % (self.account, self.user)
    
    def __unicode__(self):
        return  str(self.user)
    
    class Meta:
        verbose_name = "User of GTS"
        verbose_name_plural = "Users of GTS"
    
    class Admin:
        list_display = ('account', 'user')

#------------------------------------------------------------------------------ 
class Device(models.Model):
    """
    Модель устройства GPS системы.
    Привязана к Аккаунту.
    """
    
    id                       = models.SlugField("Device ID", primary_key=True, maxlength="32", help_text="Use only letters and numbers")
    account                  = models.ForeignKey(Account, verbose_name="Account ID", editable=False)
    description              = models.CharField("Description", maxlength="128") # equipment description

    #save_curent_ip_address   = models.BooleanField("Save the incoming ip address in the Device", editable=False)
    
    unique_id                = models.CharField("Unique ID", maxlength="40", blank=True)
    group_id                 = models.CharField("Group ID", maxlength="32", blank=True) # device group
    equipment_type           = models.CharField("Equipment Type", maxlength="32", blank=True) # equipment type
    serial_number            = models.CharField("Serial Number", maxlength="24", blank=True) # device serial#
    is_active                = models.BooleanField("Is Active") # active device?
    
    allow_notify             = models.BooleanField("Allow Notification", blank=True, null=True, default=0, editable=False) # allow notification
    notify_email             = models.EmailField("Notification EMail address", blank=True, editable=False) # notification email
    notify_selector          = models.TextField("Notification selector", blank=True, editable=False) # notification rule
    notify_action            = models.IntegerField("Notification action", blank=True, null=True, default=0, editable=False) # notification action
    
    device_type              = models.IntegerField("Device type", blank=True, null=True, default=0) # manufacturer, etc (config)
    border_crossing          = models.IntegerField("Border Crossing Flags", blank=True, null=True, default=0, editable=False) # border crossing flags
    
    ip_address_valid         = models.IPAddressField("Valid IP Addresses", blank=True, default='127.0.0.1', editable=False) # valid IP address block
    ip_address_current       = models.CharField("Current IP Address", maxlength="32", blank=True, editable=False) # current IP address
    
    supported_encodings      = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    unit_limit_interval      = models.IntegerField(blank=True, null=True, default=0, editable=False) #DMTP
    max_allowed_events       = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    last_total_connect_time  = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    total_profile_mask       = models.TextField(blank=True, editable=False) # DMTP
    total_max_conn           = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    total_max_conn_per_min   = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    last_duplex_connect_time = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    duplex_profile_mask      = models.TextField(blank=True, editable=False) # DMTP
    duplex_max_conn          = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    duplex_max_conn_per_min  = models.IntegerField(blank=True, null=True, default=0, editable=False) # DMTP
    
    # ограничивающий многоугольник для устройства,
    # рисуется пользователем на карте.
    limiting_region_xml      = models.TextField(blank=True, editable=False)

    def is_active_str(self):
        """
        Возвращает удобочитаемое представление статуса активен/неактивен.
        """
        if self.is_active == 1:
            return "Да"
        else:
            return "Нет"

    def __str__(self):
        return  self.description
    
    def __unicode__(self):
        return  self.description
    
    class Admin:
        list_display = ('id', 'account', 'description', 'unique_id', 'equipment_type', 'is_active')

#------------------------------------------------------------------------------
"""
STATUS_CODES - список пар "код" : "событие" для представления кодов событий в удобочитаемом виде
"""

STATUS_CODES = {
                   61456 : 'Initialized',
                   61713 : 'MotionStart',
                   61714 : 'InMotion',
                   61715 : 'Stop',
                   61716 : 'MotionDormant'
                   }


#------------------------------------------------------------------------------ 
def Decimal2DegMinSec(decimal=0.0):
    """
    Перевод десятичных градусов в градусы минуты' секунды"
    """
    return "%02i &deg; %02i' %02i''" % (int(decimal), int((decimal - int(decimal)) * 60), int((((decimal - int(decimal)) * 60) - int((decimal - int(decimal)) * 60)) * 60))

def IsSimilar(coord1, coord2):
    """
    Принимает десятичные градусы.
    Если они различаются меньше чем на две секунды, то считает их подобными.
    """
    if abs(coord2 - coord1) < 0.000555:
        return True
    else:
        return None
     
#------------------------------------------------------------------------------ 
class EventData(models.Model):
    """
    Модель GPS события.
    Событие привязано к Аккаунту и Устройству.
    """
    
    account       = models.ForeignKey(Account, verbose_name="Account ID") # SlugField(db_column="accountID" , primary_key=True, maxlength=32)
    device        = models.ForeignKey(Device, verbose_name="Device ID") # models.SlugField(db_column="deviceID" ,primary_key=True, maxlength=32)
    timestamp     = models.IntegerField(db_column="timestamp" ,primary_key=True)
    status_code   = models.IntegerField(db_column="statusCode")
    entity        = models.CharField(db_column="entity" ,null=True ,blank=True, maxlength=32)
    data_source   = models.CharField(db_column="dataSource" ,null=True ,blank=True, maxlength=32)
    raw_data      = models.TextField(db_column="rawData" ,null=True ,blank=True)
    latitude      = models.FloatField(db_column="latitude" ,null=True, max_digits=13, decimal_places=6, blank=True)
    longitude     = models.FloatField(db_column="longitude" ,null=True, max_digits=13, decimal_places=6, blank=True)
    gps_age       = models.IntegerField(db_column="gpsAge" ,null=True, blank=True)
    horz_accuracy = models.FloatField(db_column="horzAccuracy" ,null=True, max_digits=13, decimal_places=6, blank=True)
    speed_kph     = models.FloatField(db_column="speedKPH" ,null=True, max_digits=13, decimal_places=2, blank=True)
    heading       = models.FloatField(db_column="heading" ,null=True, max_digits=13, decimal_places=6, blank=True)
    altitude      = models.FloatField(db_column="altitude" ,null=True, max_digits=13, decimal_places=6, blank=True)
    distance_km   = models.FloatField(db_column="distanceKM" ,null=True, max_digits=13, decimal_places=2,blank=True)
    odometer_km   = models.FloatField(db_column="odometerKM" ,null=True, max_digits=13, decimal_places=2,blank=True)
    geozone_index = models.IntegerField(db_column="geozoneIndex" ,null=True, blank=True)
    geozone_id    = models.CharField(db_column="geozoneID" ,null=True ,blank=True, maxlength=32)
    address       = models.CharField(db_column="address" ,null=True ,blank=True, maxlength=90)
    subdivision   = models.CharField(db_column="subdivision" ,null=True ,blank=True, maxlength=32)
    creation_time = models.IntegerField(db_column="creationTime" ,null=True, blank=True)

    class Meta:
    #вручную указанно название таблицы в БД
        db_table = 'EventData'
    
    def event_date(self):
        """
        Возвращает дату и время события,
        конвертировав их из timestamp
        """
        return datetime.datetime.fromtimestamp(self.timestamp)
    
    def status(self):
        "Возвращает представление статуса по коду"
        return STATUS_CODES[self.status_code]

    def lat(self):
        "Возвращает строку: Градусы Минуты Секунды"
        return Decimal2DegMinSec(self.latitude)
    
    def lon(self):
        "Возвращает строку: Градусы Минуты Секунды"
        return Decimal2DegMinSec(self.longitude)

    def __str__(self):
        return '%s, %s, %s' % (self.account, self.device, datetime.datetime.fromtimestamp(self.timestamp))
    
    def __unicode__(self):
        return '%s, %s, %s' % (self.account, self.device, datetime.datetime.fromtimestamp(self.timestamp))

#Раскоментируйте нижележащий код, если нужно видеть и редактировать в Админке объекты EventData 
#Насколько мне видится архитектура проекта, у пользователей нет надобности руками вводить события   
#или редактировать их.
#    class Admin:
#        pass

#------------------------------------------------------------------------------ 
