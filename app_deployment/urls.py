from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),   
    url(r'^$', views.IndexView.as_view()),  
    url(r'^index/', views.IndexView.as_view()),    
    url(r'^installSoftwares/', views.installSoftwares), 
    url(r'^getDeployInfo/', views.getDeployInfo),  
    url(r'^indexnew/', views.getindexnew), 
    
    #url(r'^test_fn/', views.test_fn),
    #url(r'^test_pkg/', views.test_pkg),
    url(r'^getPackages/', views.getPackages),
    url(r'^uploadFiles/', views.uploadFiles),
     url(r'^createCustomPackage/', views.createCustomPackage),
     
    
       
    
]