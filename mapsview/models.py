from django.db import models
from django.utils import timezone
import elasticsearch
from elasticsearch import helpers
import json
import json as simplejson

def list(queryString, field):
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
    print('list')
    if queryString is None or queryString is "":
        print("queryString is None")
        data = es_client.search(index = 'matzip',
                                doc_type = 'doc',
                                body = {
                                    'size': 100,
                                    'sort': {'ID': 'desc'}
                                })
    else:
        if field is None or field is "":
            print("field is None")
            data = es_client.search(index = 'matzip',
                                    doc_type = 'doc',
                                    body = {
                                        'size': 100,
                                        'query' : {
                                            'query_string' : {
                                                'query' : '*' + queryString + '*'
                                            }
                                        }
                                    })
        else:
            print("field is not None")
            data = es_client.search(index = 'matzip',
                                    doc_type = 'doc',
                                    body = {
                                        'size': 100,
                                        'query' : {
                                            'query_string' : {
                                                'default_field': field,
                                                'query' : '*' + queryString + '*'
                                            }
                                        }
                                    })
    
    matList = data['hits']['hits']

    return matList

def sub_type_list(queryString) :
    print('sub_type_list')
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
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

def es_insert(matzip):
    print('es_insert')
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
    source = {
                'ID': es_last_index()+1, 
                'NAME': matzip.get('NAME'), 
                'RN_ADDR': matzip.get('RN_ADDR'), 
                'LB_ADDR': matzip.get('LB_ADDR'), 
                'DETAIL_ADDR': matzip.get('DETAIL_ADDR') if 'DETAIL_ADDR' in matzip else None, 
                'TEL': matzip.get('TEL') if 'TEL' in matzip else None, 
                'OFF_DAY': matzip.get('OFF_DAY') if 'OFF_DAY' in matzip else None, 
                'SALES_FROM': matzip.get('SALES_FROM') if 'SALES_FROM' in matzip else None,
                'SALES_TO': matzip.get('SALES_TO') if 'SALES_TO' in matzip else None,
                'BREAK_FROM': matzip.get('BREAK_FROM') if 'BREAK_FROM' in matzip else None,
                'BREAK_TO': matzip.get('BREAK_TO') if 'BREAK_TO' in matzip else None,
                'PARKING': matzip.get('PARKING') if 'PARKING' in matzip else None,
                'TYPE': matzip.get('TYPE') if 'TYPE' in matzip else None,
                'SUB_TYPE': matzip.get('SUB_TYPE') if 'SUB_TYPE' in matzip else None,
                'DESC': matzip.get('DESC') if 'DESC' in matzip else None,
                'TRY': matzip.get('TRY') if 'TRY' in matzip else None,
                'TAG': matzip.get('TAG') if 'TAG' in matzip else None,
                'lat': matzip.get('lat') if 'lat' in matzip else None,
                'lng': matzip.get('lng') if 'lng' in matzip else None
            }
    
    docs = []
    for cnt in range(1):
        docs.append({
            '_index': 'matzip',
            '_type': 'doc',
            '_source': source
        })

    elasticsearch.helpers.bulk(es_client, docs)

def es_request_insert(matzip):
    print('es_request_insert')
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
    last_index = es_last_index()+1
    source = {
                'ID': last_index, 
                'NAME': matzip.get('NAME'), 
                'RN_ADDR': matzip.get('RN_ADDR'), 
                'LB_ADDR': matzip.get('LB_ADDR'), 
                'DETAIL_ADDR': matzip.get('DETAIL_ADDR') if 'DETAIL_ADDR' in matzip else None, 
                'TEL': matzip.get('TEL') if 'TEL' in matzip else None, 
                'OFF_DAY': matzip.get('OFF_DAY') if 'OFF_DAY' in matzip else None, 
                'SALES_FROM': matzip.get('SALES_FROM') if 'SALES_FROM' in matzip else None,
                'SALES_TO': matzip.get('SALES_TO') if 'SALES_TO' in matzip else None,
                'BREAK_FROM': matzip.get('BREAK_FROM') if 'BREAK_FROM' in matzip else None,
                'BREAK_TO': matzip.get('BREAK_TO') if 'BREAK_TO' in matzip else None,
                'PARKING': matzip.get('PARKING') if 'PARKING' in matzip else None,
                'TYPE': matzip.get('TYPE') if 'TYPE' in matzip else None,
                'SUB_TYPE': matzip.get('SUB_TYPE') if 'SUB_TYPE' in matzip else None,
                'DESC': matzip.get('DESC') if 'DESC' in matzip else None,
                'TRY': matzip.get('TRY') if 'TRY' in matzip else None,
                'TAG': matzip.get('TAG') if 'TAG' in matzip else None,
                'lat': matzip.get('lat') if 'lat' in matzip else None,
                'lng': matzip.get('lng') if 'lng' in matzip else None
            }
    
    result = es_client.transport.perform_request(
                method = 'PUT',
                url = '/matzip/doc/'+ str(last_index),
                body = source
            )
    
    return result

def es_last_index():
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
    print('es_last_index')
    count = es_client.count(index = 'matzip', 
                            doc_type = 'doc', 
                            body = { "query": {"match_all" : { }}})
    
    total = es_client.search(index = 'matzip',
                            doc_type = 'doc',
                            body = {
                                "query" : {
                                    "match_all": {}
                                },
                                "size": count['count'],
                                "script_fields" : {
                                    "ID" : {
                                        "script" : {
                                            "source": "params['_source']['ID']"
                                        }
                                    }
                                }
                            })
    
    ids = []
    for one in total['hits']['hits']:
       ids.extend(one['fields']['ID'])
    
    ids.sort()

    
    return ids[len(ids)-1]

def es_search_by_id(search_id):
    print('es_search_by_id')
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
    data = es_client.get(index = 'matzip',
                        doc_type = 'doc',
                        id = search_id)

    return data['_source']

def es_update(matzip):
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
    print('es_update')
    up_data = es_client.update(
        index = 'matzip',
        doc_type = 'doc',
        id = int(matzip.get('ID')),
        body = {
            'doc': {
                'ID': int(matzip.get('ID')), 
                'NAME': matzip.get('NAME'), 
                'RN_ADDR': matzip.get('RN_ADDR'), 
                'LB_ADDR': matzip.get('LB_ADDR'), 
                'DETAIL_ADDR': matzip.get('DETAIL_ADDR'),
                'TEL': matzip.get('TEL'), 
                'OFF_DAY': matzip.get('OFF_DAY'), 
                'PARKING': matzip.get('PARKING'),
                'DESC': matzip.get('DESC'), 
                'TYPE': matzip.get('TYPE'), 
                'BREAK_FROM': matzip.get('BREAK_FROM'), 
                'BREAK_TO': matzip.get('BREAK_TO'), 
                'SALES_FROM': matzip.get('SALES_FROM'), 
                'SALES_TO': matzip.get('SALES_TO'), 
                'SUB_TYPE': matzip.get('SUB_TYPE'), 
                'TRY': matzip.get('TRY'),
                'TAG': matzip.get('TAG'),
                'lat': matzip.get('lat'),
                'lng': matzip.get('lng')
            }
        }
    )
    print(up_data)
    return up_data

def es_delete(id):
    es_client = elasticsearch.Elasticsearch("http://3.17.187.92:9201")
    
    result = {}
    try:
        result = es_client.delete(index = 'matzip', doc_type = 'doc', id=id)
    except Exception as e:
        result['result'] = e.args[1]
    return result
        
