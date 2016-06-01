
import requests
import urllib
import json
from django.db import connections
import properties
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from collections import namedtuple


def funcPullImage(url, name, tag):
    r = requests.post(url+'/images/create?fromImage='+urllib.quote_plus(name)+'&tag='+urllib.quote_plus(tag))
    if r.status_code == 200:
        return {'status': 'success', 'content': 'Image pulled successfully.'}
    else:
        return {'status': 'failed', 'content': 'Pulling the image failed with the following error: '+r.content}

def funcCreateContainer(url, name, data):
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url + '/containers/create?name='+name, data=json.dumps(data), headers=headers)
    if r.status_code == 201:
        d = json.loads(r.content)
        return {'status': 'success', 'content': 'Container deployed successfully with ID: ' + d["Id"], 'id' : d["Id"] }
    elif r.status_code == 404:
        return {'status': 'failed', 'content': 'Deploying the container failed with the following error: '+r.content}
    elif r.status_code == 406:
        return {'status': 'failed', 'content': 'Deploying the container failed with the following error: '+r.content}
    else:
        return {'status': 'failed', 'content': 'Deploying the container failed with the following error: '+r.content}

def funcAddPortsToDB(container_id, port_bindings):
    cursor = connections['default'].cursor()
    sql = "INSERT INTO containers(container_id, port_bindings) " + "VALUES ('" + container_id + "','" + port_bindings + "')"
    cursor.execute(sql)
    rowid = cursor.lastrowid
    print rowid

def funcStartContainer(url, id):
    headers = {'Content-Type': 'application/json'}

    cursor = connections['default'].cursor()
    response = []
    sql = "SELECT * FROM containers where container_id='"+id+"'"
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    print results
    exposedPortsObj = {}
    for row in results:
        portBindings = row.port_bindings
        print portBindings
        portBindings =portBindings.split(",")
        for portBinding in portBindings:
            portBinding= portBinding.split(":")
            print portBinding
            if len(portBinding) == 2:
                if portBinding[0] == '' or portBinding[1] == '':
                    return JsonResponse({"status": "failure", "content": "Port binding in wrong format. Correct format: HOST_PORT:CONTAINER_PORT"})
                else:
                    print "here"
                    index = portBinding[1]+'/tcp'
                    exposedPortsObj[index]=[{"HostPort": portBinding[0]}]
    data={
          "PortBindings": exposedPortsObj
        }
    print data
    r = requests.post(url+'/containers/'+id+'/attach?logs=1&stream=0&stdout=1')

    r = requests.post(url + '/containers/'+id+'/start', data=json.dumps(data), headers=headers)
    if r.status_code == 204:
        return {'status': 'success', 'content': 'Container Started successfully'}
    elif r.status_code == 304:
        return {'status': 'success', 'content': 'Container already in started state'}
    elif r.status_code == 404:
        return {'status': 'failed', 'content': 'Container not found'}
    else:
        return {'status': 'failed', 'content': 'Starting the container failed with the following error: '+r.content}

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def funcAttachContainer(url, id):
    r = requests.post(url+'/containers/'+id+'/attach?logs=1&stream=0&stdout=1')
    print r.content
    if r.status_code == 101:
        print 'here'
        print r.content
        return {'status': 'success', 'content': r.content}
    elif r.status_code == 200:
        print r.content
        return {'status': 'success', 'content': r.content}
    elif r.status_code == 404:
        return {'status': 'failed', 'content': 'Attaching the container failed with the following error: '+r.content}
    else:
        return {'status': 'failed', 'content': 'Attaching the container failed with the following error: '+r.content}


def funcKillContainer(url, id):
    r = requests.post(url + '/containers/' + id + '/kill')
    print r.status_code
    if r.status_code == 204:
        return {'status': 'success', 'content': 'Container Killed successfully'}
    elif r.status_code == 404:
        return {'status': 'failed', 'content': 'Killing the container failed with the following error: ' + r.content}
    else:
        return {'status': 'failed', 'content': 'Killing the container failed with the following error: ' + r.content}

def funcDeleteContainer(url, id):
    r = requests.delete(url + '/containers/' + id)
    print r.status_code
    if r.status_code == 204:
        return {'status': 'success', 'content': 'Container deleted successfully'}
    elif r.status_code == 404:
        return {'status': 'failed', 'content': 'Deleting the container failed with the following error: ' + r.content}
    elif r.status_code == 406:
        return {'status': 'failed', 'content': 'Deleting the container failed with the following error: ' + r.content}
    else:
        return {'status': 'failed', 'content': 'Deleting the container failed with the following error: ' + r.content}

def funcCreateAuthToken(ip, user, tenant, password):
    # data = {"auth": {"tenantName": tenant, "passwordCredentials": {"username": user, "password": password}}}
    # headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    # data_json = json.dumps(data)
    # response = requests.post('http://' + ip + ':35357/v2.0/tokens', data=data_json, headers=headers)
    #
    # # Print(response.text)
    # response = response.json()
    #auth_token = response["access"]["token"]["id"]

    auth_token = properties.TOKEN
    return auth_token

def funcCreateAuthTokenAndGetEP(ip, user, tenant, password,servicename):
    # data = {"auth": {"tenantName": tenant, "passwordCredentials": {"username": user, "password": password}}}
    # headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    # data_json = json.dumps(data)
    # response = requests.post('http://' + ip + ':35357/v2.0/tokens', data=data_json, headers=headers)
    #
    # # Print(response.text)
    # response = response.json()
    # auth_token = response["access"]["token"]["id"]
    # tenantId = response["access"]["token"]["tenant"]["id"]
    # service_catalog = response["access"]["serviceCatalog"]
    auth_token=properties.TOKEN
    tenantId=properties.TENANT
    endpoint = properties.ENDPOINT

    return {"auth_token": auth_token, "endpoint": endpoint, "tenantId":tenantId}

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


def addNode(ip, port, name):
    cursor = connections['default'].cursor()
    print "inside addNode"
    sql = "INSERT INTO nodes(ip, port, name) " + "VALUES ('" + ip + "','" + port + "','" + name + "')"
    cursor.execute(sql)
    rowid = cursor.lastrowid
    print rowid

