from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
import json
from . import models as m, elastic as e

def index_view(request):
    if (request.user.is_anonymous):
        return redirect('member:login')
    else:
        return render(request, 'mapviews/map_list.html', {})

@csrf_exempt
@require_POST
def map_list(request):
    print("map_list")
    if request.method == 'POST':
        body = json.loads(request.body)
        body['is_superuser'] = request.user.is_superuser
        
        result = [mat['_source'] for mat in e.es_list(body)]
            
        return HttpResponse(json.dumps(result), content_type='application/json; charset=utf-8')

def list_map(request):
    return render(request, 'mapviews/map_list.html', {})

def sub_type_list(request):
    query = request.GET.get('q')
    subTypeList = []

    for _type in e.sub_type_list(query):
        subTypeList.append(_type['_source'])

    return HttpResponse( json.dumps(subTypeList), content_type='application/json; charset=utf-8')

def searchGetEs(request):
    loc = {
        'lat': request.GET.get('lat'),
        'lon': request.GET.get('lng')
    }
    print(loc['lat'])
    result = e.searchByLocation(loc)

    return HttpResponse(json.dumps(result), content_type='application/json; charset=utf-8')

@csrf_exempt
@require_POST
def enroll_map(request):
    print("enroll_map")
    if request.method == 'POST':
        body = json.loads(request.body)
        # result = e.es_request_insert(body)
        result = e.es_insert(body)
        return HttpResponse(json.dumps(result), content_type='application/json; charset=utf-8')


def detail_map(request, user, id):

    result = e.es_search_by_id(id)
    result2 = e.es_search_by_persnal_detail(id, user)
    return render(request, 'mapviews/map_detail.html', { 'p_info': result
                                                        , 'p_info2': json.dumps(result)
                                                        , 'u_info': result2
                                                        , 'u_info2': json.dumps(result2) })


@csrf_exempt
@require_POST
def modify_map(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        result = e.es_update(body)
        return HttpResponse(json.dumps(result), content_type='application/json; charset=utf-8')


def delete_map(request, id):

    result = e.es_delete(id)
    return HttpResponse(json.dumps(result), content_type='application/json; charset=utf-8')

def is_None(param):
    if param is None or param is "":
        param = None
    return param
