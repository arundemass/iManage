import requests
import json
import datetime
import os



from django.conf import settings

import keystoneclient.v2_0.client as ksclient
from muranoclient.v1 import client as v1_client    
from muranoclient.v1 import shell as v1_shell
from docker_ui.home import generalfunctions

from oslo_log import log as logging
LOG = logging.getLogger(__name__)



ip = settings.MURANO_CONNECT['ip']
tenantname = settings.MURANO_CONNECT['tenantname']
username = settings.MURANO_CONNECT['username']
password = settings.MURANO_CONNECT['password']
admin_token = settings.MURANO_CONNECT['admin_token']
env_name_prefix = settings.MURANO_CONNECT['env_name_prefix']
endpoint = "http://"+ip+":8082/"
key_name = settings.MURANO_KEY_PAIR_NAME
CUSTOM_PACKAGE_DIR = settings.MURANO_CUSTOM_PACKAGE_DIR
default_image = settings.MURANO_DAFAULT_IMAGE

'''
    Create auth_token
'''
def get_auth_token():   
    
    '''
    #Using REST API
    data = {"auth": {"tenantName": tenantname, "passwordCredentials": {"username": username, "password": password}}}
    headers = {'Content-type': 'application/json','Accept':'application/json'}
    data_json = json.dumps(data)
    response = requests.post('http://'+ ip +':5000/v2.0/tokens', data=data_json, headers=headers)   
    response = response.json()
    auth_token = response["access"]["token"]["id"]    
    return auth_token
    '''    
    #Using Keystone
    keystone = ksclient.Client(auth_url="http://"+ip+":35357/v2.0",
                           username=username,
                           password=password,
                           tenant_name=tenantname)
    
    return keystone.auth_token

'''    
    Create  environment

'''
def create_environment():
    
    auth_token = get_auth_token()
        
    utc_datetime = datetime.datetime.utcnow()
    formated_string = utc_datetime.strftime("%Y-%m-%d-%H%M%SZ") 
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
    payload = { 'name': env_name_prefix+str(formated_string)}    
    resp_env = requests.post('http://'+ip+':8082/v1/environments',data=json.dumps(payload),headers=headers)    
    resp_env = resp_env.json()     
    #environment Id 
    #env_id = resp_env["id"]     
    return resp_env


def import_application_package(repo_url,package_name):
    
    try:
        auth_token = get_auth_token()
        #initializing MuranoClient
        mc = v1_client.Client(endpoint=endpoint, token= auth_token,timeout = 600)
        #mc.environments.list()
        #mc.environments.get(environment_id='b93d63bde2b3423cb1f8d5e54aeb99a3')
        
        args = InitArgs()    
        ###filename is URL###
        #args.filename = {"http://storage.apps.openstack.org/apps/io.murano.apps.apache.ApacheHttpServer.zip"}
        args.murano_repo_url = ''
        
        ###filename is name and repo_url###
        #args.filename = {"io.murano.apps.apache.ApacheHttpServer"}
        #args.murano_repo_url = 'http://storage.apps.openstack.org/'    
        args.filename = {package_name}
        args.murano_repo_url = repo_url
        
        ###filename is localpath###
        #args.filename = {"C:/Users/admin/Downloads/io.murano.apps.apache.ApacheHttpServer.zip"}
        #args.murano_repo_url = ''    
        args.categories = None
        args.is_public = False
        args.package_version = ''    
        args.exists_action = 'u' #(s)kip, (u)pdate, (a)bort    
        
        
        response = v1_shell.do_package_import(mc, args)
        
        '''
            Check whether the package imported properly
        '''        
        
        if os.path.exists(package_name):
            package_name = os.path.basename(package_name)
            package_name = os.path.splitext(package_name)[0]
            
        package_generator = mc.packages.filter(fqn = package_name)
        #pp = mc.packages.list()
        package_obj =  package_generator.next()        
        package_info = package_obj.__dict__
        print package_info
        #print package_info['id']
        #print package_info['class_definitions']['id']
        
        if package_info['id']: 
            return {'status': 'success', 'msg': 'Package imported successfully','response':package_info}       
        else:
            return {'status': 'failed', 'msg': 'Error occurred,while importing the package'}
        
    except Exception as e:
        LOG.error("Error  occurred,"
                          " while importing the package".format(e))
        return {'status': 'failed', 'msg': 'Error Occurred,while importing the package'}
        #raise   
    
    return {'status': 'success', 'msg': 'Package imported successfully'}

   
  
'''
Create a configuration session  
'''
def create_session(env_id):
    
    auth_token = get_auth_token()
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}      
    resp_config = requests.post('http://'+ip+':8082/v1/environments/'+env_id+'/configure',headers=headers)    
    resp_config = resp_config.json()   
    #environment Id 
    #session_id = resp_config["id"]     
    return resp_config

'''
    Add applications to an environment
'''

def add_application(env_id,session_id,app_info):
    
    auth_token = get_auth_token() 
    
    utc_datetime = datetime.datetime.utcnow()
    formated_string = utc_datetime.strftime("%Y-%m-%d-%H%M%SZ")    
   
    #securityGroupName
    #"securityGroupName" :"test_grp",
    #"availabilityZone": "nova",
    #"image": "ubuntu14.04-x64-docker",
    
    instance_json = {
      "instance": {
        "flavor": "m1.small",
        "keyname": key_name,        
        "assignFloatingIp": "true",   
        "availabilityZone": "nova",    
        "image": default_image,
        "?": {
          "type": "io.murano.resources.LinuxMuranoInstance",
          "id": generate_uuid()
        },
        "name": "inst_"+str(formated_string)
      },
      "name": str(app_info['response']['name']),
      "?": {        
        "type": str(app_info['response']['fully_qualified_name']),
        "id": str(app_info['response']['id'])
      }
      
    }
    
    '''instance_json = {
      "instance": {
        "flavor": "m1.murano15",
        "keyname": key_name,        
        "assignFloatingIp": "true",   
        "availabilityZone": "nova",    
        "image": "debian-8-m-agent.qcow2",
        "?": {
          "type": "io.murano.resources.LinuxMuranoInstance",
          "id": generate_uuid()
        },
        "name": "inst_"+str(formated_string)
      },
      "name": "ApacheMySql",
      "?": {        
        "type": "io.murano.apps.apache.ApacheHttpServer",
        "id": generate_uuid()
      }
      
    }'''
    
    
    
    #print instance_json
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token,'X-Configuration-Session':session_id}
    resp_app = requests.post('http://'+ip+':8082/v1/environments/'+env_id+'/services',data=json.dumps(instance_json),headers=headers)
    
    #resp_app = resp_app.json()     
    #print resp_app    
    return resp_app.__dict__

'''
  Depoly session

'''
def deploy_session(env_id,session_id):
    
    auth_token = get_auth_token()
    
    #headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token,'X-Configuration-Session':session_id}
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
    resp_deploy = requests.post('http://'+ip+':8082/v1/environments/'+env_id+'/sessions/'+session_id+'/deploy',headers=headers)    
    #print resp_deploy
    #resp_deploy = resp_deploy.json()  
    #print resp_deploy.__dict__  
    
        
    '''
    #initializing MuranoClient
    mc = v1_client.Client(endpoint=endpoint, token= auth_token,timeout = 6000)
   
    args = InitArgs()    
    
    args.id = env_id
    args.session_id = session_id    
    response = v1_shell.do_environment_deploy(mc, args)
    
    print resp_deploy
    print resp_deploy.__dict__
    '''
      
    return resp_deploy.__dict__



def get_deployment_status(env_id):
    ip = settings.MURANO_CONNECT['ip']
    # ='1a5cb9ba73a94c95af20bd2f4d5d6c9a'
    auth_token = get_auth_token()
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    resp_deploy = requests.get('http://' + ip + ':8082/v1/environments/' + env_id , headers=headers)
    #print resp_config
    resp_deploy = resp_deploy.json()
    print "***********************************************************************************************"
    print resp_deploy
    
    if(resp_deploy['status']):
        if resp_deploy['services']:
            instance = resp_deploy['services'][0]
            ip = instance['ipAddresses'][0]
            name = instance['name']
            port = '2375'
            generalfunctions.addNode(ip, port, name)
            print ip
        return resp_deploy
    else:
        return False

def get_deployment_status_completely(env_id):

        # ='1a5cb9ba73a94c95af20bd2f4d5d6c9a'
        auth_token = get_auth_token()
        headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
        resp_deploy = requests.get('http://' + ip + ':8082/v1/environments/' + env_id, headers=headers)
        # print resp_config
        resp_deploy = resp_deploy.json()
        print "***********************************************************************************************"
        print resp_deploy

        return resp_deploy
    
    
'''
 Fetch session details
'''

def get_session_deatils(env_id,session_id):
    
    try:
        auth_token = get_auth_token()
        #print env_id
        #print session_id
        
        headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
        resp_sess = requests.get('http://'+ip+':8082/v1/environments/'+env_id+'/sessions/'+session_id,headers=headers)    
        print resp_sess
        print resp_sess.__dict__['status_code']
        if(resp_sess.__dict__['status_code'] == 200):
            return resp_sess.json() 
        else:
            return False
    except Exception as e:
        return False 





def list_deployments(env_id):    
    
    auth_token = get_auth_token()
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
    resp_dep = requests.get('http://'+ip+':8082/v1/environments/'+env_id+'/deployments/',headers=headers)  
    print resp_dep
    print resp_dep.__dict__

'''
 Test function
 
'''
def check_test_ok(env_id):
    
    auth_token = get_auth_token()
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token}
    
    app_id = ""
    
    #resp_app = requests.get('http://'+ip+':8082/v1//environments/'+env_id+'/services/'+app_id,headers=headers)  
    
    #resp_app = requests.get('http://'+ip+':8082/v1/images/detail',headers=headers)    
    #print
    
    #resp_app = resp_app.json()  
    
    #v1/images/detail
    
    #from muranoclient.glance import client as gl_client
    
    #gl_client.Client(endpoint=endpoint, type_name ="" , type_version="")
    
    #auth_token = get_auth_token()
        #initializing MuranoClient
    #mc = v1_client.Client(endpoint=endpoint, token= auth_token,timeout = 60)
        #mc.environmen
    
    #print resp_app.__dict__
    
    keystone = ksclient.Client(auth_url="http://"+ip+":35357/v2.0",
                           username=username,
                           password=password,
                           tenant_name=tenantname)
    
    import glanceclient.v2.client as glclient
    
    glance_endpoint = keystone.service_catalog.url_for(service_type='image',endpoint_type='publicURL')
    
    print glance_endpoint
    
    glance = glclient.Client(endpoint, token=keystone.auth_token)
    
    images = glance.images.list()
    
    print images.next()   
    #return keystone.auth_token    
    
    
    return images   


def generate_uuid():
    import uuid
    """Generate uuid for objects."""
    return uuid.uuid4().hex


def prepare_mpl_package():
    
    from muranoclient.v1.package_creator import mpl_package
    
    import os
    
    
    #FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
    #                                      'static-assets'))
    FIXTURE_DIR =  "/home/unameit/Downloads/deployPortal/static-assets/murano_packages"
    TEMPLATE = os.path.join(FIXTURE_DIR, 'heat-template.yaml')
    CLASSES_DIR = os.path.join(FIXTURE_DIR, 'test-app', 'Classes')
    RESOURCES_DIR = os.path.join(FIXTURE_DIR, 'test-app', 'Resources')
    UI = os.path.join(FIXTURE_DIR, 'test-app', 'ui.yaml')
    LOGO = os.path.join(FIXTURE_DIR, 'logo.png')
    
    
    args = InitArgs()
    args.template = TEMPLATE
    args.classes_dir = CLASSES_DIR
    args.resources_dir = RESOURCES_DIR
    args.type = 'Application'
    args.name = 'ApacheMySql'
    args.author = 'TestAuthor'
    args.full_name = 'io.murano.apps.imanage.ApacheMySql'
    #args.tags = "[HTTP, Server, WebServer, HTML, Apache,Database, MySql, SQL, RDBMS]"
    args.tags = ["HTTP", "Server", "WebServer", "Apache","Database", "MySql", "SQL", "RDBMS"]
    args.description = 'Test description'
    args.ui = UI
    args.logo = LOGO
    args.require = 'io.murano.databases'

        
    #prepared_files = ['UI', 'Classes', 'manifest.yaml',
    #                 'Resources', 'logo.png']
    package_dir = mpl_package.prepare_package(args)
    
    
    ZIP_DIR = "/home/unameit/Downloads/deployPortal/static-assets/murano_packages"
    
    
    zip_files(package_dir,ZIP_DIR+"/zip/"+args.full_name)
    
    print package_dir
    #self.assertEqual(sorted(prepared_files),
    #                 sorted(os.listdir(package_dir)))
    #shutil.rmtree(package_dir)
    
    
    
    

def zip_files(src, dst):
    import zipfile
    import os
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                        arcname)
            zf.write(absname, arcname)
    zf.close()
    
def get_murano_packages():
    
    #auth_token = get_auth_token()
    headers = {'Content-type': 'application/json','Accept':'application/json'}
    resp_assets = requests.get('https://apps.openstack.org/api/v1/assets',headers=headers)  
    
    #print json.load('https://apps.openstack.org/api/v1/assets')
    assets =   resp_assets.json()['assets']
    
    
    resp = []
    
    
    for entry in assets:
       #print entry['service']['type']
       if entry['service']['type'] == "murano":
           
           #z = {**entry['service'], **entry['name'],**entry['release']}
           #z = entry['service'].copy()
           #entry['service'].update(entry['provided_by'])
           
           entry['service'].update({'label': entry['name']})
           entry['service'].update({'source':  entry['service']['type']})
           entry['service'].update({'type': 'option'})
           entry['service'].update({'value':  entry['service']['package_name']})
           
           
           #default_data.update({'item3': 3})
           #print entry
           #resp[entry['service']['package_name']] = entry['service']
           
           #resp += entry['service']
           
           resp.append(entry['service'])
    
    respc = []   
    #pkg1 = "{'source': 'murano', 'package_name': 'io.murano.apps.pivotal.OpsManager', 'format': 'package', 'type':'option','Label':'Mysql'}"
          
    #respc.append({'source': 'murano','package_name': 'io.murano.apps.pivotal.OpsManager12','format': 'package', 'type':'option','label':'Mysql','value': 'io.murano.apps.magnum.plugin.MagnumBayApp12'})
    #exit
    CUSTOM_DIR = CUSTOM_PACKAGE_DIR+"/custom"
   
    for file in os.listdir(CUSTOM_DIR):
        if file.endswith(".zip"):
            #print(file)
            pkg_fqn = file.strip('.zip')
            pkg_name = str(pkg_fqn.split(".")[-1:][0])
            respc.append({'source': 'murano','package_name': pkg_fqn,'format': 'package', 'type':'option','label':pkg_name,'value': CUSTOM_DIR+"/"+file})
    
            
    '''resp2 =  [{
            "type": "optiongroup",
            "label": "Custom Packages",
            "children":respc                    
            }]'''
           
    resp1 =  [{
            "type": "optiongroup",
            "label": "Murano Packages",
            "children":resp                    
            },{
            "type": "optiongroup",
            "label": "Custom Packages",
            "children":respc                    
            }
              
            ]
    
    #resp1.append(resp2)
    print json.dumps(resp1)
    return json.dumps(resp1)

   
    
    #for k in assets:        
    #        print 
    '''    
        for v in assets[k]:
            if searchFor in v:
                return k
    #print resp_assets.__dict__
    '''
    

def prepare_hot_package(filepath):
    
    
    import yaml
    
    decr = ""
    stream = open(filepath, "r")
    docs = yaml.load_all(stream)
    for doc in docs:
        for k,v in doc.items():            
            print k, "->", v
            if k == "description":
                decr = v
    print "\n",
    
    import os
    from muranoclient.v1.package_creator import hot_package    
    
   
    archive_name = os.path.basename(filepath)
    archive_name = os.path.splitext(archive_name)[0]
   
    LOGO = CUSTOM_PACKAGE_DIR+"/custom_package_default_logo.png"    
    args = InitArgs()
    args.template = filepath    
    args.name = str(archive_name)
    args.author = username
    args.full_name = str('io.murano.apps.generated.'+archive_name.title())
    args.tags = ["Heat-generated"]
    args.description = str(decr)
    args.logo = LOGO        
  
    package_dir = hot_package.prepare_package(args)
    print package_dir
    
    ZIP_DIR = CUSTOM_PACKAGE_DIR
    
    
    zip_files(package_dir,ZIP_DIR+"/custom/"+args.full_name)
    
    return ZIP_DIR+"/custom/"+args.full_name+".zip"
    
    
    #murano package-create --template my_hot_template --logo logo.png
    '''
    auth_token = get_auth_token()
        #initializing MuranoClient
    mc = v1_client.Client(endpoint=endpoint, token= auth_token,timeout = 600)
    
    args = InitArgs()    
    
    args.template = filepath  
    
    args.classes_dir = "" 
    
    args.output  = '/'
    
    LOGO = "/home/unameit/Downloads/deployPortal/static-assets/images/custom_package_logo.png"
    args.name = os.path.splitext(filepath)[0]
    args.author = username
    args.full_name = 'io.murano.apps.generated.'+os.path.splitext(filepath)[0].title()
    args.tags = 'Heat-generated'
    args.description = 'Test description' 
    args.logo = LOGO      

    response = v1_shell.do_package_create(mc, args)
    
    print response'''
    
    
    #ZIP_DIR = "D:\Roshin\workspace\deployPortal\static-assets\murano_packages"
    
    
    #zip_files(package_dir,ZIP_DIR+"\zip/"+args.full_name)
    
   
    #self.assertEqual(sorted(prepared_files),
    #                 sorted(os.listdir(package_dir)))
    #shutil.rmtree(package_dir)
      



def test_pkg_ui():
    
    
    auth_token = get_auth_token()
        #initializing MuranoClient
    mc = v1_client.Client(endpoint=endpoint, token= auth_token,timeout = 600)  
    
    
    
    #app_id = '888102e1bae34046b2d531012441fa17'
    app_id = '09a49f9b984c4b91a169dcb6f67450b4'
    return mc.packages.get_ui(app_id,make_loader_cls())
    #return mc.packages.
    
    #from muranoclient.v1 import packages as v1_packages
        #app_id = '888102e1bae34046b2d531012441fa17'
        #print v1_packages.PackageManager.get_supplier_logo
        
def make_loader_cls():    
    
    import yaml    
    
    class Loader(yaml.Loader):
        pass

    def yaql_constructor(loader, node):
        value = loader.construct_scalar(node)
        return YaqlExpression(value)

    # workaround for PyYAML bug: http://pyyaml.org/ticket/221
    resolvers = {}
    for k, v in yaml.Loader.yaml_implicit_resolvers.items():
        resolvers[k] = v[:]
    Loader.yaml_implicit_resolvers = resolvers

    Loader.add_constructor(u'!yaql', yaql_constructor)
    Loader.add_implicit_resolver(
        u'!yaql', YaqlExpression, None)

    return Loader
    
class InitArgs(object):
    pass


# YaqlExpression
import re
import types

import yaql
from yaql.language import exceptions as yaql_exc


def _set_up_yaql():
    legacy_engine_options = {
        'yaql.limitIterators': 100,
        'yaql.memoryQuota': 20000
    }
    return yaql.YaqlFactory().create(options=legacy_engine_options)

YAQL = _set_up_yaql()


class YaqlExpression(object):
    def __init__(self, expression):
        self._expression = str(expression)
        self._parsed_expression = YAQL(self._expression)

    def expression(self):
        return self._expression

    def __repr__(self):
        return 'YAQL(%s)' % self._expression

    def __str__(self):
        return self._expression

    @staticmethod
    def match(expr):
        if not isinstance(expr, types.StringTypes):
            return False
        if re.match('^[\s\w\d.:]*$', expr):
            return False
        try:
            YAQL(expr)
            return True
        except yaql_exc.YaqlGrammarException:
            return False
        except yaql_exc.YaqlLexicalException:
            return False

    def evaluate(self, data=yaql.utils.NO_VALUE, context=None):
        return self._parsed_expression.evaluate(data=data, context=context)

    
    


