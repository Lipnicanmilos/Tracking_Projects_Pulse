from django.urls import path
from . import views
from . import views_ems
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

app_name = 'work'

urlpatterns = [
    # path('', views.main, name='main'),
    path('', views.signin, name='index'),
    path('projects', views.preface, name='preface'),
    path('home', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('hpsm_i', views.hpsm, name='hpsm_i'),
    path('hpsm_c', views.hpsm_c, name='hpsm_c'),

    # LOGGING
    # path('view_log', views.view_log, name='view_log'),
    path('info_log', views.info_log, name='info_log'),




    path('logs', views.logs, name='logs'),
    path('open_all_logs', views.open_all_logs, name='open_all_logs'),
    path('download_acisBO', views.download_acisBO, name='download_acisBO'),
    path('download_bcisBO', views.download_bcisBO, name='download_bcisBO'),
    path('download_acisPOS', views.download_acisPOS, name='download_acisPOS'),
    path('download_bcisPOS', views.download_bcisPOS, name='download_bcisPOS'),
    path('download_acisFCI', views.download_acisFCI, name='download_acisFCI'),
    path('download_bcisFCI', views.download_bcisFCI, name='download_bcisFCI'),
    path('download_acisSC', views.download_acisSC, name='download_acisSC'),
    path('download_bcisSC', views.download_bcisSC, name='download_bcisSC'),
    path('download_acisIS_error', views.download_acisIS_error, name='download_acisIS_error'),
    path('download_bcisIS_error', views.download_bcisIS_error, name='download_bcisIS_error'),
    path('download_acisIS_app', views.download_acisIS_app, name='download_acisIS_app'),
    path('download_bcisIS_app', views.download_bcisIS_app, name='download_bcisIS_app'),
    path('download_acisAPP01_error', views.download_acisAPP01_error, name='download_acisAPP01_error'),
    path('download_acisAPP02_error', views.download_acisAPP02_error, name='download_acisAPP02_error'),
    path('download_acisAPP03_error', views.download_acisAPP03_error, name='download_acisAPP03_error'),
    path('download_acisAPP04_error', views.download_acisAPP04_error, name='download_acisAPP04_error'),
    path('download_bcisAPP01_error', views.download_bcisAPP01_error, name='download_bcisAPP01_error'),
    path('download_bcisAPP02_error', views.download_bcisAPP02_error, name='download_bcisAPP02_error'),
    path('download_bcisAPP03_error', views.download_bcisAPP03_error, name='download_bcisAPP03_error'),
    path('download_bcisAPP04_error', views.download_bcisAPP04_error, name='download_bcisAPP04_error'),
    path('download_acisAPP01_app', views.download_acisAPP01_app, name='download_acisAPP01_app'),
    path('download_acisAPP02_app', views.download_acisAPP02_app, name='download_acisAPP02_app'),
    path('download_acisAPP03_app', views.download_acisAPP03_app, name='download_acisAPP03_app'),
    path('download_acisAPP04_app', views.download_acisAPP04_app, name='download_acisAPP04_app'),
    path('download_bcisAPP01_app', views.download_bcisAPP01_app, name='download_bcisAPP01_app'),
    path('download_bcisAPP02_app', views.download_bcisAPP02_app, name='download_bcisAPP02_app'),
    path('download_bcisAPP03_app', views.download_bcisAPP03_app, name='download_bcisAPP03_app'),
    path('download_bcisAPP04_app', views.download_bcisAPP04_app, name='download_bcisAPP04_app'),

    path('users', views.users, name='users'),
    path('jobs', views.jobs, name='jobs'),

    path('bad_trans', views.bad_trans, name='bad_trans'),
    path('download_DBMS', views.download_DBMS, name='download_DBMS'),
    
    path('bo_log', views.bo_log, name='bo_log'),

    path('awr', views.awr, name='awr'),
    path('open_awr', views.open_awr, name='open_awr'),

    # path('dwh_control', views.dwh_control, name='dwh_control'),
    path('dwh_loading', views.dwh_loading, name='dwh_loading'),
    
    path('bd_ack', views.bd_ack, name='bd_ack'),
    path('wl_bl', views.wl_bl, name='wl_bl'),
    path('obu_event', views.obu_event, name='obu_event'),

    
    path('sc_login', views.sc_login, name='sc_login'),
    path('val_test', views.val_test, name='val_test'),

    path('cisdb', views.cisdb, name='cisdb'),
    path('dwhdb', views.dwhdb, name='dwhdb'),

    # EMS PATH
    path('home_ems', views_ems.home_ems, name='home_ems'),
    path('validation', views_ems.validacia, name='validation'),
    path('reports_View', views_ems.reports_View, name='reports_View'),
    path('jobs_ems', views_ems.jobs_ems, name='jobs_ems'),
    path('EMS_bd_ack', views_ems.EMS_bd_ack, name='EMS_bd_ack'),
    path('EMS_bad_trans', views_ems.EMS_bad_trans, name='EMS_bad_trans'),
    path('pos', views_ems.pos_user, name='pos'),
    path('paywell', views_ems.paywell, name='paywell'),
    path('paywell/download/<str:filename>/', views_ems.download_sql, name='download_sql'),
    path('paywell/download-log/', views_ems.download_auto_log, name='download_auto_log'),
    path('inactivity', views_ems.inactivity, name='inactivity'),
    path('download_inactivity_file/<path:relative_path>/', views_ems.download_inactivity_file, name='download_inactivity_file'),
    
    #EMS ICT DPH
    path('ict_dph', views_ems.ict_dph, name='ict_dph'),
    
    path('download-log/', views_ems.download_log, name='download_log'),

    path('daily_rep', views_ems.daily_rep, name='daily_rep'),
    path('download_daily_file/<path:relative_path>/', views_ems.download_daily_file, name='download_daily_file'),
  

    path('download_daily_log/', views_ems.download_log_daily, name='daily_auto_log'),

    



       


    # EMS LOGS
    path('ems_logs', views_ems.ems_logs, name='ems_logs'),
    path('EMSAAPP01_realtime_error', views_ems.EMSAAPP01_realtime_error, name='EMSAAPP01_realtime_error'), 
    path('EMSAAPP01_realtime_app', views_ems.EMSAAPP01_realtime_app, name='EMSAAPP01_realtime_app'), 
    path('EMSAAPP02_realtime_error', views_ems.EMSAAPP02_realtime_error, name='EMSAAPP02_realtime_error'), 
    path('EMSAAPP02_realtime_app', views_ems.EMSAAPP02_realtime_app, name='EMSAAPP02_realtime_app'), 
    path('EMSBAPP01_realtime_error', views_ems.EMSBAPP01_realtime_error, name='EMSBAPP01_realtime_error'), 
    path('EMSBAPP01_realtime_app', views_ems.EMSBAPP01_realtime_app, name='EMSBAPP01_realtime_app'), 
    path('EMSBAPP02_realtime_error', views_ems.EMSBAPP02_realtime_error, name='EMSBAPP02_realtime_error'), 
    path('EMSBAPP02_realtime_app', views_ems.EMSBAPP02_realtime_app, name='EMSBAPP02_realtime_app'), 
    path('EMSCAPP01_realtime_error', views_ems.EMSCAPP01_realtime_error, name='EMSCAPP01_realtime_error'), 
    path('EMSCAPP01_realtime_app', views_ems.EMSCAPP01_realtime_app, name='EMSCAPP01_realtime_app'), 
    path('EMSCAPP02_realtime_error', views_ems.EMSCAPP02_realtime_error, name='EMSCAPP02_realtime_error'), 
    path('EMSCAPP02_realtime_app', views_ems.EMSCAPP02_realtime_app, name='EMSCAPP02_realtime_app'), 
    path('EMSDAPP01_realtime_error', views_ems.EMSDAPP01_realtime_error, name='EMSDAPP01_realtime_error'), 
    path('EMSDAPP01_realtime_app', views_ems.EMSDAPP01_realtime_app, name='EMSDAPP01_realtime_app'), 
    path('EMSDAPP02_realtime_error', views_ems.EMSDAPP02_realtime_error, name='EMSDAPP02_realtime_error'), 
    path('EMSDAPP02_realtime_app', views_ems.EMSDAPP02_realtime_app, name='EMSDAPP02_realtime_app'), 
    path('EMSISAPP01_realtime_error', views_ems.EMSISAPP01_realtime_error, name='EMSISAPP01_realtime_error'), 
    path('EMSISAPP01_realtime_app', views_ems.EMSISAPP01_realtime_app, name='EMSISAPP01_realtime_app'),     
    path('EMSISAPP02_realtime_error', views_ems.EMSISAPP02_realtime_error, name='EMSISAPP02_realtime_error'), 
    path('EMSISAPP02_realtime_app', views_ems.EMSISAPP02_realtime_app, name='EMSISAPP02_realtime_app'), 

    path('EMSAWEB01_bo_realtime_web', views_ems.EMSAWEB01_bo_realtime_web, name='EMSAWEB01_bo_realtime_web'), 
    path('EMSAWEB02_bo_realtime_web', views_ems.EMSAWEB02_bo_realtime_web, name='EMSAWEB02_bo_realtime_web'), 
    path('EMSAWEB01_pos_realtime_web', views_ems.EMSAWEB01_pos_realtime_web, name='EMSAWEB01_pos_realtime_web'), 
    path('EMSAWEB02_pos_realtime_web', views_ems.EMSAWEB02_pos_realtime_web, name='EMSAWEB02_pos_realtime_web'), 
    path('EMSAWEB01_cr_realtime_web', views_ems.EMSAWEB01_cr_realtime_web, name='EMSAWEB01_cr_realtime_web'), 
    path('EMSAWEB02_cr_realtime_web', views_ems.EMSAWEB02_cr_realtime_web, name='EMSAWEB02_cr_realtime_web'), 
    path('EMSAWEB01_fci_realtime_web', views_ems.EMSAWEB01_fci_realtime_web, name='EMSAWEB01_fci_realtime_web'), 
    path('EMSAWEB02_fci_realtime_web', views_ems.EMSAWEB02_fci_realtime_web, name='EMSAWEB02_fci_realtime_web'), 
    path('EMSAWEB01_sc_realtime_web', views_ems.EMSAWEB01_sc_realtime_web, name='EMSAWEB01_sc_realtime_web'), 
    path('EMSAWEB02_sc_realtime_web', views_ems.EMSAWEB02_sc_realtime_web, name='EMSAWEB02_sc_realtime_web'), 

    # reports BILLDB
    path('sql_Invoices', views_ems.sql_Invoices, name='sql_Invoices'), 

    path('sql_INACTIVITY_4M', views_ems.sql_INACTIVITY_4M, name='sql_INACTIVITY_4M'), 

    path('sql_INACTIVITY_6M_PRP', views_ems.sql_INACTIVITY_6M_PRP, name='sql_INACTIVITY_6M_PRP'), 
    
    path('sql_Vyrubene_myto_kategorie', views_ems.sql_Vyrubene_myto_kategorie, name='sql_Vyrubene_myto_kategorie'), 

    path('sql_Vyrubene_myto_krajiny', views_ems.sql_Vyrubene_myto_krajiny, name='sql_Vyrubene_myto_krajiny'), 

    path('rms', views_ems.report_Mark_stat, name='rms'), 
 

    
    path('test', views.test, name='test'), 
    
    path('marketing_stats_view', views_ems.marketing_stats_view, name='marketing_stats_view'),
    path('generate_pdf', views_ems.generate_pdf, name='generate_pdf'),
    path('generate_report', views_ems.generate_report, name='generate_report'),
    path('render_pdf_view', views_ems.render_pdf_view, name='render_pdf_view'),

    #lego report ems
    path('lego_rep_CRM', views_ems.lego_rep_CRM, name='lego_rep_CRM'),
    # DWH dwh_control
    path('DWH', views_ems.dwh_control, name='dwh'),



    

    
    
    
    
    
    

   
    # SQL PATH


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



# from django.conf.urls import (handler403, handler404, handler500)

# handler500 = 'work.views.profil'


    