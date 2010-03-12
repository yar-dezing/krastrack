# -*- coding: utf-8 -*-

#===============================================================================
# DjangoGTS project Views (controlers of output to HTML) file
# 2007-09-07: Sergeyev V.V.
#===============================================================================

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django import newforms as forms
from django.newforms import form_for_instance, form_for_model, save_instance, form_for_fields
from django.core.paginator import ObjectPaginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from GTS.models import Account, GTS_User, Device, EventData, STATUS_CODES, Decimal2DegMinSec, IsSimilar 

import datetime
import time
import math
from xml.dom.minidom import Document
from django.conf import settings

#------------------------------------------------------------------------------ 
#Авторизация
#------------------------------------------------------------------------------ 
def login_user(request):
    "Implements login action"
    if request.method == "POST":
        accountname  = request.POST["account"]
        username = request.POST["username"]
        password = request.POST["password"]
        
        try:
            user = authenticate(username=username, password=password)
            if user is None:
                raise Exception
            
            if user.gts_user.account.id != accountname:
                raise Exception
            
            login(request, user)
            
            return HttpResponseRedirect("/")
        except:
            error_message = "Uncorrect account, user name or password! Please try again."
            return render_to_response("login.html", {"error_message" : error_message})
    else:
        return render_to_response("login.html")

#------------------------------------------------------------------------------
def logout_user(request):
    "Implements logout action"
    logout(request)
    return HttpResponseRedirect("/")

#------------------------------------------------------------------------------ 
def last_event_for_devices(request):
    """
    Выбирает из БД одно последнее событие для каждого устройства для текущего Аккаунта.
    """
    
    account = request.user.gts_user.account
    
    #Получаем одно последнее событие для каждого устройства
    devices = Device.objects.filter(account__exact=account)
    events = []
    for device in devices:
        event_set = EventData.objects.filter(device__exact=device).order_by('-timestamp')[:1]
        for event in event_set: 
            events.append(event)
            
    return events

#------------------------------------------------------------------------------ 
#Главная страница 
#------------------------------------------------------------------------------
@login_required 
def show_index(request):
    """
    Рендерит главную страницу на основе шаблона.
    (!) В данный момент не используется,
    При загрузке главной страницы выводится последнее извесное местоположение устройств
    функцией last_known_location()
    """
    
    events = last_event_for_devices(request)
        
    sub_title = "Последнее месторасположение ТС"
    
    content = {"sub_title" : sub_title,
               "events" : events}
    
    return render_to_response("index.html", content)

#------------------------------------------------------------------------------ 
#Работа с Аккаунтами 
#------------------------------------------------------------------------------
@login_required 
def accounts_list(request):
    """
    Show list of accounts.
    (!) В данный момент не используется.
    Сразу выводится account_detail() для текущего аккаунта.
    """
    accounts = Account.objects.all()
    
    content = {"accounts" : accounts}
    
    return render_to_response("accounts_list.html", content)

#------------------------------------------------------------------------------
@login_required 
def account_detail(request, account_id=0):
    """
    Отображает информацию о текущем Аккаунте.
    Ее можно изменить и сохранить.
    Аккаунт берется из request, при залогиневшеся юзере там появляется переменная user.
    """
    
    error_message = ""

    #if account_id == 0:
    account = request.user.gts_user.account
    #else:
    #    account = Account.objects.get(pk=account_id)
    
    if request.method == "POST":
        AccountForm = form_for_model(Account)
        account_form = AccountForm(request.POST)
        if account_form.is_valid():
            account_form.clean_data['id'] = account.id 
            save_instance(account_form, account, True)

            return HttpResponseRedirect('/gts_accounts/')
        else:
            error_message = "Form contain errors!"  # % account_form.errors 
    else:
        AccountForm = form_for_instance(account)
        
        account_form = AccountForm()
        
    content = {"account" : account,
               "account_form" : account_form,
               "error_message" : error_message,
               }

    return render_to_response("account_detail.html", content)

#------------------------------------------------------------------------------
@login_required 
def account_add(request):
    "Add new Account instance"
    error_message = ""
    
    if request.method == "POST":
        AccountForm = form_for_model(Account)
        account_form = AccountForm(request.POST)
        if account_form.is_valid():
            account_form.save()
            return HttpResponseRedirect('/gts_accounts/')
        else:
            error_message = "Form contain errors!" # % account_form.errors 
    else:
        AccountForm = form_for_model(Account)
        account_form = AccountForm() 
    
    content = {"account_form" : account_form,
               "error_message" : error_message,
               }

    return render_to_response("account_detail.html", content)

#------------------------------------------------------------------------------ 
#Работа с Юзерами 
#------------------------------------------------------------------------------
@login_required 
def users_list(request):
    """
    Выводит список юзеров, принадлежащих данному аккаунту
    """
    
    account = request.user.gts_user.account
    
    #users = GTS_User.objects.all()
    users = GTS_User.objects.filter(account__exact=account)
    
    content = {"users" : users}
    
    return render_to_response("users_list.html", content)

#------------------------------------------------------------------------------
@login_required 
def user_detail(request, user_id):
    """
    Show/edit/save GTS_User instance
    (!) В данный момент не используется.
    Пользователи редактируюся в админ-части Джанго-сайта.
    """
    error_message = ""
    user = GTS_User.objects.get(pk=user_id)
    
    if request.method == "POST":
        UserForm = form_for_model(GTS_User)
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            save_instance(user_form, user, True)

            return HttpResponseRedirect('/users/')
        else:
            error_message = "Form contain errors!"  # % account_form.errors 
    else:
        UserForm = form_for_instance(user)
        user_form = UserForm() 
    
    content = {"user" : user,
               "user_form" : user_form,
               "error_message" : error_message,
               }

    return render_to_response("user_detail.html", content)

#------------------------------------------------------------------------------
@login_required 
def user_add(request):
    """
    Add new GTS_User instance
    (!) В данный момент не используется.
    Пользователи заводятся в админ-части Джанго-сайта.
    """
    error_message = ""
    
    if request.method == "POST":
        UserForm = form_for_model(GTS_User)
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            return HttpResponseRedirect('/users/')
        else:
            error_message = "Form contain errors!" # % account_form.errors 
    else:
        UserForm = form_for_model(GTS_User)
        user_form = UserForm() 
    
    content = {"user_form" : user_form,
               "error_message" : error_message,
               }

    return render_to_response("user_detail.html", content)

#------------------------------------------------------------------------------ 
#Работа с Устройствами 
#------------------------------------------------------------------------------
@login_required 
def devices_list(request):
    """
    Выводит список устройств, принадлежащих данному аккаунту
    """
    
    account = request.user.gts_user.account
    
    #devices = Device.objects.all()
    devices = Device.objects.filter(account__exact=account)
    
    content = {"devices" : devices}
    
    return render_to_response("devices_list.html", content)

#------------------------------------------------------------------------------
@login_required 
def device_detail(request, device_id):
    "Show/edit/save Device instance"
    
    account = request.user.gts_user.account
    
    error_message = ""
    device = Device.objects.get(pk=device_id)
    
    if request.method == "POST":
        DeviceForm = form_for_model(Device)
        device_form = DeviceForm(request.POST)
        if device_form.is_valid():
            save_instance(device_form, device, True)
#            new_device = save_instance(device_form, device, False)
#            new_device.account = account
#            new_device.save()

            return HttpResponseRedirect('/devices/')
        else:
            error_message = "Form contain errors!"  # % account_form.errors 
    else:
        DeviceForm = form_for_instance(device)
        device_form = DeviceForm()
        
    content = {"device" : device,
               "device_form" : device_form,
               "error_message" : error_message,
               }

    return render_to_response("device_detail.html", content)

#------------------------------------------------------------------------------
@login_required 
def device_add(request):
    "Add new Device instance"
    
    account = request.user.gts_user.account
    
    error_message = ""
    
    if request.method == "POST":
        DeviceForm = form_for_model(Device)
        device_form = DeviceForm(request.POST)
        if device_form.is_valid():
            new_device = device_form.save(False)
            new_device.account = account
            new_device.save()
            
            return HttpResponseRedirect('/devices/')
        else:
            error_message = "Form contain errors!" # % account_form.errors 
    else:
        DeviceForm = form_for_model(Device)
        device_form = DeviceForm() 
    
    content = {"device_form" : device_form,
               "error_message" : error_message,
               }

    return render_to_response("device_detail.html", content)

#------------------------------------------------------------------------------ 
@login_required 
def device_delete(request, device_id):
    "Delete Device instance"
    error_message = ""
    device = Device.objects.get(pk=device_id)
    device.delete()
    
    return HttpResponseRedirect("/devices/")

#------------------------------------------------------------------------------ 
@login_required
def device_name_check(request):
    "Check ID of new device via AJAX and return result - avaible/such device already exists"
    device_id = request.POST["device"]
    try:
        device = Device.objects.get(pk=device_id)
        return HttpResponse('<p class="errornote">Device already exists</p>')
    except:
        return HttpResponse('')
        
#------------------------------------------------------------------------------ 
#Импорт "Истории событий" в CSV 
#------------------------------------------------------------------------------ 
import csv

def events_history_csv(request, username, password, interval_begin, interval_end):
    """
    Обрабатывает запрос на csv-файл.
    Возвращает записи EventData отфильтрованные по параметрам.
    Пример строки запроса:
    http://127.0.0.1:8000/cvs/root/rootwdp/2007_09_01/2007_09_09/
    root        - пользователь
    rootwdp     - пароль
    2007_09_01  - нач. дата
    2007_09_09  - кон. дата
    """
    
    try:
        #Проверка пользователя
        if password == "_":
            user = request.user
            if user.is_authenticated():
                pass
            else:
                raise Exception
            
            begin_timestamp = interval_begin
            end_timestamp = interval_end
            device = username
            #выборка событий
            events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                raise Exception
        
            #переводим даты из строк в объекты "ДатаВремя"
            interval_begin_clear = datetime.datetime(*map(int, interval_begin.split("_")))  
            interval_begin_end = datetime.datetime(*map(int, interval_end.split("_")))
        
            begin_timestamp = time.mktime(interval_begin_clear.timetuple())
            end_timestamp = time.mktime(interval_begin_end.timetuple())
        
            #выборка событий
            events = EventData.objects.filter(timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')
        
        #задаем заголовок cvs
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=events.csv'
        
        #вывод заголовочной строки
        writer = csv.writer(response)
        writer.writerow(["Date/time", "Status", "Lat", "Lon", "Speed", "Altitude"])
        
        #вывод строк событий
        #можно использовать любое из полей модели EventData
        for event in events:
            #writer.writerow([str(event.event_date()), event.status(), event.latitude, event.longitude, event.speed_kph, event.altitude])
            writer.writerow([str(event.event_date()), event.latitude, event.longitude, event.speed_kph, event.altitude])

        return response
    except:
        return HttpResponse("Error in parameters!")

#------------------------------------------------------------------------------
#Часть №2. 
#- отображение перемещения устройства по карте googlemap реализованное
#через google map API (значки, показывающие точки, должны иметь
#картинку с направлением передвижения)
#------------------------------------------------------------------------------ 

#------------------------------------------------------------------------------ 
#def get_device_choices(account):
#    devices = Device.objects.filter(account=account)
#    for device in devices:
#        yield (device.id, device.id) 

#------------------------------------------------------------------------------
class MapParametersForm(forms.Form):
    "Класс формы для указания параметров карты"
#    device         = forms.ModelChoiceField(Device.objects.all())
    interval_begin = forms.DateTimeField(label="Начало периода", widget=forms.TextInput(attrs={"class" : "vDateField"}), help_text="гггг-мм-дд чч:мм:сс")
    interval_end   = forms.DateTimeField(label="Конец периода", widget=forms.TextInput(attrs={"class" : "vDateField"}), help_text="гггг-мм-дд чч:мм:сс")
    
    def __init__(self, account, *args, **kwargs):
        """
        Конструктор переопределен для создания поля "device", 
        список значений для которого фильтруется в соответствии с текущим Аккаунтом  
        """
        super(MapParametersForm, self).__init__(*args, **kwargs)
        self.fields["device"] = forms.ModelChoiceField(Device.objects.filter(account__exact=account), label="Устройство")

#------------------------------------------------------------------------------ 
#class GooglePoint(object):
#    """
#    Вспомогательный клас для создания списка точек для карты.
#    """
#    html = ""      # код точки для вставки в ДжаваСкрипт на странице
#    info = ""      # строка информации для подсказки при клике по точке
#    icon = ""      # пиктограма точки на карте (начало, движение, стоп, направление движения)
#    latitude = ""  # строка со значением "latitude" События, (!) округленная 
#    longitude = "" # строка со значением "longitude" События, (!) округленная
#    lat       = 0.0
#    lon       = 0.0
#    #status = ""    # статус (движение, стоянка)
#    
#    def __init__(self, html, info, icon, latitude, longitude):
#        self.html = html
#        self.info = info
#        self.icon = icon
#        # координаты округляются до 2х знаков
#        # так учитывается погрешность передатчика + уменшается кол-во точек на карте
#        # в принципе 1 знак после запятой тоже дает неплохую точность, а кол-во точек уменшается _очень_
#        self.latitude = "%.2f" % latitude
#        self.longitude = "%.2f" % longitude
#        self.lat = latitude
#        self.lon = longitude
#    
#    def __str__(self):
#        return "%s:%s" % (self.latitude, self.longitude)

#------------------------------------------------------------------------------
class DriveIdleEvent(object):
    """
    Вспомогательный клас для создания списка событий движение/стоянка и списка точек для карты.
    Поля: широта, долгота, начало движения, окончание движения, время движения, начало стоянки, окончание стоянки, время стоянки.
    """
    html = ""      # код точки для вставки в ДжаваСкрипт на странице
    info = ""      # строка информации для подсказки при клике по точке
    icon = ""      # пиктограма точки на карте (начало, движение, стоп, направление движения)    
    stop_begin_timestamp = ""    # дата/время начала стоянки
    stop_end_timestamp = ""      # дата/время окончания стоянки
    motion_begin_timestamp = ""  # дата/время начала движения
    motion_end_timestamp = ""    # дата/время окончания движения
    latitude = 0.0               # строка со значением "latitude" События 
    longitude = 0.0              # строка со значением "longitude" События
    latitude_rounded = ""        # строка со значением "latitude" События, (!) округленная.
    longitude_rounded = ""       # строка со значением "longitude" События, (!) округленная
                                 # Используется дял сравнения. Округление позволяет отсеивать точки, которые находятся очень близко.
    lat = ""                     # 
    lon = ""                     # 
    
    def __init__(self, html, info, icon, latitude=0.0, longitude=0.0):
        self.html = html
        self.info = info
        self.icon = icon
        # координаты округляются до 2х знаков
        # в принципе и 1 знак после запятой дает неплохую точность для отчета
        self.latitude = latitude # "%.2f" % latitude
        self.longitude = longitude # "%.2f" % longitude
        self.latitude_rounded = "%.3f" % latitude
        self.longitude_rounded = "%.3f" % longitude
        self.lat = Decimal2DegMinSec(latitude)
        self.lon = Decimal2DegMinSec(longitude)
    
    def driving_dates(self):
        "Возвращает: Строка содержащая даты начала и окончания движения"
        return "%s / %s" % (datetime.datetime.fromtimestamp(self.motion_begin_timestamp), datetime.datetime.fromtimestamp(self.motion_end_timestamp))
    
    def idle_dates(self):
        "Возвращает: Строка содержащая даты начала и окончания стоянки"
        return "%s / %s" % (datetime.datetime.fromtimestamp(self.stop_begin_timestamp), datetime.datetime.fromtimestamp(self.stop_end_timestamp))
    
    def driving_time(self):
        "Возвращает: Время движения"
        return datetime.datetime.fromtimestamp(self.motion_end_timestamp) - datetime.datetime.fromtimestamp(self.motion_begin_timestamp)

    def idle_time(self):
        "Возвращает: Время стоянки"
        return datetime.datetime.fromtimestamp(self.stop_end_timestamp) - datetime.datetime.fromtimestamp(self.stop_begin_timestamp)
    
    def idle_to_long(self):
        "Возвращает: 1 - если стоянка больше 5-ти минут (300 секунд)"
        delta = self.stop_end_timestamp - self.stop_begin_timestamp
        if delta > 300:
            return True
        else:
            return None 
    
    def is_parking(self):
        "Возвращает: True, если время движения = 0"
        delta = self.stop_end_timestamp - self.stop_begin_timestamp
        if delta > 0:
            return True
        else:
            return None

    def actual_icon(self):
        "Возвращает: пиктограмму Маркера."
        if self.idle_to_long():
            return 'red'
        else:
            return self.icon

    def tooltip(self):
        "Возвращает: Текст подсказки Маркера в зависимости от того, стоянка это или движение"
        if self.actual_icon()=='red':
            info_date = str(datetime.datetime.fromtimestamp(self.stop_begin_timestamp))
            info = '<b>Date/time: %s </b> <br>Idle time: %s <br>GPS: %s, %s ' % (info_date, str(self.idle_time()), self.lat, self.lon)            
    	    return info
        else:
            return self.info
        
#------------------------------------------------------------------------------
@login_required 
def google_map(request):
    """
    Выводит пустую карту. Обработка осуществляется через google_map_ajax
    """
    
    account = request.user.gts_user.account
    
    # просто отдаем форму для ввода параметров карты
    map_form = MapParametersForm(account)
    #map_form.base_fields['device'].choices = get_device_choices(account) # forms.ModelChoiceField(queryset=Device.objects.filter(account=account))
    content = {"map_form" : map_form}
    
    return render_to_response("map.html", content)

#------------------------------------------------------------------------------
@login_required
def google_map_ajax(request):
    """
    Возвращает данные для построения карты.
    Список маркеров загоняется в ХМЛ и отдается клиенту. 
    """
    
    xml_doc = Document()
    xml_markers = xml_doc.createElement("markers")
    xml_doc.appendChild(xml_markers)
    
    account = request.user.gts_user.account
    
    if request.method == "POST":
        map_form = MapParametersForm(account, request.POST)
        if map_form.is_valid():
            interval_begin = map_form.clean_data['interval_begin']
            interval_end = map_form.clean_data['interval_end']
            device = map_form.clean_data['device']
            
            # if time not specified, we will assign time = end of day
            if (interval_end.hour == 0) and (interval_end.minute == 0) and (interval_end.second == 0):
                interval_end = interval_end.replace(hour = 23, minute = 59, second = 59)
            
            begin_timestamp = time.mktime(interval_begin.timetuple())
            end_timestamp = time.mktime(interval_end.timetuple())
        
            polyline_points = []
            # первая точка - для центрирования карты
            first_point = ""
            
            #-----------------------------------------------------------------
            
            events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')
            
            # "предыдущее" событие
            di_event = None
            
            for event in events:
                icon = 'blue'

                if first_point=="":
                    first_point = "new GLatLng(%.6f, %.6f)" % (event.latitude, event.longitude)
                    icon = 'green'
                    
                info_date = str(datetime.datetime.fromtimestamp(event.timestamp))
                #info = '<b>Дата/Время: %s </b> <br>Скор: %.2f <br>Коорд: %s, %s ' % (info_date, event.speed_kph, event.lat(), event.lon())
                info = '<b>Date/time: %s </b> <br>Speed: %.2f <br>GPS: %s, %s ' % (info_date, event.speed_kph, event.lat(), event.lon())
                
                new_di_event = DriveIdleEvent("", info, icon, event.latitude, event.longitude)
                new_di_event.stop_begin_timestamp = event.timestamp
                new_di_event.stop_end_timestamp = event.timestamp
        
                # точку с одинаковыми координатами дважды не заносим
                # if (di_event) and (new_di_event.latitude_rounded == di_event.latitude_rounded) and (new_di_event.longitude_rounded == di_event.longitude_rounded):
                if (di_event) and IsSimilar(new_di_event.latitude, di_event.latitude) and IsSimilar(new_di_event.longitude, di_event.longitude):
                #if (di_event) and (new_di_event.lat == di_event.lat) and (new_di_event.lon == di_event.lon):
                    di_event.stop_end_timestamp = new_di_event.stop_end_timestamp
                    new_di_event = None
                else:
                    if di_event:
                        # из предыдущей точки берем окончание стоянки а из текущей - дату/время начала стоянки
                        #new_di_event.motion_begin_timestamp = di_event.stop_end_timestamp
                        #new_di_event.motion_end_timestamp = new_di_event.stop_begin_timestamp
                        
                        # добавляем новую точку в список
                        polyline_points.append(di_event)
                        di_event = None
                        di_event = new_di_event
                    else:
                        di_event = new_di_event
            
            if di_event:
                di_event.icon = 'red'
                polyline_points.append(di_event)
            
            for point in polyline_points:
                xml_marker = xml_doc.createElement("marker")
                xml_marker.setAttribute("lat", '%.6f' % point.latitude)
                xml_marker.setAttribute("lng", '%.6f' % point.longitude)
                xml_marker.setAttribute("info", point.tooltip())
                xml_marker.setAttribute("icon", point.actual_icon())
                xml_markers.appendChild(xml_marker)
            
#    filename = "%smarkers.xml" % settings.MEDIA_ROOT
#    thefile=open(filename,"w")
#    xml_doc.writexml(thefile)
#    thefile.close()
            
    return HttpResponse(xml_doc.toxml(encoding="utf-8"))
    
#------------------------------------------------------------------------------ 
@login_required
def region_save_ajax(request):
    """
    Получает данные о созданном пользователем регионе и сохраняет их. 
    """
    try:
        device_id = request.POST["device"]
        device = Device.objects.get(pk=device_id)
        
        xml_data = request.POST["xml_data"]
        
        device.limiting_region_xml = xml_data
        device.save()
        
        if xml_data == '':
            raise
        
        return HttpResponse("Limiting region succsessfuly saved.")
    except:
        return HttpResponse("Data don't contain valid region!")

#------------------------------------------------------------------------------ 
@login_required
def region_load_ajax(request):
    """
    Возвращает данные о созданном пользователем регионе. 
    """
    
    device_id = request.POST["device"]
    device = Device.objects.get(pk=device_id)
        
    xml_doc = device.limiting_region_xml
        
    if xml_doc == '':
        xml_doc = Document()
        xml_routes = xml_doc.createElement("routes")
        xml_doc.appendChild(xml_routes)
        return HttpResponse(xml_doc.toxml(encoding="utf-8"))
    
    return HttpResponse(xml_doc)

#------------------------------------------------------------------------------ 
@login_required
def region_delete_ajax(request):
    """
    Очищает регион. 
    """
    try:
        device_id = request.POST["device"]
        device = Device.objects.get(pk=device_id)
        
        device.limiting_region_xml = ""
        device.save()
        
        return HttpResponse("Limiting region succsessfuly cleared.")
    except:
        return HttpResponse("Nothing to do!")

#------------------------------------------------------------------------------
# Отчеты
#
# При открытии страницы "Reports" вызывается функция "reports()",
# она отображает пользователю форму для ввода пареметров отчета.
# 
# Функция "reports_ajax()" обрабатывает параметры отчета, полученные от пользователя
# и, в зависимости от типа отчета, вызывает соответствующую функцию отчета.
# - События за период                            events_history_ajax()
# - Превышения скорости                          speed_exceeding_ajax()
# - Время движения/стоянки                       driving_idle_time_ajax()
# - Местоположение устройств в текущий момент    last_known_location()
#------------------------------------------------------------------------------ 

#------------------------------------------------------------------------------
# Виды отчетов 
REPORT_KINDS = [("events_history", "Детали по событиям"), ("speed_exceeding", "Превышения скорости"), ("driving_idle_time", "Поездка/Стоянка суммарно"), ("driving_path_summary", "Пройденное расстояние")]

#------------------------------------------------------------------------------
class ReportsForm(forms.Form):
    "Класс формы для отчета"
    report_kind    = forms.ChoiceField(label="Вид отчета", choices=REPORT_KINDS, help_text="Выберите вид отчета")
#    device         = forms.ModelChoiceField(queryset=Device.objects.filter())
    interval_begin = forms.DateTimeField(label="Начало периода", widget=forms.TextInput(attrs={"class" : "vDateField"}), help_text="гггг-мм-дд чч:мм:сс")
    interval_end   = forms.DateTimeField(label="Конец периода", widget=forms.TextInput(attrs={"class" : "vDateField"}), help_text="гггг-мм-дд чч:мм:сс")
    speed_limit    = forms.IntegerField(label="Ограничение скорости", initial=72,  help_text="скорость в км/ч")
    
    def __init__(self, account, *args, **kwargs):
        """
        Конструктор переопределен для создания поля "device", 
        список значений для которого фильтруется в соответствии с текущим Аккаунтом  
        """
        super(ReportsForm, self).__init__(*args, **kwargs)
        self.fields["device"] = forms.ModelChoiceField(Device.objects.filter(account=account), label="Устройство")
    
#------------------------------------------------------------------------------ 
# Отчет "События за период" 
#------------------------------------------------------------------------------
def events_history_ajax(request, begin_timestamp, end_timestamp, device):
    """
    Возвращает записи EventData отфильтрованные по параметрам из формы отчета.
    """
    
    events_count = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).count()
    
    if events_count > 500:
        events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')[:500]
        get_csv = "/cvs/%s/%s/%i/%i/" % (device.id, "_", begin_timestamp, end_timestamp)
    else:
        events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')
        get_csv = None
    
    content = {"events" : events,
               "get_csv" : get_csv,
              } 
    return render_to_response("report_events_history_ajax.html", content)

#------------------------------------------------------------------------------ 
# Отчет "Превышения скорости" 
#------------------------------------------------------------------------------ 
def speed_exceeding_ajax(begin_timestamp, end_timestamp, device, max_speed):
    """
    Возвращает записи EventData отфильтрованные по параметрам из формы отчета.
    """
    events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp, speed_kph__gte=max_speed).order_by('timestamp')
            
    content = {"events" : events,
                        } 
    return render_to_response("report_speed_exceeding_ajax.html", content)

#------------------------------------------------------------------------------ 
# Отчет "Время движения/стоянки" 
#------------------------------------------------------------------------------
def driving_idle_time_ajax(begin_timestamp, end_timestamp, device):
    """
    Отчет "Время движения/стоянки".
    Возвращает записи EventData отфильтрованные по параметрам из формы отчета.
    """
    events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')
    # список "очищеных" событий, без дублей
    dirty_events = []
    # "предыдущее" событие
    di_event = None
    
    events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')
            
    # "предыдущее" событие
    di_event = None
    
    for event in events:
        new_di_event = DriveIdleEvent("", "", "", event.latitude, event.longitude)
        new_di_event.stop_begin_timestamp = event.timestamp
        new_di_event.stop_end_timestamp = event.timestamp

        # точку с одинаковыми координатами дважды не заносим
        if (di_event) and IsSimilar(new_di_event.latitude, di_event.latitude) and IsSimilar(new_di_event.longitude, di_event.longitude):
        #if (di_event) and (new_di_event.lat == di_event.lat) and (new_di_event.lon == di_event.lon):
            di_event.stop_end_timestamp = new_di_event.stop_end_timestamp
            new_di_event = None
        else:
            if di_event:
                # добавляем новую точку в список
                dirty_events.append(di_event)
                di_event = None
                di_event = new_di_event
            else:
                di_event = new_di_event
    
    if di_event:
        dirty_events.append(di_event)
    
    #--Второй цикл: группируем последовательные События движения в одно--
    clear_events = []
    di_event = None
    
    for event in dirty_events:
        if di_event == None:
            di_event = DriveIdleEvent("", "", "", event.latitude, event.longitude)
            di_event.motion_begin_timestamp = event.stop_begin_timestamp
        
        di_event.motion_end_timestamp = event.stop_begin_timestamp
        
        if event.idle_to_long():
            di_event.stop_begin_timestamp = event.stop_begin_timestamp
            di_event.stop_end_timestamp = event.stop_end_timestamp
            clear_events.append(di_event)
            di_event = None
    
    if di_event:
        clear_events.append(di_event)
        
    content = {"events" : clear_events} 
    return render_to_response("report_driving_idle_time_ajax.html", content)

#------------------------------------------------------------------------------
# Отчет "О пройденном пути за выбранное время" (в этом отчете
# должны быть пройденный путь, общее время и средняя путевая скорость -
# вычисляется как пройденный путь/время).
#----------------------------------------------------------------------------- "
def driving_path_summary(begin_timestamp, end_timestamp, device):
    """
    Отчет "Пройденный путь за выбранное время".
    """
    events = EventData.objects.filter(device__exact=device, timestamp__gte=begin_timestamp, timestamp__lte=end_timestamp).order_by('timestamp')
    # список "очищеных" событий, без дублей
    beg_time = None
    end_time = None
    
    lat = None
    lng = None
    total_distance_km = 0.0
    
    R = 6371
    
    for event in events:
        if not beg_time:
            beg_time = event.timestamp
        
        if lat:
            lat2 = event.latitude
            lng2 = event.longitude
            
            dLat = math.radians(lat2-lat)
            dLon = math.radians(lng2-lng)
            #dLat = (lat2-lat1).toRad()
            #dLon = (lon2-lon1).toRad()
            
             
            a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            total_distance_km = total_distance_km + R * c
            
            lat = None
            lng = None
        else:
            lat = event.latitude
            lng = event.longitude
        
        end_time = event.timestamp
    
    #--------------------------------------------------------------------------
    if end_time != None:
        total_time = datetime.datetime.fromtimestamp(end_time) - datetime.datetime.fromtimestamp(beg_time)
        average_velocity = "%.2f kph" % (total_distance_km / ((end_time-beg_time) / 3600))
        total_distance = "%.2f km" % total_distance_km
    
    
        content = {"total_time" : total_time,
               "total_distance" : total_distance,
               "average_velocity" : average_velocity,
               }
        return render_to_response("report_driving_path_summary_ajax.html", content)
    else:
        return HttpResponse("")

#------------------------------------------------------------------------------ 
# Отчет "Местоположение устройств в текущий момент" 
#------------------------------------------------------------------------------

#import Image,ImageDraw
#from django.conf import settings
from random import randint as rint

@login_required 
def last_known_location(request):
    """
    Местоположение устройств в текущий момент.
    Выводится при загрузке главной страницы.
    """

    #-----------------------------------------------------------------
    # 10 картинок для меток от Гугл-мепс
    icon_kinds = ('blue', 'green', 'red', 'orange', 'purple', 'yellow', 'brown', 'gray', 'white', 'black')
    
    icons_script_text = 'var customIcons = [];\n'
    
    icon = 0
    for icon_kind in icon_kinds:
        icons_script_text = icons_script_text + 'var %sIcon = (new GIcon(baseIcon, "http://labs.google.com/ridefinder/images/mm_20_%s.png", null, "")); \n' % (icon_kind, icon_kind)
        icons_script_text = icons_script_text + 'customIcons[%i] = %sIcon;\n' % (icon, icon_kind)
        icon = icon + 1
    
    #------------------------------------------------------------------------------ 
    events = last_event_for_devices(request)

    # список точек для карты
    google_points = []
    # первая точка - для центрирования карты
    first_point = ""
    icon = 0 #'"blue"'
    
    for event in events:
        if first_point=="":
            first_point = "new GLatLng(%.6f, %.6f)" % (event.latitude, event.longitude)

        html = "new GLatLng(%.6f, %.6f)" % (event.latitude, event.longitude)
                    
        info_date = str(datetime.datetime.fromtimestamp(event.timestamp))
        info = '"<b>%s</b> <br><b>%.2f km/h</b> <br>Date/time: %s <br>GPS: %s, %s "' %(event.device, event.speed_kph, info_date, event.lat(), event.lon())
        
## Код для генерации маркера случайного цвета
## (!) Случайно выбираемые цвета часто "несимпатичны"
#
#        img = Image.new("RGB", (12, 12), None)
#        draw = ImageDraw.Draw(img)
#
#        r,g,b = rint(128,255), rint(128,255), rint(128,255)
#        draw.ellipse((1,1,11,11), fill=(int(r),int(g),int(b)), outline=0)
#
#        filename = "%s%i.png" % (settings.MEDIA_ROOT, icon)
#        img.save(filename, "PNG")
        
        event.icon = 'http://labs.google.com/ridefinder/images/mm_20_%s.png' % (icon_kinds[icon])
        gmarker = DriveIdleEvent(html, info, icon, event.latitude, event.longitude)
        google_points.append(gmarker)    
        
        icon = icon + 1
        if icon > 10:
            icon = 0
        
    #-----------------------------------------------------------------
    sub_title = "Последнее месторасположение ТС"
    
    content = {"sub_title" : sub_title,
               "events" : events,
               "google_points" : google_points,
               "first_point" : first_point,
               "icons_script_text" : icons_script_text,}
                       
    return render_to_response("report_last_known_location.html", content)

#------------------------------------------------------------------------------
@login_required 
def reports(request):
    """
    Выводим форму с параметрами отчета.
    Введенные пользователем параметры вернутся посредством AJAX-запроса из "reports_ajax"
    Виды отчетов:
     - События за период
     - Превышения скорости
     - Время движения/стоянки
     
    (!) Отчет "Местоположение устройств в текущий момент" выводится при загрузке главной страницы
    """
    
    account = request.user.gts_user.account
    
    reports_form = ReportsForm(account)
    
    content = {"reports_form" : reports_form}
    
    return render_to_response("reports.html", content)

#------------------------------------------------------------------------------
@login_required 
def reports_ajax(request):
    """
    Обрабатывает AJAX-запрос.
    Возвращает результат отчета в соответствии с типом отчета.
    """
    
    account = request.user.gts_user.account
    
    if request.method == "POST":
        reports_form = ReportsForm(account, request.POST)
        if reports_form.is_valid():
            interval_begin = reports_form.clean_data['interval_begin']
            interval_end = reports_form.clean_data['interval_end']
            device = reports_form.clean_data['device']
            report_kind = reports_form.clean_data['report_kind']
            speed_limit = reports_form.clean_data['speed_limit']
            
            # if time not specified, we will assign time = end of day
            if (interval_end.hour == 0) and (interval_end.minute == 0) and (interval_end.second == 0):
                interval_end = interval_end.replace(hour = 23, minute = 59, second = 59)
            
            begin_timestamp = time.mktime(interval_begin.timetuple())
            end_timestamp = time.mktime(interval_end.timetuple())
            
            if report_kind == "events_history":
                return events_history_ajax(request, begin_timestamp, end_timestamp, device)
            elif report_kind == "speed_exceeding":
                #max_speed = 72.0;
                return speed_exceeding_ajax(begin_timestamp, end_timestamp, device, speed_limit)
            elif report_kind == "driving_idle_time":
                return driving_idle_time_ajax(begin_timestamp, end_timestamp, device)
            elif report_kind == "driving_path_summary":
                return driving_path_summary(begin_timestamp, end_timestamp, device)
            #------------------------------------------------------------------

    return HttpResponse("")

#------------------------------------------------------------------------------ 
