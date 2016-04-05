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
    url(r'^Kubernetes/', views.KubernetesView.as_view()),
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
    url(r'^upload/', views.upload),

    url(r'^admin/', include(admin.site.urls)),
]
