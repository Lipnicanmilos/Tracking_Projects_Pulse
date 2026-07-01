from django.urls import path
from . import views, views_scheduler
from django.conf.urls import handler400, handler403, handler404, handler500
from django.conf.urls.static import static
from django.conf import settings
# RESET PASSWORD
# from django.contrib.auth.views import (
#     LogoutView, 
#     PasswordResetView, 
#     PasswordResetDoneView, 
#     PasswordResetConfirmView,
#     PasswordResetCompleteView
# )

app_name = 'eets'

urlpatterns = [
    # TC
    path('eets', views.eets, name='eets'),
    path('bd_ack', views.bd_ack, name='bd_ack'),
    path('rte', views.eets_rte, name='rte'),
    path('whitelist', views.wl_ack, name='wl_ack'),
    path('blacklist', views.bl_ack, name='bl_ack'),
    path('jobs', views.jobs, name='jobs'),
    path('rating', views.tc_rating, name='rating'),
    path('td_preparation', views.td_preparation, name='td_preparation'),
    path('awr', views.awr, name='awr'),
        
    # saida
    path('saidamd_front', views.saidamd_fronts, name='saidamd_front'),
    #proxy
    path('proxy_section', views.proxy_section, name='proxy_section'),

    path('dwh', views.dwh_control, name='dwh'), 


    path('eetsdb', views.eetsdb, name='eetsdb'),
    path('dwhdb', views.dwhdb, name='dwhdb'),

    path('reports_view', views.reports_View, name='reports_view'),
    path('rating_view', views_scheduler.report_eets_rating_html, name='rating_view'),
    path('obe_positions', views_scheduler.job_eets_obe_pos_html, name='obe_positions'),

    #jira
    path('jira/issues/', views.get_jira_issues, name='get_jira_issues'),
    path('jira/issues_all/', views.get_jira_emsw, name='get_jira_emsw'),
   


    #LEGO report
    path('DB_USER', views.dwh_rep_CRM, name='DB_USER'),
    # LEGO edit job
    path('eets_lego', views.report_eets_lego_html, name='eets_lego'),
    #    

    
    
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)