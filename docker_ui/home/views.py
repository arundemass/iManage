#! /usr/bin/env python2.7

import json
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import random
from django.contrib import messages
import urllib
import json

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

class KubernetesView(TemplateView):
    template_name = 'Kubernetes.html'

    def get(self, request, *args, **kwargs):
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)


def GetImages(request):
    resp = requests.get('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/images/json')
    item = resp.json()
    return JsonResponse({'status': 'success', 'content': item})

def GetContainers(request):
    resp = requests.get('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/containers/json?all=1')
    item = resp.json()
    return JsonResponse({'status': 'success', 'content': item})

def UploadImage(request):
    path = handle_uploaded_file(request.FILES['dockerFile'])
    name = request.POST.get('name')
    tag = request.POST.get('tag')
    if name=='':
        messages.error(request, 'Please enter a name')
        return HttpResponseRedirect('/Build/')

    name = name+':'+tag

    headers = {'Content-Type': 'application/tar'}

    data = open(path, 'rb').read()
    r = requests.post('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/build?t='+urllib.quote_plus(name), data=data, headers=headers)
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

    if name=='':
        messages.error(request, 'Please enter a name')
        return HttpResponseRedirect('/Build/')

    if tag=='':
        tag='latest'

    print 'http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/images/create?fromImage='+urllib.quote_plus(name)+'&tag='+urllib.quote_plus(tag)
    r = requests.post('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/images/create?fromImage='+urllib.quote_plus(name)+'&tag='+urllib.quote_plus(tag))


    if r.status_code == 200:
        messages.error(request, 'Image pulled successfully.')
        return HttpResponseRedirect('/Build/')
    else:
        messages.error(request, 'Pulling the image failed with the following error: '+r.content)
        return HttpResponseRedirect('/Build/')


def DeleteImage(request):
    name = request.GET.get('name')
    r = requests.delete('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/images/'+name +'?force=true')
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
    r = requests.post('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/containers/'+id+'/kill')
    print r.status_code
    if r.status_code == 204:
        d = json.loads(r.content)
        return JsonResponse({'status': 'success', 'content': 'Container Killed successfully'})
    elif r.status_code == 404:
        return JsonResponse({'status': 'failed', 'content': 'Killing the container failed with the following error: '+r.content})
    else:
        return JsonResponse({'status': 'failed', 'content': 'Killing the container failed with the following error: '+r.content})


def DeleteContainer(request):
    id = request.GET.get('id')
    r = requests.delete('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/containers/'+id)
    print r.status_code
    if r.status_code == 204:
        return JsonResponse({'status': 'success', 'content': 'Container deleted successfully'})
    elif r.status_code == 404:
        return JsonResponse({'status': 'failed', 'content': 'Deleting the container failed with the following error: '+r.content})
    elif r.status_code == 406:
        return JsonResponse({'status': 'failed', 'content': 'Deleting the container failed with the following error: '+r.content})
    else:
        return JsonResponse({'status': 'failed', 'content': 'Deleting the container failed with the following error: '+r.content})


def RunContainer(request):
    name = request.GET.get('name')
    image = request.GET.get('image')
    commands = request.GET.get('commands')

    commands = commands.split()
    print commands

    headers = {'Content-Type': 'application/json'}
    data={
          "AttachStdin": False,
          "AttachStdout": True,
          "AttachStderr": True,
          "Tty": False,
          "OpenStdin": False,
          "StdinOnce": False,
          "Cmd": commands,
          "Image": image
        }

    print json.dumps(data)
    r = requests.post('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/containers/create?name='+name, data=json.dumps(data), headers=headers)
    print r.content
    print r.status_code
    if r.status_code == 201:
        d = json.loads(r.content)
        return JsonResponse({'status': 'success', 'content': 'Container deployed successfully with ID: ' + d["Id"]})
    elif r.status_code == 404:
        return JsonResponse({'status': 'failed', 'content': 'Deploying the container failed with the following error: '+r.content})
    elif r.status_code == 406:
        return JsonResponse({'status': 'failed', 'content': 'Deploying the container failed with the following error: '+r.content})
    else:
        return JsonResponse({'status': 'failed', 'content': 'Deploying the container failed with the following error: '+r.content})

def StartContainer(request):
    id = request.GET.get('id')

    r = requests.post('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/containers/'+id+'/attach?logs=1&stream=0&stdout=1')
    print r.status_code
    print r.content


    r = requests.post('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/containers/'+id+'/start')
    print r.status_code
    if r.status_code == 204:
        return JsonResponse({'status': 'success', 'content': 'Container Started successfully'})
    elif r.status_code == 304:
        return JsonResponse({'status': 'success', 'content': 'Container already in started state'})
    elif r.status_code == 404:
        return JsonResponse({'status': 'failed', 'content': 'Container already in started state'})
    else:
        return JsonResponse({'status': 'failed', 'content': 'Starting the container failed with the following error: '+r.content})


def AttachContainer(request):
    id = request.GET.get('id')
    r = requests.post('http://ubuntuserver140412-testinstance-jqvgjz92.srv.ravcloud.com:2375/containers/'+id+'/attach?logs=1&stream=0&stdout=1')
    print r.status_code
    print r.content
    if r.status_code == 101:
        return JsonResponse({'status': 'success', 'content': r.content})
    elif r.status_code == 200:
        return JsonResponse({'status': 'success', 'content': r.content})
    elif r.status_code == 404:
        return JsonResponse({'status': 'failed', 'content': r.content})
    else:
        return JsonResponse({'status': 'failed', 'content': 'Killing the container failed with the following error: '+r.content})

def handle_uploaded_file(f):
    print f.name
    filename = f.name +`random.random()` + '.tar.gz'
    path = 'C:\\docker\\' + filename
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path