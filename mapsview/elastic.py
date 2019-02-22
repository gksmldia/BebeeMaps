from django.db import models
from django.utils import timezone
import elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import GeoPoint
import json

es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200/")
def es_list(param):
    print('es_list')
    must, filters = {}, []
    if param['q'] is None or param['q'] is "":
        print("queryString is None")
        must = { "match_all" : {} }
    else:
        if param['field'] is None or param['field'] is "":
            print("field is None")
            must = [
                {
                    "query_string" : {
                        "default_field" : "messages",
                        "query" : "*" + param['q'] +"*",
                        "fuzzy_prefix_length": 1
                    }
                }
            ]
        else:
            print("queryString and field are not None")
            must = [
                {
                    "fuzzy" : {
                        param['field']: {
                            "value"    : param['q'],
                            "fuzziness": 1
                        }
                    }
                }
            ]

    if not param['is_superuser']:
        filters.append({ "terms":  {"ID": searchByPersonal(param['user'])} })

    if param['loc'] is not None and not param['is_superuser']:
        print(param['loc'])
        filters.append({
                            "geo_distance": {
                                "distance": "1km",
                                "location": {
                                    "lon" : param['loc']['lng'],
                                    "lat" : param['loc']['lat']
                                }
                            }
                        })
    
    body = {
                'size': 100,
                "query": {
                    "bool": { 
                        "must": must,
                        "filter": filters
                    }
                }
            }
    print("query >>>\n" + json.dumps(body, indent=2, sort_keys=True, ensure_ascii=False))
    
    data = es_client.search(index = 'place',
                            doc_type = 'doc',
                            body = body)
    
    print("data >>>\n " + str(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)))
    
    matList = data['hits']['hits']
    
    return matList


def searchByPersonal(user_id):
    # es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    personal_data = es_client.search(index = 'personal',
                                    doc_type = 'doc',
                                    body = {
                                        'size': 100,
                                        "query" : {
                                            "term" : {"U_ID" : user_id}
                                        }
                                    })['hits']['hits']
            
    personal_mat_ids = [x['_source']['M_ID'] for x in personal_data]
    personal_mat_ids.sort()

    return list(set(personal_mat_ids))

def searchByConnetLoc(user_id, addr):
    # es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    mat_data = es_client.search(index = 'place',
                                doc_type = 'doc',
                                body = {
                                    "query" : {
                                        "bool": {
                                            "must": [
                                                {
                                                    "match": {
                                                        "LB_ADDR": '*' + addr + '*'
                                                    }
                                                }
                                            ],
                                            "filter": {
                                                "terms": {
                                                    "ID": searchByPersonal(user_id)
                                                }
                                            }
                                        }
                                    }
                                })['hits']['hits']
    return mat_data

def sub_type_list(queryString) :
    print('sub_type_list')
    # es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200/")
    if queryString is None or queryString is "":
        data = es_client.search(index = 'subtype',
                                    doc_type = 'doc',
                                    body = {
                                        'size': 100,
                                    })
    else:
        data = es_client.search(index = 'subtype',
                                    doc_type = 'doc',
                                    body = {
                                        'query' : {
                                            'query_string' : {
                                                'default_field': 'TYPE',
                                                'query' : queryString
                                            }
                                        }
                                    })
    sub_type_list = data['hits']['hits']
    return sub_type_list

def es_last_index(index):
    # es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200/")
    print('es_last_index')
    field = None
    if index is 'personal' : field = '_id'
    else : field = 'ID'

    total = es_client.search(index = index,
                            doc_type = 'doc',
                            body = {
                                "sort": {field: 'desc'},
                                "size": 1
                            })
    
    print(total['hits']['hits'])
    id = 0
    for one in total['hits']['hits']:
       id = one['_id']
    
    return int(id)

def es_search_by_id(search_id):
    print('es_search_by_id')
    data = es_client.get(index = 'place',
                        doc_type = 'doc',
                        id = search_id)

    return data['_source']

def es_insert(place):
    print('es_insert')

    last_index_place = es_last_index('place')+1
    source = getSource(place, last_index_place)
    
    docs = []
    for cnt in range(1):
        docs.append({
            '_index': 'place',
            '_type': 'doc',
            "_id": last_index_place,
            '_source': source
        })

    response = elasticsearch.helpers.bulk(es_client, docs)

    response2 = es_insert_personal(last_index_place, int(place.get('user')))
    return (response, response2)

def es_request_insert(place):
    print('es_request_insert')
    print(type(place['location']['lat']))
    last_index_place = es_last_index('place')+1
    source = getSource(place, last_index_place)
    
    response = es_client.transport.perform_request(
                method = 'PUT',
                url = '/place/doc/'+ str(last_index_place),
                body = source
            )
    
    response2 = es_insert_personal(last_index_place, int(place.get('user')))
    
    return (response, response2)

def es_insert_personal(p_id, u_id):
    last_index_personal = es_last_index('personal')+1
    result = es_client.transport.perform_request(
                method = 'PUT',
                url = '/personal/doc/'+ str(last_index_personal),
                body = {
                    'M_ID': p_id,
                    'U_ID': u_id
                }
            )
    print(result)

    return result

def es_update(place):
    print('es_update')
    up_data = es_client.update(
        index = 'place',
        doc_type = 'doc',
        id = int(place.get('ID')),
        body = getSource(place, int(place.get('ID')))
    )
    print(up_data)
    return up_data

def getSource(place, index): 
    location = GeoPoint(lat_lon=True)
    location = {
        'lon': float("{0:.7f}".format(place['location']['lon'])), 
        'lat': float("{0:.7f}".format(place['location']['lat']))
    }
    
    print("index >>" + str(index))
    source = {
        'ID': index, 
        'NAME': place.get('NAME'), 
        'RN_ADDR': place.get('RN_ADDR'), 
        'LB_ADDR': place.get('LB_ADDR'), 
        'DETAIL_ADDR': place.get('DETAIL_ADDR') if 'DETAIL_ADDR' in place else None, 
        'TEL': place.get('TEL') if 'TEL' in place else None, 
        'OFF_DAY': place.get('OFF_DAY') if 'OFF_DAY' in place else None, 
        'SALES_FROM': place.get('SALES_FROM') if 'SALES_FROM' in place else None,
        'SALES_TO': place.get('SALES_TO') if 'SALES_TO' in place else None,
        'BREAK_FROM': place.get('BREAK_FROM') if 'BREAK_FROM' in place else None,
        'BREAK_TO': place.get('BREAK_TO') if 'BREAK_TO' in place else None,
        'PARKING': place.get('PARKING') if 'PARKING' in place else None,
        'TYPE': place.get('TYPE') if 'TYPE' in place else None,
        'SUB_TYPE': place.get('SUB_TYPE') if 'SUB_TYPE' in place else None,
        'DESC': place.get('DESC') if 'DESC' in place else None,
        'TRY': place.get('TRY') if 'TRY' in place else None,
        'TAG': place.get('TAG') if 'TAG' in place else None,
        'location': location
    }
    
    return source

def es_delete(id):

    result = {}
    try:
        result = es_client.delete(index = 'place', doc_type = 'doc', id=id)
    except Exception as e:
        result['result'] = e.args[1]
    return result
        
