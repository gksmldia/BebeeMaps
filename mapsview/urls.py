from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.map_list, name='map_list'),
    url(r'^map/(\d+)/$', views.map_detail, name='map_detail'),
    url(r'^api/sub_type_list/$', views.sub_type_list, name='sub_type_list'),
    url(r'^api/enroll_map/$', views.enroll_map, name='enroll_map'),
]