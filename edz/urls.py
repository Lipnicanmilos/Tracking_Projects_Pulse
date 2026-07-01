from django.urls import path
from . import views
from django.conf.urls import handler400, handler403, handler404, handler500
from django.conf.urls.static import static
from django.conf import settings
# from edz.jobs import Command as EdzCommand
# RESET PASSWORD
# from django.contrib.auth.views import (
#     LogoutView, 
#     PasswordResetView, 
#     PasswordResetDoneView, 
#     PasswordResetConfirmView,
#     PasswordResetCompleteView
# )

app_name = 'edz'

urlpatterns = [
    path('edz', views.edz, name='edz'),
    path('connect', views.connect, name='connect'),
    path('jobs', views.jobs, name='jobs'),
    path('users', views.users, name='users'),
    path('pos', views.pos, name='pos'),
    path('send_email', views.send_email, name='send_email'),
    path('bad_trans', views.EDZ_bad_trans, name='EDZ_bad_trans'),
    path('reports_View', views.reports_View, name='reports_View'),
    path('dwh', views.dwh_control, name='dwh'),

    path('sql_podania_edz', views.sql_podania_edz, name='sql_podania_edz'), 
    path('report_edz_crv', views.report_edz_crv, name='report_edz_crv'),
    path('edz_crv_view', views.report_edz_crv_view, name='report_edz_crv_view'),
    path('report_edz_podania_html', views.report_edz_podania_html, name='report_edz_podania_html'),

    

    # report_podania_
    path('sql_crv_edz', views.sql_crv_edz, name='sql_crv_edz'), 
    path('report_edz_podania', views.report_edz_podania, name='report_edz_podania'),

    path('edzdb', views.edzdb, name='edzdb'),
    path('dwhdb', views.dwhdb, name='dwhdb'),
    

    
    


    
    
    # path(r"^edz-scheduler/$", EdzCommand().handle, name='edz-scheduler'),
    
      
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)