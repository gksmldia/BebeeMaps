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
            id = int(one['_source']['ID']),
            body = {
                'doc': {
                    'ID': int(one['_source']['ID']), 
                    'NAME': one['_source']['NAME'], 
                    'RN_ADDR': one['_source']['RN_ADDR'], 
                    'LB_ADDR': one['_source']['LB_ADDR'], 
                    'DETAIL_ADDR': one['_source']['DETAIL_ADDR'], 
                    'TEL': one['_source']['TEL'], 
                    'OFF_DAY': ['SUN', 'MON(2,4)'], 
                    'PARKING': one['_source']['PARKING'],
                    'DESC': one['_source']['DESC'], 
                    'BREAK': one['_source']['BREAK'], 
                    'TYPE': one['_source']['TYPE'], 
                    'FROM-TO': one['_source']['FROM-TO'], 
                    'SUB_TYPE': one['_source']['SUB_TYPE'], 
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
    addr = '서울 양천구 오목로 320-2'
    latLng = get_coordinates(addr)
    source = {
                'ID': es_last_index()+1, 
                'NAME': '창평가마솥순대국', 
                'RN_ADDR': addr, 
                'LB_ADDR': '목동 405-148', 
                'DETAIL_ADDR': None, 
                'TEL': '02-2643-3100', 
                'OFF_DAY': ['holiday'], 
                'FROM-TO': '06:00 ~ 23:00',
                'BREAK': None,
                'PARKING': 'TRUE',
                'TYPE': 'M',
                'SUB_TYPE': 'K',
                'DESC': '목동 SBS 피디님 추천',
                'TRY': 'FALSE',
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

def bulk_to_json_file() :
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    
    MyFile= open("C:\\Users\\gksml\\Programing\\git\BebeeMaps\\mapsview\\static\\json\sub_type_db.json", 'r', encoding='UTF8').read()
    ClearData = MyFile.splitlines(True)
    i=0
    json_str=""
    docs ={}
    for line in ClearData:
        line = ''.join(line.split())
        if line != "},":
            json_str = json_str+line
        else:
            docs[i]=json_str+"}"
            json_str=""
            print(docs[i])
            es_client.index(index='subtype', doc_type='doc', id=i+1, body=docs[i])
            i=i+1

if __name__ == '__main__':    # 프로그램의 시작점일 때만 아래 코드 실행
    # print(list())
    
    # 데이터 추가 
    # es_insert()
    
    # json파일 엘라스틱서치에 밀어 넣기
    bulk_to_json_file()
    
    # 데이터 완전 새로 올린 후 위경도 및 태그 프로퍼티 추가
    # es_update(get_coordinates_list(list()))
    