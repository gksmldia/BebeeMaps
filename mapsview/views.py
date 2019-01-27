from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
import json
from . import models as m

# Create your views here.

def map_list(request):
    query = request.GET.get('q')
    field = request.GET.get('field')
    # print(request.is_ajax())

    mat_list = []
    for mat in m.list(query, field):
        mat['_source']['_id'] = mat['_id']
        mat_list.append(mat['_source'])

    json_list = json.dumps(mat_list)

    if request.is_ajax():
        return HttpResponse(json_list, content_type='application/json; charset=utf-8')
    else:
        return render(request, 'map_list.html', {'list': json_list})

def sub_type_list(request):
    query = request.GET.get('q')
    subTypeList = []

    for _type in m.sub_type_list(query) :
        subTypeList.append(_type['_source'])
        
    return HttpResponse(json.dumps(subTypeList), content_type='application/json; charset=utf-8')

@csrf_exempt
@require_POST
def enroll_map(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        result = m.es_request_insert(body)
        print(result)
        return HttpResponse(json.dumps(result), content_type='application/json; charset=utf-8')

def map_detail(request, id):
    
    result = m.es_search_by_id(id)
    return render(request, 'mapviews/map_detail.html', {'info': result, 'info2': json.dumps(result)})
    