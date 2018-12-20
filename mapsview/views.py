from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
import json
from . import models as m

# Create your views here.

def post_list(request):
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
        return render(request, 'post_list.html', {'list': json_list})

def sub_type_list(request):
    subTypeList = []

    for _type in m.sub_type_list() :
        subTypeList.append(_type['_source'])
        
    return HttpResponse(json.dumps(subTypeList), content_type='application/json; charset=utf-8')

@csrf_protect
@require_POST
def regist_zip(request):
    if request.method == 'POST':
        print(request.body)
        body = json.loads(request.body)
        print(body.get('RN_ADDR'))
    