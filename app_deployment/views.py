from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from django.conf import settings
from django.shortcuts import render
import os
import time
import json
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from murano_connect import utils as m_utils
from docker_ui.home import generalfunctions
import properties
import requests
import json
import datetime
import random
import base64
from django.contrib import messages

class IndexView(TemplateView):
    template_name = 'app_deployment.html'

    def get(self, request, *args, **kwargs):   
        
        #packages = m_utils.get_murano_packages()    
        #packages = "{'io.murano.apps.docker.DockerPostgreSQL': {'hash': '4d0200b151c6d50800d433283080888c'}}"
        #packages = json.loads(packages)
       
        context = {
            'some_dynamic_value': 'This text comes from django view!',
            #'packages' : json.dumps(packages),
        }
        
        return self.render_to_response(context)
        
        #return JsonResponse(context)
        
        #return render(request, 'app_deployment.html', {"foo": "bar"},
        #content_type="application/xhtml+xml")


class TestView(TemplateView):
    template_name = 'test.html'

    def get(self, request, *args, **kwargs):   
        
        #packages = m_utils.get_murano_packages()    
        #packages = "{'io.murano.apps.docker.DockerPostgreSQL': {'hash': '4d0200b151c6d50800d433283080888c'}}"
        #packages = json.loads(packages)
       
        
        pkg_ui = m_utils.test_pkg_ui()    
        
        
        
        context = {
            'pkg_ui': pkg_ui,
            'some_dynamic_value': 'This text comes from django view!',
            #'packages' : json.dumps(packages),
        }
        
        return self.render_to_response(context)
        
        #return JsonResponse(context)
        
        #return render(request, 'app_deployment.html', {"foo": "bar"},
        #content_type="application/xhtml+xml")
 
 
def getindexnew(request):
    
    #packages = m_utils.get_murano_packages()
    
    packages = "{'io.murano.apps.docker.DockerPostgreSQL': {'hash': '4d0200b151c6d50800d433283080888c'}}"
    context = {
        'some_dynamic_value': 'This text comes from django view!',
        'packages' : packages, 
    }    
    
    return render(request, 'app_deployment.html', context)

def installSoftwares(request): 
    
    try:      
        selected_pkgs = request.GET.get('ids')
        selected_pkgs = selected_pkgs.rstrip(',');    
        packagelist = selected_pkgs.split(',')    
        
        #Create environment
        response_env = m_utils.create_environment()
        if response_env['id']:        
            env_id = response_env['id']     
        else:        
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating environment'})
        
        #Create session
        response_sess = m_utils.create_session(env_id)
        if response_sess['id']:
            session_id = response_sess['id']
        else:
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating session'})  
        
        '''
        print "env_id \n "
        print env_id
        print "session_id \n"  
        print session_id
        '''
        msg = ""
        err_msg = ""
        print packagelist
        
        isDocker=False
        dockerEnv=""
        
        for package in packagelist:     
            
            #package_name = settings.MURANO_PACKAGE_NAMES[package]     
            package_name = package
            print package_name
            repo_url = settings.MURANO_PACKAGE_REPO_URL  
            
            #import package
            app_info = m_utils.import_application_package(repo_url, package_name)  
            #print "app_info \n"
            #print app_info
            
            if(app_info['response']['id']):             
                #Add application to environment
                respose_app = m_utils.add_application(env_id, session_id, app_info)
                #print "add application result \n"
                #print respose_app            
            else:            
                err_msg += 'Error occurred while importing package '+package+'\n'

            #if "docker" in package_name.lower():
            #    isDocker = True
            dockerEnv = env_id
        
        #app_info = []
        #respose_app = m_utils.add_application(env_id, session_id, app_info)   
        #Deploy session
        response_deploy = m_utils.deploy_session(env_id, session_id)
            
           
        if response_deploy['status_code'] == 200:
            msg +='Package deployment initiated \n'
            loopAndUpdateIP(dockerEnv)
        elif response_deploy['status_code'] == 404:
            err_msg += ' Specified session does not exist \n'             
        elif response_deploy['status_code'] == 401:
            err_msg += ' User is not authorized to access this session \n'             
        elif response_deploy['status_code'] == 403:
            err_msg += ' Session is already deployed or deployment is in progress \n'              
        else:
            err_msg += 'Error occurred while deploying  \n'  
                
        if msg == "":     
            return JsonResponse({'status': 'failed', 'msg': 'Submission completed with below messages \n'+err_msg})     
        else:
            return JsonResponse({'status': 'success', 'msg': 'Submission completed with below messages \n'+msg+err_msg,'envid':env_id,'sessid':session_id})
        
    except Exception as e:
        print e
        return JsonResponse({'status': 'failed', 'msg': 'Exception occurred while deploying packages'})     
    

def loopAndUpdateIP(env_id):
    isDone = True
    while isDone:
        resp = m_utils.get_deployment_status_completely(env_id)
        if resp['status']:
            if resp['status'] == 'ready':
                instance = resp['services'][0]
                ip = instance['ipAddresses'][0]
                name = instance['name']
                port = '2375'
                generalfunctions.addNode(ip, port, name)
                print ip
                isDone=False


def getDeployInfo(request):    
    
    '''
    env_id = request.GET.get('envid')
    session_id = request.GET.get('sessid')     
    resp =m_utils.get_session_deatils(env_id, session_id) 
    if resp !=False:
        return JsonResponse({'status': 'success', 'state': resp['state']})   
    else:
        return JsonResponse({'status': 'failed', 'msg': 'Error occurred,while fetching deployment details'}) 
    '''
    env_id = request.GET.get('envid')
    
    resp = m_utils.get_deployment_status(env_id)
    
    #print resp
    
    if resp !=False:
        return JsonResponse({'status': 'success', 'state': str(resp['status'])})   
    else:
        return JsonResponse({'status': 'failed', 'msg': 'Error occurred,while fetching deployment details'}) 
    
def test_pkg(request):
    
    m_utils.prepare_mpl_package()        
    
    return HttpResponse("Done")

def getPackages(request):
    
    resp = m_utils.get_murano_packages()        
    
    return HttpResponse(resp)
    
@csrf_exempt
def uploadFiles(request):
    
    #resp = m_utils.get_murano_packages()        
    
    #return HttpResponse(resp)
    print request.FILES['file']
    f = request.FILES['file']
    
    path = handle_uploaded_file(f)
    
    '''with open('C:\Users', 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)'''
    return JsonResponse({'status': 'ok','filepath':path})   

def handle_uploaded_file(f):
    print f.name
    extension = f.name.split('.')[-1]
    filename = f.name +"oho"+ '.' + extension
    #path = properties.filestoreparth + f.name
    path = settings.UPLOAD_FILE_PATH +"\\"+ f.name
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
    print path
    return path

def createCustomPackage(request):
    
    '''selected_files = request.GET.get('files')
    selected_files = selected_files.rstrip(',')    
    filelist = selected_files.split(',')   
    #print filelist
    pkg_zip = m_utils.prepare_hot_package(selected_files)
    
    #print filelist
    
    return HttpResponse("Done")'''


    try:      
        selected_files = request.GET.get('files')
        selected_files = selected_files.rstrip(',')    
        filelist = selected_files.split(',')   
        #Create environment
        response_env = m_utils.create_environment()
        if response_env['id']:        
            env_id = response_env['id']     
        else:        
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating environment'})
        
        #Create session
        response_sess = m_utils.create_session(env_id)
        if response_sess['id']:
            session_id = response_sess['id']
        else:
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating session'})  
        
        '''
        print "env_id \n "
        print env_id
        print "session_id \n"  
        print session_id
        '''
        msg = ""
        err_msg = ""
        print filelist
        
        
        
        for package in filelist:     
            
            print package
            package_name = m_utils.prepare_hot_package(package)
            #package_name = settings.MURANO_PACKAGE_NAMES[package]     
            #package_name = pkg_zip     
            repo_url = "" 
            print package_name
            #import package
            app_info = m_utils.import_application_package(repo_url, package_name)  
            print "app_info \n"
            print app_info
            
            if(app_info['response']['id']):             
                #Add application to environment
                respose_app = m_utils.add_application(env_id, session_id, app_info)
                #print "add application result \n"
                #print respose_app            
            else:            
                err_msg += 'Error occurred while importing package '+package+'\n'
        
        
        #app_info = []
        #respose_app = m_utils.add_application(env_id, session_id, app_info)   
        #Deploy session
        response_deploy = m_utils.deploy_session(env_id, session_id)
            
           
        if response_deploy['status_code'] == 200:
            msg +='Package deployment initiated \n'            
        elif response_deploy['status_code'] == 404:
            err_msg += ' Specified session does not exist \n'             
        elif response_deploy['status_code'] == 401:
            err_msg += ' User is not authorized to access this session \n'             
        elif response_deploy['status_code'] == 403:
            err_msg += ' Session is already deployed or deployment is in progress \n'              
        else:
            err_msg += 'Error occurred while deploying  \n'  
                
        if msg == "":     
            return JsonResponse({'status': 'failed', 'msg': 'Submission completed with below messages \n'+err_msg})     
        else:
            return JsonResponse({'status': 'success', 'msg': 'Submission completed with below messages \n'+msg+err_msg,'envid':env_id,'sessid':session_id})
        
    except Exception as e:
        print e
        return JsonResponse({'status': 'failed', 'msg': 'Exception occurred while deploying packages'})   
    
    
 
    
def test_fn(request):
    ip = 'controller-demodevstack-xppgiav6.srv.ravcloud.com'
    ###Creating auth_token
    data = {"auth": {"tenantName": "demo", "passwordCredentials": {"username": "demo", "password": "demo"}}}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    data_json = json.dumps(data)
    response = requests.post('http://' + ip + ':35357/v2.0/tokens', data=data_json, headers=headers)
    #print(response.text)
    response = response.json()
    auth_token = response["access"]["token"]["id"]
    print auth_token
    
    #env_id ='5ffbea6d511e46fe985fa789ab649745'
    env_id ='1a5cb9ba73a94c95af20bd2f4d5d6c9a'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    resp_config = requests.get('http://' + ip + ':8082/v1/environments/' + env_id , headers=headers)
    print resp_config
    resp_config = resp_config.json()
    
    print resp_config
   
    
    
    return HttpResponse("Done")
    
    
    
    ip = 'controller-multinodetacker-yrcntlzg.srv.ravcloud.com'
    ###Creating auth_token
    data = {"auth": {"tenantName": "demo", "passwordCredentials": {"username": "demo", "password": "demo"}}}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    data_json = json.dumps(data)
    response = requests.post('http://' + ip + ':35357/v2.0/tokens', data=data_json, headers=headers)
    #print(response.text)
    response = response.json()
    auth_token = response["access"]["token"]["id"]
    print auth_token
    
    ###Creating a template
    utc_datetime = datetime.datetime.utcnow()
    formated_string = utc_datetime.strftime("%Y-%m-%d-%H%M%SZ")
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    payload = {'name': 'temp_name_1' + str(formated_string)}
    resp_temp = requests.post('http://' + ip + ':8082/v1/templates', data=json.dumps(payload), headers=headers)
    resp_temp = resp_temp.json()
    # environment Id
    temp_id = resp_temp["id"]
    print temp_id
    
    
    instance_json = {
      "instance": {
        "flavor": "m1.small",
        "keyname": "key_tacker",
        "assignFloatingIp": "true",
        "image": "debian-8-m-agent.qcow2",
        "?": {
          "type": "io.murano.resources.Instance",
          "id": "b49352b8-95cf-4d63-a60b-61c8c8ea88a9"
        }
      },
      "name": "PostgreSQL",
      "?": {
       
        "type": "io.murano.databases.PostgreSql",
        "id": "fdba9ef8710b4a4b907c6ce48d350a84"
      }
    }   
    
    
    package_name = 'io.murano.databases.PostgreSql'      
    repo_url = settings.MURANO_PACKAGE_REPO_URL  
        
        #import package
    app_info = m_utils.import_application_package(repo_url, package_name)
    
    
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    resp_app = requests.post('http://' + ip + ':8082/v1/templates/' + temp_id + '/services',
                            data=json.dumps(instance_json), headers=headers)
    resp_app = resp_app.json()
    # environment Id
    app_id = resp_app["instance"]
    print app_id
    
    
    ###Creating environmetn template in template
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    payload = {'name': 'env_name_11' + str(formated_string)}
    resp_env = requests.post('http://' + ip + ':8082/v1/templates/' + temp_id + '/create-environment', data=json.dumps(payload), headers=headers)
    resp_env = resp_env.json()
    # environment Id
    env_id = resp_env["environment_id"]
    session_id = resp_env["session_id"]
    print env_id
    print session_id
    
    ###Session id
    resp_config = requests.get('http://' + ip + ':8082/v1/environments/' + env_id + '/sessions/' + session_id, headers=headers)
    resp_config = resp_config.json()
    instance_state = resp_config["state"]
    print instance_state
    
    ###deploy a session
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token,'X-Configuration-Session':session_id}
    resp_session = requests.post('http://' + ip + ':8082/v1/environments/' + env_id + '/sessions/' + session_id + '/deploy' , headers=headers)
    print resp_session.status_code
    
    
    return HttpResponse(resp_session.status_code)
    
    
          
    
    #time.sleep(2)    
    
def createInstance(request):
    image_id=request.GET.get('image_id')
    flavor_id=properties.FLAVOR


    #encoded_string = ""
    #with open("/home/user_data.file", "rb") as data_file:
    #    encoded_string = base64.b64encode(data_file.read())

    print image_id
    data = {
        "server": {"name": "instance1", "imageRef": image_id, "flavorRef": flavor_id,
                   "max_count": 1, "min_count": 1, "key_name": properties.KEYPAIR, "networks":[{"uuid": properties.NETWORK}]}
    }

    print data
    print json.dumps(data)
    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password

    resp = generalfunctions.funcCreateAuthTokenAndGetEP(ip, user, tenant, password, "nova")
    auth_token = resp["auth_token"]
    url = resp["endpoint"]
    print auth_token
    print url


    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    print url+"/servers"
    response = requests.post(url+"/servers", data=json.dumps(data), headers=headers)
    print response
    print response.json()

    response = response.json()
    checkMachineStatusAndUpdateIp(url, auth_token, response["server"]["id"])
    return JsonResponse({"status":"success", "server_id": response["server"]["id"]})

def checkMachineStatusAndUpdateIp(url, auth_token, server_id):
    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password
    print server_id
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    print "here"
    loop = True
    while loop:
        print url + "/servers/"+server_id
        response = requests.get(url + "/servers/"+server_id, headers=headers)
        print response
        response = response.json()
        if response["server"]["status"]:
            print response
            if response["server"]['addresses']:
                if response["server"]['addresses']['Intranet-10.142.153.0/24']:
                    if response["server"]['addresses']['Intranet-10.142.153.0/24'][0]:
                        if response["server"]['addresses']['Intranet-10.142.153.0/24'][0]['addr']:
                            ip = response["server"]['addresses']['Intranet-10.142.153.0/24'][0]['addr']
                            if ip != "":
                                name = response["server"]['name']
                                port = '2375'
                                print ip
                                print name

                                generalfunctions.addNode(ip, port, name)
                                loop = False


def deployHeatTemplate(request):
    ip = properties.openstack_IP
    user = properties.openstack_user
    tenant = properties.openstack_tenant
    password = properties.openstack_password


    print "********************************************"

    path = handle_uploaded_file(request.FILES['templateFile'])
    #path="/home/rdk/Desktop/docker_heat.yaml"
    fileData = open(path, 'rb').read()
    print fileData
    resp = generalfunctions.funcCreateAuthTokenAndGetEP(ip, user, tenant, password, "nova")
    auth_token = resp["auth_token"]
    url = resp["endpoint"]
    tenantId = resp["tenantId"]
    print auth_token
    print url
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    data = {"stack_name": "teststack"+str(random.random()), "template": fileData}

    url = "http://" + ip + ":8004/v1/"+ tenantId +"/stacks"
    print url
    print "#####"
    print data
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print response
    response = response.json()
    print response
    print response["stack"]["links"][0]["href"]

    url = response["stack"]["links"][0]["href"]
    #url = "http://tacker-mitaka-y8uyph4a.srv.ravcloud.com:8004/v1/fd3164ec53b94437a281f5196febba72/stacks/teststack/3014b171-63df-481e-9444-79eadf684545"
    print url
    loop = True
    while loop:
        response = requests.get(url, headers=headers)
        response=response.json()
        if 'outputs' in response["stack"]:
            outputs = response["stack"]["outputs"]
            ip=""
            name=""
            for output in outputs:
                print response
                if output["output_key"] == "name":
                    name = output["output_value"][0]
                if output["output_key"] == "ip":
                    ip = output["output_value"][0]

            port = '2375'
            print ip
            print name
            generalfunctions.addNode(ip, port, name)
            loop = False

    messages.error(request, 'Stack created and deployed successfully.')
    return HttpResponseRedirect('/app_deployment/')


def handle_uploaded_file(f):
    print f.name
    UPLOAD_FILE_PATH = settings.UPLOAD_FILE_PATH
    extension = f.name.split('.')[-1]
    filename = f.name +`random.random()` + '.' + extension
    path = UPLOAD_FILE_PATH + "/" + f.name
    #path = 'c:\\files\\' + f.name
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path



