#! /usr/bin/env python2.7

import requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import random
from django.contrib import messages
import urllib
import json
import socket;
import generalfunctions
from collections import namedtuple
from django.db import connections
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import properties
from murano_connect import utils as m_utils
from django.conf import settings


from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)


class ManageView(TemplateView):
    template_name = 'Manage.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)

class BuildView(TemplateView):
    template_name = 'Build.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)

class DeployView(TemplateView):
    template_name = 'Deploy.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)

class SwarmView(TemplateView):
    template_name = 'Swarm.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)

class MigrateView(TemplateView):
    template_name = 'Migrate.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)

class ImagesView(TemplateView):
    template_name = 'Images.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)

class VNFCatalogView(TemplateView):
    template_name = 'VNFCatalog.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)

class VNFManagerView(TemplateView):
    template_name = 'VNFManager.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)


class DockerManageView(TemplateView):
    template_name = 'DockerManage.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)


def GetImages(request):
    docker_server_url = request.session['currentip']
    resp = requests.get(docker_server_url+'/images/json')
    item = resp.json()
    return JsonResponse({'status': 'success', 'content': item})

def GetContainers(request):
    docker_server_url = request.session['currentip']
    resp = requests.get(docker_server_url+'/containers/json?all=1')
    item = resp.json()
    return JsonResponse({'status': 'success', 'content': item})

def UploadImage(request):
    path = handle_uploaded_file(request.FILES['dockerFile'])
    name = request.POST.get('name')
    tag = request.POST.get('tag')
    docker_server_url = request.session['currentip']
    if name=='':
        messages.error(request, 'Please enter a name')
        return HttpResponseRedirect('/Build/')

    name = name+':'+tag

    headers = {'Content-Type': 'application/tar'}

    data = open(path, 'rb').read()
    r = requests.post(docker_server_url+'/build?t='+urllib.quote_plus(name), data=data, headers=headers)
    print r.content
    if r.status_code == 200:
        messages.error(request, 'Image built successfully.')
        return HttpResponseRedirect('/Build/')

    else:
        messages.error(request, 'Building the image failed with the following error: '+r.content)
        return HttpResponseRedirect('/Build/')

def PullImage(request):
    name = request.GET.get('name')
    tag = request.GET.get('tag')
    docker_server_url = request.session['currentip']

    if name=='':
        messages.error(request, 'Please enter a name')
        return HttpResponseRedirect('/Build/')

    if tag=='':
        tag='latest'

    r = generalfunctions.funcPullImage(docker_server_url, name, tag)

    messages.error(request, r["content"])
    return HttpResponseRedirect('/Build/')



def DeleteImage(request):
    name = request.GET.get('name')
    docker_server_url = request.session['currentip']

    r = requests.delete(docker_server_url+'/images/'+name +'?force=true')
    print r.status_code
    print r.content
    if r.status_code == 200:
        return JsonResponse({'status': 'success', 'content': 'Image deleted successfully.'})
    elif r.status_code == 404:
        return JsonResponse({'status': 'failed', 'content': 'Deleting the image failed with the following error: '+r.content})
    elif r.status_code == 409:
        return JsonResponse({'status': 'failed', 'content': 'Deleting the image failed with the following error: '+r.content})
    else:
        return JsonResponse({'status': 'failed', 'content': 'Deleting the image failed with the following error: '+r.content})

def KillContainer(request):
    id = request.GET.get('id')
    docker_server_url = request.session['currentip']
    r = generalfunctions.funcKillContainer(docker_server_url, id)

    return JsonResponse(r)

def DeleteContainer(request):
    id = request.GET.get('id')
    docker_server_url = request.session['currentip']

    r = generalfunctions.funcDeleteContainer(docker_server_url, id)
    return JsonResponse(r)


def RunContainer(request):
    name = request.GET.get('name')
    image = request.GET.get('image')
    commands = request.GET.get('commands')
    environments = request.GET.get('environments')
    volumes = request.GET.get('volumes')
    #tcpports = request.GET.get('tcpports')
    docker_server_url = request.session['currentip']

    envs=[]
    last = len(environments.split(',')) - 1
    i=0

    if commands != "":
        commands = commands.split(",")
    else:
        commands = None

    if environments!="":
        for env in environments.split(','):
            envs.append(env)
    else:
        envs = None

    if volumes!="":
        volumes = volumes.split(",")
    else:
        volumes=None

    jsonport=[]
    # if tcpports!="":
    #     ports=tcpports.split(",")
    #     for port in ports:
    #         port=port.split(":")
    #         portarray = {"PrivatePort": int(port[1]), "PublicPort": int(port[0]), "Type": "tcp"}
    #         jsonport.append(portarray)
    # else:
    #     tcpports=[]
    #
    # print jsonport
    vols=[]
    #for volume in volumes:
    #    volume = volume.split(':')
    #    vols.append(volume[0]+":"+volume[1])

    #print vols

    headers = {'Content-Type': 'application/json'}
    data={
          "AttachStdin": False,
          "AttachStdout": True,
          "AttachStderr": True,
          "Tty": False,
          "OpenStdin": False,
          "StdinOnce": False,
          "Cmd": commands,
          "Env": envs,
          "Image": image,
          "HostConfig": {"Binds": volumes},
          "Ports": jsonport
        }
    #,"HostConfig":{"Binds": volumes}
    print json.dumps(data)

    r = generalfunctions.funcCreateContainer(docker_server_url, name, data)

    return JsonResponse(r)

    #return JsonResponse({"status": "success"})


def StartContainer(request):
    id = request.GET.get('id')
    docker_server_url = request.session['currentip']

    r = generalfunctions.funcStartContainer(docker_server_url, id)
    return JsonResponse(r)

def AttachContainer(request):
    id = request.GET.get('id')
    docker_server_url = request.session['currentip']

    r = generalfunctions.funcAttachContainer(docker_server_url, id)
    return JsonResponse(r)

@csrf_exempt
def HandleSwarm(request):
    response = '{"master":[{"ip": "153.92.34.6", "port":"2375", "name":"master1"}],"node":[{"ip": "153.92.35.46", "port":"2375", "name":"node1"}]}'
    print 'here'
    print 'Raw Data: "%s"' % request.body
    jsonrequest = json.loads(request.body)
    print jsonrequest
    token = ''
    swarmmaster=0

    #check master connectivity
    for master in jsonrequest["master"]:
        print master["ip"]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((master["ip"], int(master["port"])))
        if result == 0:
            print "Port is open"
        else:
            print "Port is not open"
            return JsonResponse({'status': 'failed', 'content': 'Please check the IP and port('+master["ip"] + ":" + master["port"]+')'})


    #check nodes connectivity
    for node in jsonrequest["node"]:
        print node["ip"]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((node["ip"], int(node["port"])))
        if result == 0:
            print "Port is open"
        else:
            print "Port is not open"
            return JsonResponse({'status': 'failed', 'content': 'Please check the IP and port('+node["ip"] + ":" + node["port"]+')'})

    #create master node
    for master in jsonrequest["master"]:
        ip = master["ip"]
        port = master["port"]
        name = master["name"]
        url = 'http://'+master["ip"] + ':' + master["port"]
        resp = generalfunctions.funcPullImage(url, 'swarm', '1.1.3')
        if resp["status"] == 'success':
            data={
              "AttachStdin": False,
              "AttachStdout": True,
              "AttachStderr": True,
              "Tty": False,
              "OpenStdin": False,
              "StdinOnce": False,
              "Cmd": ["create"],
              "Image": "swarm:1.1.3"
            }
            masterContainer = generalfunctions.funcCreateContainer(url, name, data)
            if masterContainer["status"] == 'success':
                print 'container created successfully'
                masterContainerId = masterContainer["id"]
                print 'master id:' + masterContainerId
                startCont = generalfunctions.funcStartContainer(url, masterContainerId)
                if startCont["status"] == 'success':
                    print 'container started successfully'
                    attachCont = generalfunctions.funcAttachContainer(url, masterContainerId)
                    print attachCont["content"]
                    token = attachCont["content"][8:]
                    print token
                    #insert the master into database
                    cursor = connections['default'].cursor()
                    sql="INSERT into swarm(name, master, master_port) VALUES('"+name+"','"+ip+"','"+port+"')"
                    cursor.execute(sql)
                    swarmmaster=cursor.lastrowid

                    #set master to Y in nodes table
                    sql="UPDATE nodes set ismaster='Y', swarmmaster=0, swarmcontainerid='"+masterContainerId+"',swarmnodename='"+name+"' where ip='"+ip+"' and port='"+port+"'"
                    cursor.execute(sql)
                else:
                    print 'starting the container failed'
            else:
                print 'creating the container failed'
        else:
            print 'pulling the image failed'




    #create slave nodes
    for node in jsonrequest["node"]:
        ip = node["ip"]
        port = node["port"]
        name = node["name"]
        url = 'http://'+ ip + ':' + port
        resp = generalfunctions.funcPullImage(url, 'swarm', '1.1.3')

        if resp["status"] == 'success':
            data={
              "AttachStdin": False,
              "AttachStdout": True,
              "AttachStderr": True,
              "Tty": False,
              "OpenStdin": False,
              "StdinOnce": False,
              "Cmd": ["join", "--addr="+ip+":"+port, "token://"+token],
              "Image": "swarm:1.1.3"
            }
            nodeContainer = generalfunctions.funcCreateContainer(url, name, data)
            if nodeContainer["status"] == 'success':
                nodeContainerId = nodeContainer["id"]
                startCont = generalfunctions.funcStartContainer(url, nodeContainerId)
                if startCont["status"] == 'success':
                    print "starting the node success" + ip
                    #set master to Y in nodes table
                    sql="UPDATE nodes set ismaster='N',swarmmaster="+str(swarmmaster)+",swarmnodename='"+name+"',swarmcontainerid='"+nodeContainerId+"' where ip='"+ip+"' and port='"+port+"'"
                    cursor.execute(sql)
                else:
                    print 'starting the container failed' + ip
                    return JsonResponse({"status": "failed"})
            else:
                print 'creating the container failed' + ip
                return JsonResponse({"status": "failed"})
        else:
            print 'pulling the image failed' + ip
            return JsonResponse({"status": "failed"})


    #create swarm master manager
    for master in jsonrequest["master"]:
        ip = master["ip"]
        port = master["port"]
        name = master["name"] + 'manage'
        url = 'http://'+master["ip"] + ':' + master["port"]

        resp = generalfunctions.funcPullImage(url, 'swarm', '1.1.3')
        if resp["status"] == 'success':
            data={
              "PortBindings": { "2375/tcp": [{ "HostPort": "5001" }] },
              "AttachStdin": False,
              "AttachStdout": True,
              "AttachStderr": True,
              "Tty": False,
              "OpenStdin": False,
              "StdinOnce": False,
              "Cmd": ["manage", "token://"+token],
              "Image": "swarm:1.1.3"
            }
            masterManagerContainer = generalfunctions.funcCreateContainer(url, name, data)
            if masterManagerContainer["status"] == 'success':
                masterManagerContainerId = masterManagerContainer["id"]
                startCont = generalfunctions.funcStartContainer(url, masterManagerContainerId)
                if startCont["status"] == 'success':
                    print 'master manager started'
                    sql="INSERT into nodes(ip, port, name, ismaster, swarmmaster, swarmnodename, swarmcontainerid) values('"+ip+"','5001', '"+name+"', 'N', 0, '"+name+"', '"+masterManagerContainerId+"')"
                    cursor.execute(sql)
                else:
                    print 'starting the container failed'
                    return JsonResponse({"status": "failed"})
            else:
                print 'creating the container failed'
                return JsonResponse({"status": "failed"})
        else:
            print 'pulling the image failed' + ip
            return JsonResponse({"status": "failed"})



    return JsonResponse({"status": "success", "content": "Swarm created successfully"})

def handle_uploaded_file(f):
    print f.name
    filename = f.name +`random.random()` + '.tar.gz'
    path = '/home/unameit/docker/' + filename
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path

def handle_uploaded_file_image(f):
    print f.name
    path = '/home/unameit/docker/' + f.name
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path


# def upload(request):
#     ip = '31.220.64.130'
#     data = {"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "d7a078d32efd17d6c1f6"}}}
#     headers = {'Content-type': 'application/json','Accept':'application/json'}
#     data_json = json.dumps(data)
#     response = requests.post('http://'+ ip +':35357/v2.0/tokens', data=data_json, headers=headers)
#     print(response.text)
#     response = response.json()
#     auth_token = response["access"]["token"]["id"]
#     print auth_token
#
#     headers = {'Content-Type': 'application/octet-stream'}
#     headers = {'X-Auth-Token': auth_token}
#     data = open("C:\\a.yaml", 'rb').read()
#     r = requests.put("http://"+ ip +":8080/v1/AUTH_15016075c6464cd3a1a3852b615f2b65/test/a.yaml", data=data, headers=headers)
#     print r.status_code
#     print r.content

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def GetNodes(request):
    cursor = connections['default'].cursor()
    response = []
    sql = "SELECT * FROM nodes"
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)

    for row in results:
        if 'currentip' in request.session:
            if request.session['currentip'] == 'http://'+row.ip+':'+row.port:
                add = {'ip':row.ip, 'name':row.name, 'port':row.port, 'id':row.Id, 'selected':'true'}
            else:
                add = {'ip':row.ip, 'name':row.name, 'port':row.port, 'id':row.Id}
        else:
            request.session['currentip'] = 'http://'+row.ip+':'+row.port
            add = {'ip':row.ip, 'name':row.name, 'port':row.port, 'id':row.Id, 'selected':'true'}

        response.append(add)
    print request.session['currentip']
    cursor.close()
    return JsonResponse(response, safe=False)

def ChangeNode(request):
    id = request.GET.get('id')

    cursor = connections['default'].cursor()
    sql = "SELECT * FROM nodes where Id="+id
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        request.session['currentip'] = 'http://'+row.ip+':'+row.port
    cursor.close()
    return JsonResponse({"status": "success"})

def EditNode(request):
    id = request.GET.get('id')
    ip = request.GET.get('ip')
    port = request.GET.get('port')
    name = request.GET.get('name')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, int(port)))
    if result == 0:
        print "Port is open"
    else:
        print "Port is not open"
        return JsonResponse({'status': 'failed', 'content': 'Please check the IP and port('+ip + ":" + port +')'})

    cursor = connections['default'].cursor()

    sql='Update nodes set ip="'+ip+'", port="'+port+'", name="'+name+'" where Id=' + id
    cursor.execute(sql)
    cursor.close()
    return JsonResponse({'status': 'success', 'id': id, 'content': 'Node details updated successfully'})

def DeleteNode(request):
    id = request.GET.get('id')

    cursor = connections['default'].cursor()

    sql = "DELETE FROM nodes where Id="+id
    cursor.execute(sql)
    cursor.close()
    return JsonResponse({'status': 'success', 'id': id, 'content': 'Node deleted successfully.'})

def AddNode(request):
    ip = request.GET.get('ip')
    port = request.GET.get('port')
    name = request.GET.get('name')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, int(port)))
    if result == 0:
        print "Port is open"
    else:
        print "Port is not open"
        return JsonResponse({'status': 'failed', 'content': 'Please check the IP and port('+ip + ":" + port +')'})

    try:
        cursor = connections['default'].cursor()

        sql = "INSERT INTO nodes(ip, port, name) " + "VALUES ('" + ip + "','" + port + "','" + name + "')"
        cursor.execute(sql)
        rowid = cursor.lastrowid
        return JsonResponse({'status': 'success', 'id': rowid, 'content': 'Node added successfully'})
    except IntegrityError as e:
        print '**************************************************'
        return JsonResponse({'status': 'failed', 'content': 'Node('+ip+') and port('+port+') already configured'})
    finally:
        cursor.close()


def GetSwarms(request):
    cursor = connections['default'].cursor()
    sql = "SELECT * FROM swarm"

    masters = []

    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        id = row.Id
        ip = row.master
        port = row.master_port
        name = row.name
        sql = "SELECT * FROM nodes where swarmmaster="+str(id)
        cursor.execute(sql)
        nodeResults = namedtuplefetchall(cursor)
        nodes = []
        for rowNode in nodeResults:
            nodeid = rowNode.Id
            nodeip = rowNode.ip
            nodeport = rowNode.port
            nodename = rowNode.name
            node = {'ip':nodeip, 'name':nodename, 'port':nodeport, 'id':str(nodeid)}
            nodes.append(node)

        master = {'id': str(id), 'ip': ip, 'port': port, 'name': name, 'nodes': nodes}
        masters.append(master)

    cursor.close()
    return JsonResponse({"status": "success", "content": masters})


def RemoveSwarmNode(request):
    ip = request.GET.get('ip')
    port = request.GET.get('port')
    nodeid = request.GET.get('nodeid')
    cursor = connections['default'].cursor()


    sql = "SELECT * FROM nodes where Id=" + str(nodeid)
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        nodeip = row.ip
        nodeport = row.port
        containername = row.swarmnodename
        containerid = row.swarmcontainerid
        docker_server_url = 'http://'+row.ip+':'+port

        r = generalfunctions.funcKillContainer(docker_server_url, containerid)
        r = generalfunctions.funcDeleteContainer(docker_server_url, containerid)

        sql = "UPDATE nodes set ismaster='N',swarmmaster=0,swarmnodename='none',swarmcontainerid='none' where ip='" + nodeip + "' and port='" + nodeport + "'"
        cursor.execute(sql)

    cursor.close()
    return JsonResponse({"status": "success", "content": "Node removed from Swarm successfully"})

def AddSwarmNode(request):
    swarmid = request.GET.get('id')
    ip = request.GET.get('ip')
    port = request.GET.get('port')
    name = request.GET.get('name')

    cursor = connections['default'].cursor()
    sql = "SELECT * FROM swarm where Id=" + swarmid
    print sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)

    for row in results:
        id = row.Id
        masterip = row.master
        masterport = row.master_port
        name = row.name
        token = ''
        url = 'http://' + masterip + ':' + masterport
        print sql
        sql = "SELECT * FROM nodes where ip='" + str(masterip)+"' and port='"+str(masterport)+"'"
        print sql
        cursor.execute(sql)
        masterResults = namedtuplefetchall(cursor)
        for rowmaster in masterResults:
            containerid = rowmaster.swarmcontainerid
            attachCont = generalfunctions.funcAttachContainer(url, containerid)
            print attachCont["content"]
            token = attachCont["content"][8:]
            print token

    url = 'http://' + ip + ':' + port
    resp = generalfunctions.funcPullImage(url, 'swarm', '1.1.3')

    if resp["status"] == 'success':
        data = {
            "AttachStdin": False,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": False,
            "OpenStdin": False,
            "StdinOnce": False,
            "Cmd": ["join", "--addr=" + ip + ":" + port, "token://" + token],
            "Image": "swarm:1.1.3"
        }
        nodeContainer = generalfunctions.funcCreateContainer(url, name, data)
        if nodeContainer["status"] == 'success':
            nodeContainerId = nodeContainer["id"]
            startCont = generalfunctions.funcStartContainer(url, nodeContainerId)
            if startCont["status"] == 'success':
                print "starting the node success" + ip
                # set master to Y in nodes table
                sql = "UPDATE nodes set ismaster='N',swarmmaster=" + str(id) + ",swarmnodename='" + name + "',swarmcontainerid='" + nodeContainerId + "' where ip='" + ip + "' and port='" + port + "'"
                cursor.execute(sql)
            else:
                print 'starting the container failed' + ip
                return JsonResponse({"status": "failed"})
        else:
            print 'creating the container failed' + ip
            return JsonResponse({"status": "failed"})
    else:
        print 'pulling the image failed' + ip
        return JsonResponse({"status": "failed"})
    return JsonResponse({"status": "success", "content": "Node added to Swarm successfully"})

def DeleteSwarm(request):
    swarmid = request.GET.get('id')

    cursor = connections['default'].cursor()
    sql = "SELECT * FROM swarm where Id="+swarmid

    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        id = row.Id
        ip = row.master
        port = row.master_port
        name = row.name
        #remove all swarm nodes
        sql = "SELECT * FROM nodes where swarmmaster=" + str(id)
        cursor.execute(sql)
        nodeResults = namedtuplefetchall(cursor)
        nodes = []
        for rowNode in nodeResults:
            nodeid = rowNode.Id
            nodeip = rowNode.ip
            nodeport = rowNode.port
            nodename = rowNode.name
            containerid = rowNode.swarmcontainerid

            docker_server_url = 'http://' + nodeip + ':' + nodeport

            r = generalfunctions.funcKillContainer(docker_server_url, containerid)
            r = generalfunctions.funcDeleteContainer(docker_server_url, containerid)
            print "deleted the node container"
            sql = "UPDATE nodes set ismaster='N',swarmmaster=0,swarmnodename='none',swarmcontainerid='none' where ip='" + nodeip + "' and port='" + nodeport + "'"
            cursor.execute(sql)
            print "updated the db for node container deletion"

        #remove swarm master manager
        sql = "SELECT * FROM nodes where swarmnodename='" + name+"manage'"
        cursor.execute(sql)
        manageResults = namedtuplefetchall(cursor)
        for rowManage in manageResults:
            manageip = rowManage.ip
            manageport = rowManage.port
            containerid = rowManage.swarmcontainerid

            docker_server_url = 'http://' + ip + ':' + port

            r = generalfunctions.funcKillContainer(docker_server_url, containerid)
            r = generalfunctions.funcDeleteContainer(docker_server_url, containerid)
            print "deleted the master manage container"
            sql = "DELETE FROM nodes where ip='" + manageip + "' and port='" + manageport + "'"
            cursor.execute(sql)
            print "updated the db for master manage container deletion"

        sql = "SELECT * FROM nodes where ip='" + ip + "' and port='"+port+"'"
        cursor.execute(sql)
        masterResults = namedtuplefetchall(cursor)
        for master in masterResults:
            containerid = master.swarmcontainerid

            docker_server_url = 'http://' + ip + ':' + port

            r = generalfunctions.funcKillContainer(docker_server_url, containerid)
            r = generalfunctions.funcDeleteContainer(docker_server_url, containerid)
            print "deleted the master container"
            sql = "UPDATE nodes set ismaster='N',swarmmaster=0,swarmnodename='none',swarmcontainerid='none' where ip='" + ip + "' and port='" + port + "'"
            cursor.execute(sql)
            print "updated the master container in db"

        sql = "DELETE FROM swarm where Id=" + str(id)
        cursor.execute(sql)
        print "updated the swarm table for master container deletion"
        return JsonResponse({"status": "success", "content": "Swarm deleted successfully"})


def listInstances(request):
    print "Inside the listInstances API"

    env_ip = request.GET.get('env_ip')
    print env_ip
    cursor = connections['default'].cursor()
    sql = "SELECT * FROM vnf_env where env_ip='" + str(env_ip)+"'"
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        env_ip = str(row.env_ip)
        user = str(row.user)
        tenant = str(row.tenant)
        password = str(row.password)

    #ip = properties.openstack_IP
    #user = properties.openstack_user
    #tenant = properties.openstack_tenant
    #password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(env_ip, user, tenant, password)
    print auth_token

    # List all Tenants
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
    response = requests.get('http://'+ env_ip +':35357/v2.0/tenants' , headers=headers)

    tenant_response = response.json()
    tenant_details = tenant_response["tenants"]

    print str(tenant_details)
    tenant_id = ''
    for tenant in tenant_details:
        if tenant["name"] == 'demo':
            tenant_id = tenant["id"]


    # List all stack

    #headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
    #response = requests.get('http://'+ ip +':8004/v1/' + tenant_id + '/stacks' , headers=headers)

    #stack_response = response.json()

    #print stack_response

    # List all servers

    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
    response = requests.get('http://'+ env_ip +':8774/v2/' + tenant_id + '/servers' , headers=headers)

    server_response = response.json()
    print server_response
    return JsonResponse(server_response)


def listHypervisors(request):
    print "Inside the listHypervisors API"
    env_ip = request.GET.get('env_ip')
    print env_ip
    cursor = connections['default'].cursor()
    sql = "SELECT * FROM vnf_env where env_ip='" + str(env_ip) + "'"
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        env_ip = str(row.env_ip)
        user = str(row.user)
        tenant = str(row.tenant)
        password = str(row.password)

    #ip = properties.openstack_IP
    #user = properties.openstack_user
    #tenant = properties.openstack_tenant
    #password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(env_ip, user, tenant, password)
    print auth_token

    # List all Tenants
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get('http://' + env_ip + ':35357/v2.0/tenants', headers=headers)

    tenant_response = response.json()
    tenant_details = tenant_response["tenants"]

    tenant_id = ''
    for tenant in tenant_details:
        if tenant["name"] == 'demo':
            tenant_id = tenant["id"]

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get('http://' + env_ip + ':8774/v2/' + tenant_id + '/os-hypervisors', headers=headers)

    hyp_response = response.json()

    return JsonResponse(hyp_response)


@api_view(['GET'])
def migrateVM(request):
    print "Inside the migrate VM API"

    env_ip = request.GET.get('env_ip')
    print env_ip
    cursor = connections['default'].cursor()
    sql = "SELECT * FROM vnf_env where env_ip='" + str(env_ip) + "'"
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        env_ip = str(row.env_ip)
        user = str(row.user)
        tenant = str(row.tenant)
        password = str(row.password)


    #ip = properties.openstack_IP
    #user = properties.openstack_user
    #tenant = properties.openstack_tenant
    #password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(env_ip, user, tenant, password)
    print auth_token

    server_id = request.GET.get('server_id')
    print 'server_id'+str(server_id)

    # List all Tenants
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get('http://' + env_ip + ':35357/v2.0/tenants', headers=headers)

    tenant_response = response.json()
    tenant_details = tenant_response["tenants"]

    tenant_id = ''
    for tenant in tenant_details:
        if tenant["name"] == 'demo':
            tenant_id = tenant["id"]

    host = request.GET.get('host')

    print 'host'+str(host)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    #host = 'Compute1'
    payload = { "os-migrateLive": {
        "host": host,
        "block_migration": True,
        "disk_over_commit": False}
    }
    response = requests.post('http://'+ env_ip +':8774/v2.1/'+ tenant_id + '/servers/' + server_id + '/action' ,data=json.dumps(payload),headers=headers)
    status = response.status_code
    print status
    #response = response.json()
    if status ==202:
        print 'Live Migration Success...'
        return JsonResponse({"status":"success"})
    else:
        print 'Live Migration Failure... Status Code:'+status
        return JsonResponse({"status":"failure"})

@csrf_exempt
def CreateVnfdTemplate(request):

    jsonrequest = json.loads(request.body)
    vnfdname = jsonrequest["vndfname"]
    vnfdcontent = jsonrequest["vnfdcontent"]
    print vnfdname
    print vnfdcontent
    yaml_string = '';
    for line in vnfdcontent.splitlines():
        print line
        line = line.rstrip('\n')
        yaml_string = yaml_string + line + '\\r\\n';
        # data = f.read().replace('\n','')
    print 'YAML_String:' + yaml_string

    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(ip, user, tenant, password)
    print "auth token:" + auth_token

    ###Creation the VNFD template
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    payload = {
	    "auth": {
		"tenantName": "admin",
		"passwordCredentials": {
		    "username": "admin",
		    "password": "devstack"
		}
	    },
	    "vnfd": {
		"service_types": [
		    {
		        "service_type": "vnfd"
		    }
		],
		"mgmt_driver": "noop",
		"infra_driver": "heat",
		"attributes": {
		    "vnfd": vnfdcontent
		},
		"name": vnfdname
	    }
	}
    print '*********************************************************'
    print json.dumps(payload)
    print '*********************************************************'
    print payload

    response = requests.post('http://' + ip + ':8888/v1.0/vnfds', data=json.dumps(payload), headers=headers)


    if response.status_code == 201:
        vnfd_create_response = response.json()
        vnfd_template_id = vnfd_create_response["vnfd"]["id"]
        print "vnfd_template_id:" + str(vnfd_template_id)
        print "vnfd_create_response:" + str(vnfd_create_response)
        return JsonResponse({"status": "success", 'content': "VNF catalog created successfully"})
    else:
        return JsonResponse({"status": "failed", 'content': "Problem occurred when creating VNF catalog"})


def DeployVnfdTemplate(request):
    # Creation of VNF Image using template ID
    vnfd_template_id = request.GET.get('vnfCatalogId')
    vnfd_name = request.GET.get('vndfname')

    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(ip, user, tenant, password)
    print "auth token:" + auth_token
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}

    vnf_image_payload = {
        "auth": {
            "tenantName": "admin",
            "passwordCredentials": {
                "username": "admin",
                "password": "demo"
            }
        },
        "vnf": {
            "vnfd_id": vnfd_template_id,
            "name": vnfd_name
        }
    }

    response = requests.post('http://' + ip + ':8888/v1.0/vnfs', data=json.dumps(vnf_image_payload),
                                       headers=headers)
    vnf_image_response = response.json()
    print "List create VNF response:" + str(vnf_image_response)

    print response.status_code
    print response
    if response.status_code == 201:
        return JsonResponse({"status":"success"})
    else:
        return JsonResponse({"status": "failed"})


def TerminateVNF(request):
    id = request.GET.get('id')

    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(ip, user, tenant, password)
    print "auth token:" + auth_token

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}

    response = requests.delete('http://' + ip + ':8888/v1.0/vnfs/'+str(id), headers=headers)
    print response.status_code
    if response.status_code == 204:
        return JsonResponse({"status": "success", "content": "VNF terminated successfully"})
    else:
        return JsonResponse({"status": "failed", "content": "Problem occurred when terminating the VNF"})


def ListVNFCatalogs(request):

    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(ip, user, tenant, password)
    print "auth token:" + auth_token

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}

    response = requests.get('http://' + ip + ':8888/v1.0/vnfds', headers=headers)

    return JsonResponse(response.json())

def ListVNFSCatalogs(request):

    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(ip, user, tenant, password)
    print "auth token:" + auth_token

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}

    response = requests.get('http://' + ip + ':8888/v1.0/vnfs', headers=headers)

    return JsonResponse(response.json())

def ListGlanceImages(request):

    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(ip, user, tenant, password)
    print "auth token:" + auth_token

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}

    response = requests.get('http://' + ip + ':9292/v2/images', headers=headers)

    return JsonResponse(response.json())


def CreateGlanceImage(request):
    uploadFromFile = request.POST.get('uploadFromFile')
    print uploadFromFile
    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    auth_token = generalfunctions.funcCreateAuthToken(ip, user, tenant, password)
    print "auth token:" + auth_token

    if uploadFromFile == 'true':
        name = request.POST.get('name')
        imageFormat = request.POST.get('imageFormat')
        containerFormat = request.POST.get('containerFormat')
        print name
        path = handle_uploaded_file_image(request.FILES['imageFile'])
        headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
        data = {'name': str(name), 'visibility':'public', 'disk_format': imageFormat, 'container_format': containerFormat}
        print data
        print 'http://' + ip + ':9292/v2/images'
        response = requests.post('http://' + ip + ':9292/v2/images', data=json.dumps(data), headers=headers)
        print response.status_code
        print response
        print '****************************************************************'
        response=response.json()
        image_file = response["file"]

        # upload Image Data
        headers = {'Content-type': 'application/octet-stream', 'X-Auth-Token': auth_token}
        data = open(path, 'rb').read()
        response = requests.put('http://' + ip + ':9292' + image_file, data=data, headers=headers)
        print response.status_code
        print response
        if response.status_code == 204:
            messages.error(request, 'Image created successfully')
            return HttpResponseRedirect('/Images/')
        else:
            messages.error(request, 'Some problem occurred when creating the image')
            return HttpResponseRedirect('/Images/')
    else:
        imageUrl = request.POST.get('imageUrl')
        imageFormat = request.POST.get('imageFormat')
        containerFormat = request.POST.get('containerFormat')
        print imageUrl
        name = request.POST.get('name')
        print name
        headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token, 'x-glance-api-copy-from':imageUrl, 'x-image-meta-name': name, 'x-image-meta-disk_format':imageFormat, 'x-image-meta-container_format':containerFormat}
        response = requests.post('http://' + ip + ':9292/v1/images', headers=headers)
        print response.status_code
        print response.json()
        if response.status_code == 201:
            messages.error(request, 'Image created successfully')
            return HttpResponseRedirect('/Images/')
        else:
            messages.error(request, 'Some problem occurred when creating the image')
            return HttpResponseRedirect('/Images/')


@api_view(['GET'])
def listEnvironments(request):
    print 'Inside list environments API'
    cursor = connections['default'].cursor()
    sql = "SELECT env_ip, env_desc FROM vnf_env"
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    json_res = []
    for row in results:
            env_ip = str(row.env_ip)
            env_desc= str(row.env_desc)
            print "Environment IP: " + env_ip
            print "Environment desc:"+ env_desc
            jsonobj = {'Environment_ip': env_ip, 'Environment_Desc': env_desc}
            json_res.append(jsonobj)

    print 'JsonResponse:' + str(json_res)
    return JsonResponse({"envs":json_res}, safe=False)

def GetHost(request):
    server_id = request.GET.get('server_id')
    env_ip = request.GET.get('env_ip')

    cursor = connections['default'].cursor()
    sql = "SELECT * FROM vnf_env where env_ip='"+env_ip+"'"
    print 'sql:' + sql
    cursor.execute(sql)
    results = namedtuplefetchall(cursor)
    for row in results:
        env_ip = str(row.env_ip)
        user = str(row.user)
        tenant = str(row.tenant)
        password = str(row.password)

    auth_token = generalfunctions.funcCreateAuthToken(env_ip, user, tenant, password)
    print "auth token:" + auth_token

    # List all Tenants
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get('http://' + env_ip + ':35357/v2.0/tenants', headers=headers)

    tenant_response = response.json()
    tenant_details = tenant_response["tenants"]

    print str(tenant_details)
    tenant_id = ''
    for tenant in tenant_details:
        if tenant["name"] == 'demo':
            tenant_id = tenant["id"]


    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    url = 'http://' + env_ip + ':8774/v2/' + tenant_id + '/servers/' + server_id
    print url
    response = requests.get(url, headers=headers)
    response = response.json()
    print response
    host = response["server"]["OS-EXT-SRV-ATTR:host"]
    print 'host' + str(host)
    return JsonResponse({"host": host})


def OsHypervisorStats(request):
    #tenant = request.GET.get('demo')
    tenant = 'admin'
    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    resp = generalfunctions.funcCreateAuthTokenAndGetEP(ip, user, tenant, password, "nova")
    auth_token = resp["auth_token"]
    url=resp["endpoint"]
    print auth_token
    print url

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get('http://' + ip + ':35357/v2.0/tenants', headers=headers)

    tenant_response = response.json()
    tenant_details = tenant_response["tenants"]

    tenant_id = ''
    for tenant in tenant_details:
        if tenant["name"] == tenant:
            tenant_id = tenant["id"]

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get(url+"/os-quota-sets/"+tenant_id+"/defaults", headers=headers)

    return JsonResponse(response.json())


def OsHypervisorStatistics(request):
    #tenant = request.GET.get('demo')
    tenant = 'admin'
    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    resp = generalfunctions.funcCreateAuthTokenAndGetEP(ip, user, tenant, password, "nova")
    auth_token = resp["auth_token"]
    url=resp["endpoint"]

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get('http://' + ip + ':35357/v2.0/tenants', headers=headers)

    tenant_response = response.json()
    tenant_details = tenant_response["tenants"]

    tenant_id = ''
    for tenant in tenant_details:
        if tenant["name"] == tenant:
            tenant_id = tenant["id"]

    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    response = requests.get(url+"/os-hypervisors/statistics", headers=headers)

    return JsonResponse(response.json())