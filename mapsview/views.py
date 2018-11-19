from django.shortcuts import render
from django.utils import timezone
import json
from . import models as m

# Create your views here.

def post_list(request):
    query = str(request.GET.get('q'))
    field = str(request.GET.get('field'))
    print("query >> " + query + ", field >> " + field)
    mat_list = []
    for mat in m.list(query, field):
        mat['_source']['_id'] = mat['_id']
        mat_list.append(mat['_source'])
        
    json_list = json.dumps(mat_list)
    return render(request, 'post_list.html', {'list': json_list})
