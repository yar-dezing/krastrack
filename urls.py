# -*- coding: utf-8 -*-

#===============================================================================
# DjangoGTS project url conf. file
# 2007-09-07: Sergeyev V.V.
#===============================================================================

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    # (r'^DjangoGTS/', include('DjangoGTS.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': 'django.conf'}),
    (r'^appmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    #(r'^$', 'GTS.views.show_index'),
    (r'^$', 'GTS.views.last_known_location'),
    
    (r'^accounts/login/$', 'GTS.views.login_user'),
    (r'^accounts/logout/$', 'GTS.views.logout_user'),
    
    (r'^gts_accounts/$', 'GTS.views.account_detail'),
    #(r'^gts_accounts/$', 'GTS.views.accounts_list'),
    #(r'^gts_accounts/add/$', 'GTS.views.account_add'),
    (r'^gts_accounts/(?P<account_id>\w+)/$', 'GTS.views.account_detail'),
    
    (r'^users/$', 'GTS.views.users_list'),
    (r'^users/add/$', 'GTS.views.user_add'),
    (r'^users/(?P<user_id>\w+)/$', 'GTS.views.user_detail'),
    
    (r'^devices/$', 'GTS.views.devices_list'),
    (r'^devices/add/$', 'GTS.views.device_add'),
    (r'^device_name_check/$', 'GTS.views.device_name_check'),
    (r'^devices/(?P<device_id>\w+)/$', 'GTS.views.device_detail'),
    (r'^devices/(?P<device_id>\w+)/delete/$', 'GTS.views.device_delete'),
    
    (r'^reports/$', 'GTS.views.reports'),
    (r'^reports_ajax/$', 'GTS.views.reports_ajax'),
    #(r'^', include('DjangoGTS.GTS.urls')),
    (r'^cvs/(?P<username>\w+)/(?P<password>\w+)/(?P<interval_begin>\w+)/(?P<interval_end>\w+)/$', 'GTS.views.events_history_csv'),
    
    #Part #2
    (r'^map/$', 'GTS.views.google_map'),
    (r'^map_ajax/$', 'GTS.views.google_map_ajax'),
    (r'^region_save_ajax/$', 'GTS.views.region_save_ajax'),
    (r'^region_load_ajax/$', 'GTS.views.region_load_ajax'),
    (r'^region_delete_ajax/$', 'GTS.views.region_delete_ajax'),
    
)
