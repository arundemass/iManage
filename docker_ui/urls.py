#! /usr/bin/env python2.7
"""{{ project_name }} URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from docker_ui.home import views

admin.autodiscover()

urlpatterns = [
    # Homepage
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^Manage/', views.ManageView.as_view()),
    url(r'^Build/', views.BuildView.as_view()),
    url(r'^Deploy/', views.DeployView.as_view()),
    url(r'^Swarm/', views.SwarmView.as_view()),
    url(r'^Nodes/', views.SwarmView.as_view()),
    url(r'^Migrate/', views.MigrateView.as_view()),
    url(r'^Images/', views.ImagesView.as_view()),
    url(r'^VNFCatalog/', views.VNFCatalogView.as_view()),
    url(r'^VNFManager/', views.VNFManagerView.as_view()),
    url(r'^DockerManage/', views.DockerManageView.as_view()),
    url(r'^GetImages/', views.GetImages),
    url(r'^GetContainers/', views.GetContainers),
    url(r'^PullImage/', views.PullImage),
    url(r'^UploadImage/', views.UploadImage),
    url(r'^DeleteImage/', views.DeleteImage),
    url(r'^KillContainer/', views.KillContainer),
    url(r'^DeleteContainer/', views.DeleteContainer),
    url(r'^RunContainer/', views.RunContainer),
    url(r'^StartContainer/', views.StartContainer),
    url(r'^AttachContainer/', views.AttachContainer),
    url(r'^HandleSwarm/', views.HandleSwarm),
    url(r'^GetNodes/', views.GetNodes),
    url(r'^ChangeNode/', views.ChangeNode),
    url(r'^EditNode/', views.EditNode),
    url(r'^DeleteNode/', views.DeleteNode),
    url(r'^AddNode/', views.AddNode),
    url(r'^GetSwarms/', views.GetSwarms),
    url(r'^RemoveSwarmNode/', views.RemoveSwarmNode),
    url(r'^AddSwarmNode/', views.AddSwarmNode),
    url(r'^DeleteSwarm/', views.DeleteSwarm),
    url(r'^listInstances/', views.listInstances),
    url(r'^listHypervisors/', views.listHypervisors),
    url(r'^migrateVM/', views.migrateVM),
    url(r'^ListGlanceImages/', views.ListGlanceImages),
    url(r'^CreateGlanceImage/', views.CreateGlanceImage),
    url(r'^ListVNFCatalogs/', views.ListVNFCatalogs),
    url(r'^ListVNFSCatalogs/', views.ListVNFSCatalogs),
    url(r'^CreateVnfdTemplate/', views.CreateVnfdTemplate),
    url(r'^DeployVnfdTemplate/', views.DeployVnfdTemplate),
    url(r'^TerminateVNF/', views.TerminateVNF),
    url(r'^listEnvironments/', views.listEnvironments),
    url(r'^GetHost/', views.GetHost),
    url(r'^OsHypervisorStats/', views.OsHypervisorStats),
    url(r'^OsHypervisorStatistics/', views.OsHypervisorStatistics),


    url(r'^app_deployment/', include('app_deployment.urls')),


    #url(r'^upload/', views.upload),

    url(r'^admin/', include(admin.site.urls)),
]
