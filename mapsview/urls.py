from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

app_name = "mapsview"

urlpatterns = [
    url(r'^$', views.index_view, name='index_view'),
    url(r'^detail/(\d+)/$', views.detail_map, name='detail_map'),
    url(r'^list_map/$', views.list_map, name='list_map'),
    url(r'^api/map_list/$', views.map_list, name='map_list'),
    url(r'^api/sub_type_list/$', views.sub_type_list, name='sub_type_list'),
    url(r'^api/enroll_map/$', views.enroll_map, name='enroll_map'),
    url(r'^api/modify_map/$', views.modify_map, name='modify_map'),
    url(r'^api/delete_map/(\d+)/$', views.delete_map, name='delete_map'),
    url(r'^api/searchGetEs$', views.searchGetEs, name='searchGetEs'),
]