from django.test import TestCase
from django.db import models
from django.utils import timezone
import elasticsearch
from elasticsearch import helpers
import urllib
import json as simplejson

googleGeocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?'
es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")

def list():
    # print(field)
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    data = es_client.search(index = 'matzip',
                            doc_type = 'doc',
                            body = {
                                'size': 100,
                            })
    
    matList = data['hits']['hits']

    return matList

def searchById(search_id):
    # print(field)
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    data = es_client.get(index = 'matzip',
                        doc_type = 'doc',
                        id = search_id)
    
    # matList = data['_source']

    return [data]
   
def get_coordinates_list(matList, from_sensor=False):
    # query = query.encode('utf-8')

    for matdict in matList:
        params = {
            'address': matdict['_source']['RN_ADDR'],
            'sensor': "true" if from_sensor else "false",
            'key': "AIzaSyBXIuWo67i4fta6gAQv7VDiIF7ZJZ3GJ9w"
        }
        
        url = googleGeocodeUrl + urllib.parse.urlencode(params)
        json_response = urllib.request.urlopen(url)
        response = simplejson.loads(json_response.read())
        if response['results']:
            location = response['results'][0]['geometry']['location']
            matdict['_source']['lat'] = location['lat']
            matdict['_source']['lng'] = location['lng']
        else:
            matdict['_source']['lat'], matdict['_source']['lng'] = None, None
            print(matdict['_source']['RN_ADDR'], "<no results>")
    return matList

def get_coordinates(addr, from_sensor=False):
    # query = query.encode('utf-8')

    params = {
        'address': addr,
        'sensor': "true" if from_sensor else "false",
        'key': "AIzaSyBXIuWo67i4fta6gAQv7VDiIF7ZJZ3GJ9w"
    }
    
    url = googleGeocodeUrl + urllib.parse.urlencode(params)
    json_response = urllib.request.urlopen(url)
    response = simplejson.loads(json_response.read())
    # lat, lng = 0, 0
    if response['results']:
        location = response['results'][0]['geometry']['location']
        lat = location['lat']
        lng = location['lng']
    else:
        lat, lng = None, None
        print(addr, "<no results>")
    
    return (lat, lng)

def es_update(lists):
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    
    for one in lists :
        updata = es_client.update(
            index = 'matzip',
            doc_type = 'doc',
            id = one['_id'],
            body = {
                'doc': {
                    'ID': int(one['_source']['ID']), 
                    'TEL': one['_source']['TEL'], 
                    'DETAIL_ADDR': one['_source']['DETAIL_ADDR'], 
                    'RN_ADDR': one['_source']['RN_ADDR'], 
                    'PARKING': one['_source']['PARKING'],
                    'DESC': one['_source']['DESC'], 
                    'NAME': one['_source']['NAME'], 
                    'BREAK': one['_source']['BREAK'], 
                    'TYPE': one['_source']['TYPE'], 
                    'FROM-TO': one['_source']['FROM-TO'], 
                    'SUB_TYPE': one['_source']['SUB_TYPE'], 
                    'LB_ADDR': one['_source']['LB_ADDR'], 
                    'OFF_DAY': one['_source']['OFF_DAY'], 
                    'TRY': one['_source']['TRY'], 
                    'lng': one['_source']['lng'], 
                    'lat': one['_source']['lat'],
                    'tag': []
                }
            }
        )

        print(updata)

def es_insert():
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    addr = '경남 진주시 촉석로 165'
    latLng = get_coordinates(addr)
    source = {
                'ID': es_last_index()+1, 
                'NAME': '원깐돌이', 
                'RN_ADDR': addr, 
                'LB_ADDR': '중안동 101', 
                'DETAIL_ADDR': None, 
                'TEL': '055-742-3937', 
                'PARKING': 'FALSE',
                'OFF_DAY': ['SUN'], 
                'FROM-TO': '10:00 ~ 17:00',
                'BREAK': None,
                'TYPE': 'M',
                'SUB_TYPE': 'K', 
                'TRY': 'TRUE',
                'DESC': '사실은 국수맛집, 육회비빔밥도, 알쓸신잡 진주편 수다장소',
                'lat': latLng[0],
                'lng': latLng[1]
            }
    # print(latLng[0], latLng[1])
    docs = []
    for cnt in range(1):
        docs.append({
            '_index': 'matzip',
            '_type': 'doc',
            '_source': source
        })

    elasticsearch.helpers.bulk(es_client, docs)

def es_last_index():
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    
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
    
if __name__ == '__main__':    # 프로그램의 시작점일 때만 아래 코드 실행
    # searchById("TM7RD2cBZ4ljROrfRJ0b")
    es_update(list())
    # 특정필드 지우기
    # http://kyungseop.tistory.com/6 