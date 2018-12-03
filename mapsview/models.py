from django.db import models
from django.utils import timezone
import elasticsearch
import urllib
import json as simplejson

googleGeocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?'

def list(queryString, field):
    es_client = elasticsearch.Elasticsearch("localhost:9200")
    # print(field)
    if queryString is None or queryString is "":
        print("queryString is None")
        data = es_client.search(index = 'matzip',
                                doc_type = 'doc',
                                body = {
                                    'size': 100,
                                })
        es_client.update
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

    return get_coordinates(matList)
    
def get_coordinates(matList, from_sensor=False):
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