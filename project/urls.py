"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from work import views 
from eets import views
from django.views.generic import RedirectView
from django.conf.urls.static import static

from django.core.management.commands.runserver import Command as runserverCommand
#from work.jobs import Command

#scheduler
# from edz.jobs import Command as EdzCommand

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.login_user, name='index'),
    # path('', views.home, name='index'),
    path('', include('work.urls')),
    #path('', include('eets.urls')),
    path('edz/', include('edz.urls')),
    path('eets/', include('eets.urls')),

    # path('eets/', include('django.contrib.auth.urls')),
    path('work/', include('django.contrib.auth.urls')),
    # path(r"^edz-scheduler/$", EdzCommand().handle, name='edz-scheduler'),
    # path('logs/', RedirectView.as_view(url = 'https://fileserver.internal.example.com/billien/CIS/'), name='test'),
] 
handler500 = 'work.views.handler500'
# urlpatterns = patterns('',
# url('file://fileserver.internal.example.com/billien/CIS/', RedirectView.as_view(url='\\fileserver.internal.example.com/billien/CIS/'), name='test')
# )


