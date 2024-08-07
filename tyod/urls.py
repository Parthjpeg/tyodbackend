"""
URL configuration for tyod project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import *
from api.tvsmviews import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', chat),
    path('uploadfile/' , uploadfile),
    path('getchatnames/',getchatnames),
    path('getfilenames/',getfilenames),
    path('getchathistory/',getchathistory),
    path('searchxls/' , searchxls),
    path('deletechat/', deletechat),
    path('renamechat/',renamechat),
    path('addprod/' , Add_product),
    path('tvsmchat/' , tvsmchat),
    path('testfile/' , fileresptest),
    path('audiotobs64/' , audiotobs64),
    path('bs64toaudio/' , bs64toaudio),
    path('addaccessories/', Add_Tvsm_Accessories),
    path('chattvsmaccessories/' , chatAccessories),
    path('jsoncheck/' , jsontest)
]
