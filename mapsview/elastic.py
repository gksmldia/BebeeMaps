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

        if not param['is_superuser']:
            filters.append({ "terms":  {"ID": searchByPersonal(param['user'])} })

            if param['loc'] is not None:
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
                    "size": 100,
                    "sort": { "ID": "desc" },
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

        matList = data['hits']['hits']
    else:
        matList = get_multi_search_data(param['user'], param['field'], param['q'])

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

    personal_mat_ids = [x['_source']['P_ID'] for x in personal_data]
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

def searchByLocation(loc):
    mat_data = es_client.search(index = 'place',
                                doc_type = 'doc',
                                body = {
                                    "query" : {
                                        "bool": {
                                            "must" : {
                                                "match_all" : {}
                                            },
                                            "filter" : {
                                                "geo_distance" : {
                                                    "distance" : "10m",
                                                    "location" : {
                                                        "lat" : loc['lat'],
                                                        "lon" : loc['lon']
                                                    }
                                                }
                                            }
                                        }
                                    }
                                })['hits']['hits']
    return mat_data

def get_multi_search_data(u_id, field, query):
    multi_search_body = [
        {"index": "personal", "type": "doc"}, 
        {"query": {"term": {"U_ID": u_id}}, "from": 0, "size": 100},
        {"index": "place", "type": "doc"}
    ]
    if field is None or field is "":
        multi_search_body.append({
            "query": {
                "bool" : {
                    "must" : {
                        "fuzzy" : {
                            "messages" : {
                                "value": query,
                                "boost": 1.0,
                                "fuzziness": 1,
                                "prefix_length": 0,
                                "max_expansions": 100
                            }
                        }
                    }
                }
            }, "from": 0, "size": 100
        })

    else:
        multi_search_body.append({
            "query": {
                "bool" : {
                    "must" : [{
                        "fuzzy" : {
                            field: {
                                "value"     : query,
                                "fuzziness" : 1
                            }
                        }
                    }]
                }
            }, "from": 0, "size": 100
        })

    print("query >>>\n" + json.dumps(multi_search_body, indent=2, sort_keys=True, ensure_ascii=False))
    data = es_client.msearch(body = multi_search_body)

    p1 = data['responses'][0]['hits']['hits']
    p2 = data['responses'][1]['hits']['hits']
    # print("data 1 >>> " + simplejson.dumps(p1, indent=2, sort_keys=True, ensure_ascii=False))
    # print("data 2 >>> " + simplejson.dumps(p2, indent=2, sort_keys=True, ensure_ascii=False))

    mat_data = []
    for private in p1:
        for query in p2:
            if(query["_source"]["ID"] == private["_source"]["P_ID"]):
                mat_data.append(query)

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

    total = es_client.search(index = index,
                            doc_type = 'doc',
                            body = {
                                "query": {
                                    "match_all": {}
                                }
                            })

    print(total['hits']['total'])
    id = int(total['hits']['total'])+1

    return id

def es_search_by_id(search_id):
    print('es_search_by_id')
    data = es_client.get(index = 'place',
                        doc_type = 'doc',
                        id = search_id)

    return data['_source']

def es_search_by_persnal_detail(p_id, u_id):
    print('es_search_by_persnal_detail')
    person_data = es_client.search(index = 'personal',
                                    doc_type = 'doc',
                                    body = {
                                        "query" : {
                                            "bool": {
                                                "must": [
                                                    { "match": { "P_ID": p_id } },
                                                    { "match": { "U_ID": u_id } }
                                                ]
                                            }
                                        }
                                    })['hits']['hits'][0]
    
    person_return_data = person_data['_source']
    person_return_data['_id'] = person_data['_id']

    return person_return_data

def es_insert(place):
    print('es_insert')

    last_index_place = es_last_index('place')+1
    last_index_personal = es_last_index('personal')+1
    p_source = getSourcePlace(place, last_index_place)
    u_source = getSourcePersonal(place, last_index_place)

    docs = []
    for cnt in range(1):
        docs.append({
            '_index': 'place',
            '_type': 'doc',
            "_id": last_index_place,
            '_source': p_source
        })

        docs.append({
            '_index': 'personal',
            '_type': 'doc',
            "_id": last_index_personal,
            '_source': u_source
        })

    response = elasticsearch.helpers.bulk(es_client, docs)

    # response2 = es_insert_personal(last_index_place, int(place.get('user')))
    return response

def es_request_insert(place):
    print('es_request_insert')
    last_index_place = es_last_index('place')+1
    p_source = getSourcePlace(place, last_index_place)

    response = es_client.transport.perform_request(
                method = 'PUT',
                url = '/place/doc/'+ str(last_index_place),
                body = p_source
            )

    response2 = es_insert_personal(place, last_index_place)

    return (response, response2)

def es_insert_personal(data, p_id):
    last_index_personal = es_last_index('personal')+1
    result = es_client.transport.perform_request(
                method = 'PUT',
                url = '/personal/doc/'+ str(last_index_personal),
                body = {
                    'P_ID': p_id,
                    'U_ID': int(data.get('user')),
                    'DESC': data.get('DESC') if 'DESC' in data else None,
                    'TRY': data.get('TRY') if 'TRY' in data else None,
                    'TAG': data.get('TAG') if 'TAG' in data else None
                }
            )
    print(result)

    return result

def es_update(place):
    print('es_update')
    place_body = getSourcePlace(place, int(place.get('ID')))
    print("place_update >>>\n" + json.dumps(place_body, indent=2, sort_keys=True, ensure_ascii=False))
    place_update = es_client.update(
        index = 'place',
        doc_type = 'doc',
        id = int(place.get('ID')),
        body = place_body
    )

    personal_body = getSourcePersonal(place, int(place.get('ID')))
    print("personal_update >>>\n" + json.dumps(personal_body, indent=2, sort_keys=True, ensure_ascii=False))
    personal_update = es_client.update(
        index = 'personal',
        doc_type = 'doc',
        id = int(place.get('personal_id')),
        body = personal_body
    )
    print(place_update)
    return (place_update, personal_update)

def getSourcePlace(place, index):
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
        'SUB_TYPE': place.get('SUB_TYPE') if 'SUB_TYPE' in place else None,\
        'location': location
    }

    return source

def getSourcePersonal(personal, p_index):

    source = {
        'U_ID': personal.get('user'),
        'P_ID': p_index,
        'DESC': personal.get('DESC') if 'DESC' in personal else None,
        'TRY': personal.get('TRY') if 'TRY' in personal else None,
        'TAG': personal.get('TAG') if 'TAG' in personal else None
    }

    return source

def es_delete(id):

    result = {}
    try:
        result = es_client.delete(index = 'place', doc_type = 'doc', id=id)
    except Exception as e:
        result['result'] = e.args[1]
    return result

