from django.test import TestCase
from django.db import models
from django.utils import timezone
import elasticsearch
from elasticsearch import helpers, RequestsHttpConnection
import urllib
import json as simplejson
import csv
from datetime import datetime
from requests_aws4auth import AWS4Auth
import boto3

googleGeocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?'
es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")

def list():
    # print(field)
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    data = es_client.search(index = 'matzip',
                            doc_type = 'doc',
                            body = {
                                'size': 100,
                                'sort': {'ID': 'asc'}
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
        addr = one['_source']['RN_ADDR']
        latlng = get_coordinates(addr)
        up_data = es_client.update(
            index = 'matzip',
            doc_type = 'doc',
            id = int(one['_source']['ID']),
            body = {
                'doc': {
                    'ID': int(one['_source']['ID']), 
                    'NAME': one['_source']['NAME'], 
                    'RN_ADDR': addr, 
                    'LB_ADDR': one['_source']['LB_ADDR'], 
                    'DETAIL_ADDR': one['_source']['DETAIL_ADDR'],
                    'TEL': one['_source']['TEL'], 
                    'OFF_DAY': one['_source']['OFF_DAY'], 
                    'PARKING': one['_source']['PARKING'],
                    'DESC': one['_source']['DESC'], 
                    'TYPE': one['_source']['TYPE'], 
                    'BREAK_FROM': one['_source']['BREAK_FROM'], 
                    'BREAK_TO': one['_source']['BREAK_TO'], 
                    'SALES_FROM': one['_source']['SALES_FROM'], 
                    'SALES_TO': one['_source']['SALES_TO'], 
                    'SUB_TYPE': one['_source']['SUB_TYPE'], 
                    'TRY': one['_source']['TRY'],
                    'TAG': one['_source']['TAG'],
                    'lat': latlng[0],
                    'lng': latlng[1]
                }
            }
        )

        print(up_data)

def es_insert():
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    addr = '서울 강동구 구천면로 221'
    latLng = get_coordinates(addr)
    source = {
                'ID': 56, 
                'NAME': '광주횟집', 
                'RN_ADDR': addr, 
                'LB_ADDR': '천호동 402-8', 
                'DETAIL_ADDR': None, 
                'TEL': '02-476-5007', 
                'OFF_DAY': None, 
                'SALES_FROM': None,
                'SALES_TO': None,
                'BREAK_FROM': None,
                'BREAK_TO': None,
                'PARKING': 'TRUE',
                'TYPE': 'M',
                'SUB_TYPE': 'K',
                'DESC': '이렇게 두꺼운 회는 처음봄',
                'TRY': 'TRUE',
                'TAG': ['회', '두꺼움'],
                'lat': latLng[0],
                'lng': latLng[1]
            }
    
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

def elastic_to_csv() :
    es = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    data = es.search(
            index="matzip",
            body={
                "query" : {
                    "match_all" : {
                    }
                },
                'size': 100,
                'sort': {'ID': 'asc'}
            }
        )

    csv_columns = [
        "ID", "NAME",
        "RN_ADDR", "LB_ADDR","DETAIL_ADDR",
        "TEL","OFF_DAY",
        "SALES_FROM","SALES_TO",
        "BREAK_FROM","BREAK_TO",
        "PARKING", "DESC", 
        "TYPE", "SUB_TYPE", 
        "TRY", "TAG",
        'lng', 'lat',
        'path', '@version', 'message', 'host', '@timestamp'
    ]
    
    csv_file = '/Users/gksml/Programing/git/BebeeMaps/mapsview/static/csv/log_matzip_'+str(datetime.today().strftime("%Y%m%d_%H%M%S"))+'.csv'

    with open(csv_file, 'w', newline='', encoding='UTF8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for document in [x['_source'] for x in data['hits']['hits']]:
            writer.writerow(document)

def csv_to_elasticsearch() :
    host = 'https://search-bebeemaps-jnd234b6kog3wdbof6oinn6ifi.us-east-2.es.amazonaws.com' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-east-2' # e.g. us-west-1
    service = 'es'
    auth = AWS4Auth('AKIAIG4PVNWTTO4FD7YQ', 'Sf5IVpOTz6+yiRnlxF5dci7QAi8NTP0dgdTLOK8q', 'us-east-2', 'es')
    credentials = boto3.Session().get_credentials()
    # awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)
    
    es = elasticsearch.Elasticsearch(
        host,
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    with open('/Users/gksml/Programing/git/BebeeMaps/mapsview/static/csv/matzip_db.csv', 'r', encoding='UTF8') as f:
        reader = csv.DictReader(f)
        helpers.bulk(es, reader, index='matzip', doc_type='doc')

def es_delete(id):
    es_client = elasticsearch.Elasticsearch("http://127.0.0.1:9200")
    
    # result = es_client.delete(index = 'matzip', doc_type = 'doc', id=id, ignore=[400, 404])
    result = {}
    try:
        result = es_client.delete(index = 'matzip', doc_type = 'doc', id=id)
    except Exception as e:
        result['result'] = e.args[1]

    return result['result']

if __name__ == '__main__':    # 프로그램의 시작점일 때만 아래 코드 실행
    # print(list())
    
    # 데이터 추가 
    # es_insert()
    
    # json파일 엘라스틱서치에 밀어 넣기
    # bulk_to_json_file()
    
    # 데이터 완전 새로 올린 후 위경도 및 태그 프로퍼티 추가
    # es_update(list())

    # elastic_to_csv()
    # print(es_delete(65))
    csv_to_elasticsearch()
    