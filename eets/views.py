from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EETSDB, SAIDAMDDB, PROXYDB
from django.contrib import messages

from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import *
from work.models import EMS_DWHDB
from work.forms import EMSDWHDBUpdateForm

import os
import glob

import logging
logger = logging.getLogger('my_app')

from django.contrib import messages

########### lego report code
import codecs
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from dateutil.relativedelta import relativedelta
from django.core.files import File

import json
#########################
#### EMAIL ####
from django.core.mail import EmailMessage
#######

import cx_Oracle
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
# Create your views here.

@login_required
def eets(request):
    eets_db=EETSDB.objects.get(user=request.user)
    form_eets = EETSDBUpdateForm(request.POST, instance=eets_db)
    
    ems_dwh_db=EMS_DWHDB.objects.get(user=request.user)
    form_ems_dwh = EMSDWHDBUpdateForm(request.POST or None, instance=ems_dwh_db)
    
    saidamd_db=SAIDAMDDB.objects.get(user=request.user)
    form_saidamd = SAIDAMDDBUpdateForm(request.POST, instance=saidamd_db)

    proxy_db=PROXYDB.objects.get(user=request.user)
    form_proxydb = PROXYDBUpdateForm(request.POST, instance=proxy_db)
           
    if form_eets.is_valid():
        form_eets.save()
        messages.success(request,'Your Profile has been updated!')
        form_eets = EETSDBUpdateForm(instance=eets_db)
    else:
        form_eets = EETSDBUpdateForm(instance=eets_db)

    if form_ems_dwh.is_valid():
        form_ems_dwh.save()
        messages.success(request,'Your Profile has been updated!')
        form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)
    else:
        form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)
    
    if form_saidamd.is_valid():
        form_saidamd.save()
        messages.success(request,'Your Profile has been updated!')
        form_saidamd = SAIDAMDDBUpdateForm(instance=saidamd_db)
    else:
        form_saidamd = SAIDAMDDBUpdateForm(instance=saidamd_db)

    if form_proxydb.is_valid():
        form_proxydb.save()
        messages.success(request,'Your Profile has been updated!')
        form_proxydb = PROXYDBUpdateForm(instance=proxy_db)
    else:
        form_proxydb = PROXYDBUpdateForm(instance=proxy_db)

    context = { 'form_eets':form_eets, 'key': 'value', 'form_ems_dwh':form_ems_dwh, 'form_saidamd':form_saidamd, 'form_proxydb':form_proxydb}

    return render(request, 'eets/base.html', context)

@login_required
def bd_ack(request):
    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()

    sql_ack_None = """
                SELECT
                        *
                    FROM
                        (
                            SELECT
                            bd.eets_provider_id as eets_provider_id,
                            bds.ede_log_status_name,
                                bd.ede_log_id           AS bd_ede_log_id,
                                bd.integration_log_id   AS bd_integration_log_id,
                                bd.ede_log_status_code
                                || '-'
                                || bds.ede_log_status_name AS bd_ede_log_status,
                                bd.ede_message_type_code || '-' ||  msl.EDE_MESSAGE_TYPE_NAME AS BD_EDE_MESSAGE_TYPE,
                                bd.eets_provider_id
                                || '-'
                                || p.provider_number
                                || '-'
                                || p.provider_abbreviation AS eets_provider,
                                TO_CHAR(bd.apdu_identifier) AS apdu_identifier,
                                DELIVERY_COUNTER,
                                TO_CHAR(from_tz(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_created_on,
                                TO_CHAR(from_tz(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_exported_on,
                                TO_CHAR(from_tz(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS ack_created_on,
                                /*CAST(ack.created_on AS TIMESTAMP) - CAST(bd.created_on AS TIMESTAMP) AS diff,*/
                                Round((ack.created_on - bd.created_on) * 24,1) as diff_hours,
                                Round((ack.created_on - bd.created_on) * 24 * 60,1) as diff_minutes,
                                Round((ack.created_on - bd.created_on) * 24 * 60 * 60,1) as diff_seconds
                            FROM
                                EETS_ede.ede_log            bd
                                JOIN EETS_ede.ede_log_status_l   bds ON bd.ede_log_status_code = bds.ede_log_status_code AND bds.language_code = 'SK'
                                JOIN EETS_ecm.eets_provider      p ON bd.eets_provider_id = p.eets_provider_id
                                LEFT JOIN EETS_ede.ede_log            ack ON bd.ede_log_id = ack.referred_ede_log_id AND ack.ede_message_type_code = 1 AND ack.ede_log_status_code = 1
                                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on bd.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                                /*DELIVERY_COUNTER*/
                                left join EETS_EDE.EDE_LOG lg on bd.EDE_LOG_ID=lg.EDE_LOG_ID
                                LEFT JOIN  EETS_EDE.EDE_EXPORT ex on ex.EDE_LOG_ID=lg.EDE_LOG_ID
                            WHERE
                                bd.ede_message_type_code = 4 and bds.ede_log_status_name!='Úspešne spracované' and bd.created_on >= trunc(sysdate-7)
                                or bd.ede_message_type_code = 4 and  ack.created_on is null and bd.created_on >= trunc(sysdate-7)
                        )
                    ORDER BY
                        BD_EDE_LOG_ID DESC
              """
    cursor.execute(sql_ack_None)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
    ack_None = dictfetchall(cursor)
    # print(ack_None)
    

    x = None
    y = None
    
    if 'x' in request.GET and request.GET['y'] =='':
        
        x = request.GET['x']
        y = request.GET['y']

        sql_x="""
            SELECT
                        *
                    FROM
                        (
                            SELECT
                            bd.eets_provider_id as eets_provider_id,
                                bds.ede_log_status_name,
                                bd.ede_log_id           AS bd_ede_log_id,
                                bd.integration_log_id   AS bd_integration_log_id,
                                bd.ede_log_status_code
                                || '-'
                                || bds.ede_log_status_name AS bd_ede_log_status,
                                bd.ede_message_type_code
                                || '-'
                                || msl.ede_message_type_name AS bd_ede_message_type,
                                bd.eets_provider_id
                                || '-'
                                || p.provider_number
                                || '-'
                                || p.provider_abbreviation AS eets_provider,
                                TO_CHAR(bd.apdu_identifier) AS apdu_identifier,
                                DELIVERY_COUNTER,
                                TO_CHAR(from_tz(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_created_on
                                ,
                                TO_CHAR(from_tz(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_exported_on
                                ,
                                TO_CHAR(from_tz(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS ack_created_on
                                , /*CAST(ack.created_on AS TIMESTAMP) - CAST(bd.created_on AS TIMESTAMP) AS diff,*/
                                round((ack.created_on - bd.created_on) * 24, 1) AS diff_hours,
                                round((ack.created_on - bd.created_on) * 24 * 60, 1) AS diff_minutes,
                                round((ack.created_on - bd.created_on) * 24 * 60 * 60, 1) AS diff_seconds
                            FROM
                                eets_ede.ede_log              bd
                                JOIN eets_ede.ede_log_status_l     bds ON bd.ede_log_status_code = bds.ede_log_status_code
                                                                    AND bds.language_code = 'SK'
                                JOIN eets_ecm.eets_provider        p ON bd.eets_provider_id = p.eets_provider_id
                                LEFT JOIN eets_ede.ede_log              ack ON bd.ede_log_id = ack.referred_ede_log_id
                                                                AND ack.ede_message_type_code = 1
                                                                AND ack.ede_log_status_code = 1
                                LEFT JOIN eets_ede.ede_message_type_l   msl ON bd.ede_message_type_code = msl.ede_message_type_code
                                                                            AND msl.language_code = 'SK'
                                                                /*DELIVERY_COUNTER*/
                                left join EETS_EDE.EDE_LOG lg on bd.EDE_LOG_ID=lg.EDE_LOG_ID
                                LEFT JOIN  EETS_EDE.EDE_EXPORT ex on ex.EDE_LOG_ID=lg.EDE_LOG_ID
                            WHERE
                                bd.ede_message_type_code = 4
                                AND bd.created_on >= to_date(:id, 'DD-MM-YYYY HH24:MI:SS')
                        )
                    ORDER BY
                        bd_ede_log_id DESC
        """
 
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_x, id=x)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
            
    
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_y="""
            SELECT
                        *
                    FROM
                        (
                            SELECT
                            bd.eets_provider_id as eets_provider_id,
                                bds.ede_log_status_name,
                                bd.ede_log_id           AS bd_ede_log_id,
                                bd.integration_log_id   AS bd_integration_log_id,
                                bd.ede_log_status_code
                                || '-'
                                || bds.ede_log_status_name AS bd_ede_log_status,
                                bd.ede_message_type_code
                                || '-'
                                || msl.ede_message_type_name AS bd_ede_message_type,
                                bd.eets_provider_id
                                || '-'
                                || p.provider_number
                                || '-'
                                || p.provider_abbreviation AS eets_provider,
                                TO_CHAR(bd.apdu_identifier) AS apdu_identifier,
                                DELIVERY_COUNTER,
                                TO_CHAR(from_tz(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_created_on
                                ,
                                TO_CHAR(from_tz(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_exported_on
                                ,
                                TO_CHAR(from_tz(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS ack_created_on
                                , /*CAST(ack.created_on AS TIMESTAMP) - CAST(bd.created_on AS TIMESTAMP) AS diff,*/
                                round((ack.created_on - bd.created_on) * 24, 1) AS diff_hours,
                                round((ack.created_on - bd.created_on) * 24 * 60, 1) AS diff_minutes,
                                round((ack.created_on - bd.created_on) * 24 * 60 * 60, 1) AS diff_seconds
                            FROM
                                eets_ede.ede_log              bd
                                JOIN eets_ede.ede_log_status_l     bds ON bd.ede_log_status_code = bds.ede_log_status_code
                                                                    AND bds.language_code = 'SK'
                                JOIN eets_ecm.eets_provider        p ON bd.eets_provider_id = p.eets_provider_id
                                LEFT JOIN eets_ede.ede_log              ack ON bd.ede_log_id = ack.referred_ede_log_id
                                                                AND ack.ede_message_type_code = 1
                                                                AND ack.ede_log_status_code = 1
                                LEFT JOIN eets_ede.ede_message_type_l   msl ON bd.ede_message_type_code = msl.ede_message_type_code
                                                                            AND msl.language_code = 'SK'
                                                                /*DELIVERY_COUNTER*/
                                left join EETS_EDE.EDE_LOG lg on bd.EDE_LOG_ID=lg.EDE_LOG_ID
                                LEFT JOIN  EETS_EDE.EDE_EXPORT ex on ex.EDE_LOG_ID=lg.EDE_LOG_ID
                            WHERE
                                bd.ede_message_type_code = 4
                                AND bd.created_on <= to_date(:id, 'DD-MM-YYYY HH24:MI:SS')
                        )
                    ORDER BY
                        bd_ede_log_id DESC
        """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_y, id=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
            SELECT
                        *
                    FROM
                        (
                            SELECT
                            bd.eets_provider_id as eets_provider_id,
                                bds.ede_log_status_name,
                                bd.ede_log_id           AS bd_ede_log_id,
                                bd.integration_log_id   AS bd_integration_log_id,
                                bd.ede_log_status_code
                                || '-'
                                || bds.ede_log_status_name AS bd_ede_log_status,
                                bd.ede_message_type_code
                                || '-'
                                || msl.ede_message_type_name AS bd_ede_message_type,
                                bd.eets_provider_id
                                || '-'
                                || p.provider_number
                                || '-'
                                || p.provider_abbreviation AS eets_provider,
                                TO_CHAR(bd.apdu_identifier) AS apdu_identifier,
                                DELIVERY_COUNTER,
                                TO_CHAR(from_tz(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_created_on
                                ,
                                TO_CHAR(from_tz(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_exported_on
                                ,
                                TO_CHAR(from_tz(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS ack_created_on
                                , /*CAST(ack.created_on AS TIMESTAMP) - CAST(bd.created_on AS TIMESTAMP) AS diff,*/
                                round((ack.created_on - bd.created_on) * 24, 1) AS diff_hours,
                                round((ack.created_on - bd.created_on) * 24 * 60, 1) AS diff_minutes,
                                round((ack.created_on - bd.created_on) * 24 * 60 * 60, 1) AS diff_seconds
                            FROM
                                eets_ede.ede_log              bd
                                JOIN eets_ede.ede_log_status_l     bds ON bd.ede_log_status_code = bds.ede_log_status_code
                                                                    AND bds.language_code = 'SK'
                                JOIN eets_ecm.eets_provider        p ON bd.eets_provider_id = p.eets_provider_id
                                LEFT JOIN eets_ede.ede_log              ack ON bd.ede_log_id = ack.referred_ede_log_id
                                                                AND ack.ede_message_type_code = 1
                                                                AND ack.ede_log_status_code = 1
                                LEFT JOIN eets_ede.ede_message_type_l   msl ON bd.ede_message_type_code = msl.ede_message_type_code
                                                                            AND msl.language_code = 'SK'
                                                                /*DELIVERY_COUNTER*/
                                left join EETS_EDE.EDE_LOG lg on bd.EDE_LOG_ID=lg.EDE_LOG_ID
                                LEFT JOIN  EETS_EDE.EDE_EXPORT ex on ex.EDE_LOG_ID=lg.EDE_LOG_ID
                            WHERE
                                bd.ede_message_type_code = 4
                                AND 
                                bd.created_on >= to_date(:id_x, 'DD-MM-YYYY HH24:MI:SS')
                                AND
                                bd.created_on <= to_date(:id_y, 'DD-MM-YYYY HH24:MI:SS')
                        )
                    ORDER BY
                        bd_ede_log_id DESC
        """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_xy, id_x=x, id_y=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
    else:
        sql_ack = """
                SELECT
                        *
                    FROM
                        (
                            SELECT
                            bd.eets_provider_id as eets_provider_id,
                            bds.ede_log_status_name,
                                bd.ede_log_id           AS bd_ede_log_id,
                                bd.integration_log_id   AS bd_integration_log_id,
                                bd.ede_log_status_code
                                || '-'
                                || bds.ede_log_status_name AS bd_ede_log_status,
                                bd.ede_message_type_code || '-' ||  msl.EDE_MESSAGE_TYPE_NAME AS BD_EDE_MESSAGE_TYPE,
                                bd.eets_provider_id
                                || '-'
                                || p.provider_number
                                || '-'
                                || p.provider_abbreviation AS eets_provider,
                                TO_CHAR(bd.apdu_identifier) AS apdu_identifier,
                                DELIVERY_COUNTER,
                                TO_CHAR(from_tz(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_created_on,
                                TO_CHAR(from_tz(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS bd_exported_on,
                                TO_CHAR(from_tz(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS ack_created_on,
                                /*CAST(ack.created_on AS TIMESTAMP) - CAST(bd.created_on AS TIMESTAMP) AS diff,*/
                                Round((ack.created_on - bd.created_on) * 24,1) as diff_hours,
                                Round((ack.created_on - bd.created_on) * 24 * 60,1) as diff_minutes,
                                Round((ack.created_on - bd.created_on) * 24 * 60 * 60,1) as diff_seconds
                            FROM
                                EETS_ede.ede_log            bd
                                JOIN EETS_ede.ede_log_status_l   bds ON bd.ede_log_status_code = bds.ede_log_status_code AND bds.language_code = 'SK'
                                JOIN EETS_ecm.eets_provider      p ON bd.eets_provider_id = p.eets_provider_id
                                LEFT JOIN EETS_ede.ede_log            ack ON bd.ede_log_id = ack.referred_ede_log_id AND ack.ede_message_type_code = 1 AND ack.ede_log_status_code = 1
                                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on bd.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                                                                /*DELIVERY_COUNTER*/
                                left join EETS_EDE.EDE_LOG lg on bd.EDE_LOG_ID=lg.EDE_LOG_ID
                                LEFT JOIN  EETS_EDE.EDE_EXPORT ex on ex.EDE_LOG_ID=lg.EDE_LOG_ID
                            WHERE
                                bd.ede_message_type_code = 4 
                                and bd.created_on >= trunc(sysdate-7)
                        )
                    ORDER BY
                        BD_EDE_LOG_ID DESC
              """
        with con_EETSDB_STDBY.cursor() as cursor:
            cursor.execute(sql_ack)
            ack = dictfetchall(cursor)

    context = {'ack':ack, 'ack_None':ack_None}
    return render(request, 'eets/bd_ack.html', context)

@login_required
def wl_ack(request):
    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()

    sql_ack_None = """
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                    TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER 
                where exl.EXCEPTION_LIST_TYPE_CODE=1 and il.EETS_INT_LOG_STATUS_NAME!='Spracovaný' and STARTED_ON >= trunc(sysdate-7)
                or
                exl.EXCEPTION_LIST_TYPE_CODE=1 and ACK_FILE_CREATED_ON is null and STARTED_ON >= trunc(sysdate-7)
                order by EETS_INTEGRATION_LOG_ITEM_ID desc
              """
    cursor.execute(sql_ack_None)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
    ack_None = dictfetchall(cursor)

    x = None
    y = None
    
    if 'x' in request.GET and request.GET['y'] =='':
        
        x = request.GET['x']
        y = request.GET['y']

        sql_x="""
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                    TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER
                where ite.EDE_MESSAGE_TYPE_CODE=2
                AND ACK_FILE_CREATED_ON >= to_date(:id, 'DD-MM-YYYY HH24:MI:SS')
                order by EETS_INTEGRATION_LOG_ITEM_ID desc    
                """
 
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_x, id=x)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
            
    
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_y="""
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                    TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER
                where ite.EDE_MESSAGE_TYPE_CODE=2 
                AND ACK_FILE_CREATED_ON <= to_date(:id, 'DD-MM-YYYY HH24:MI:SS')
                order by EETS_INTEGRATION_LOG_ITEM_ID desc  
        """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_y, id=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                    TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                    round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER
                where ite.EDE_MESSAGE_TYPE_CODE=2
                AND ACK_FILE_CREATED_ON >= to_date(:id_x, 'DD-MM-YYYY HH24:MI:SS')
                AND ACK_FILE_CREATED_ON <= to_date(:id_y, 'DD-MM-YYYY HH24:MI:SS')
                order by EETS_INTEGRATION_LOG_ITEM_ID desc  

        """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_xy, id_x=x, id_y=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
    else:
        sql_ack = """
                SELECT
                    eets_integration_log_item_id,
                    ite.integration_log_id,
                    VERSION, 
                    il.eets_int_log_status_code
                    || '-'
                    || il.eets_int_log_status_name AS eets_int_log_status,
                    msl.ede_message_type_code
                    || '-'
                    || msl.ede_message_type_name AS ede_message,
                    exl.exception_list_type_code
                    || '-'
                    || exl.exception_list_type_name AS exception_list,
                    ite.eets_provider_id
                    || '-'
                    || p.provider_number
                    || '-'
                    || p.provider_abbreviation AS provider,
                    TO_CHAR(from_tz(CAST(exception_list_valid_from AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS exception_list_valid_from
                    ,
                    TO_CHAR(from_tz(CAST(exception_list_valid_to AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS exception_list_valid_to
                    ,
                    TO_CHAR(from_tz(CAST(started_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS started_on,
                    log_file_created_on,
                    TO_CHAR(from_tz(CAST(ack_file_created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS ack_file_created_on
                    ,
                    TO_CHAR(from_tz(CAST(process_date_time AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS process_date_time
                    ,
                    CAST(ack_file_created_on AS TIMESTAMP) - CAST(started_on AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                    TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                    round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM
                    eets_ecm.eets_integration_log_item   ite
                    LEFT JOIN eets_ecm.eets_int_log_status_l       il ON ite.eets_il_status_code = il.eets_int_log_status_code
                                                                AND il.language_code = 'SK'
                    LEFT JOIN eets_ecm.exception_list_type_l       exl ON ite.exception_list_type_code = exl.exception_list_type_code
                                                                    AND exl.language_code = 'SK'
                    LEFT JOIN eets_ede.ede_message_type_l          msl ON ite.ede_message_type_code = msl.ede_message_type_code
                                                                AND msl.language_code = 'SK'
                    LEFT JOIN eets_ecm.eets_provider               p ON ite.eets_provider_id = p.eets_provider_id
                    LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER
                 WHERE
                    exl.exception_list_type_code = 1
                    AND started_on >= ( SYSDATE - 7 )
                ORDER BY
                    eets_integration_log_item_id DESC   
              """
        with con_EETSDB_STDBY.cursor() as cursor:
            cursor.execute(sql_ack)
            ack = dictfetchall(cursor)

    context = {'ack':ack, 'ack_None':ack_None}
    return render(request, 'eets/wl_bl_ack.html', context)

@login_required
def bl_ack(request):
    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()

    sql_ack_None = """
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                    TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER 
                where ite.EDE_MESSAGE_TYPE_CODE=3 and il.EETS_INT_LOG_STATUS_NAME!='Spracovaný' and STARTED_ON >= trunc(sysdate-7)
                or
                ite.EDE_MESSAGE_TYPE_CODE=3 and ACK_FILE_CREATED_ON is null and STARTED_ON >= trunc(sysdate-7)
                order by EETS_INTEGRATION_LOG_ITEM_ID desc
              """
    cursor.execute(sql_ack_None)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
    ack_None = dictfetchall(cursor)

    x = None
    y = None
    
    if 'x' in request.GET and request.GET['y'] =='':
        
        x = request.GET['x']
        y = request.GET['y']

        sql_x="""
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER 
                where ite.EDE_MESSAGE_TYPE_CODE=3
                AND ACK_FILE_CREATED_ON >= to_date(:id, 'DD-MM-YYYY HH24:MI:SS')
                order by EETS_INTEGRATION_LOG_ITEM_ID desc    
                """
 
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_x, id=x)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
            
    
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_y="""
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER 
                where ite.EDE_MESSAGE_TYPE_CODE=3 
                AND ACK_FILE_CREATED_ON <= to_date(:id, 'DD-MM-YYYY HH24:MI:SS')
                order by EETS_INTEGRATION_LOG_ITEM_ID desc  
        """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_y, id=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER 
                where ite.EDE_MESSAGE_TYPE_CODE=3
                AND ACK_FILE_CREATED_ON >= to_date(:id_x, 'DD-MM-YYYY HH24:MI:SS')
                AND ACK_FILE_CREATED_ON <= to_date(:id_y, 'DD-MM-YYYY HH24:MI:SS')
                order by EETS_INTEGRATION_LOG_ITEM_ID desc  

        """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_xy, id_x=x, id_y=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
    else:
        sql_ack = """
                Select EETS_INTEGRATION_LOG_ITEM_ID, ite.INTEGRATION_LOG_ID, VERSION, il.EETS_INT_LOG_STATUS_CODE || '-' || il.EETS_INT_LOG_STATUS_NAME as EETS_INT_LOG_STATUS,
                msl.EDE_MESSAGE_TYPE_CODE || '-' || msl.EDE_MESSAGE_TYPE_NAME as EDE_MESSAGE,
                exl.EXCEPTION_LIST_TYPE_CODE || '-' || exl.EXCEPTION_LIST_TYPE_NAME as EXCEPTION_LIST,
                ite.EETS_PROVIDER_ID as PROVIDER_ID,
                ite.EETS_PROVIDER_ID || '-' || p.PROVIDER_NUMBER || '-' || p.PROVIDER_ABBREVIATION as PROVIDER,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_FROM,
                TO_CHAR(from_tz(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as EXCEPTION_LIST_VALID_TO,
                TO_CHAR(from_tz(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as STARTED_ON,      
                LOG_FILE_CREATED_ON, 
                TO_CHAR(from_tz(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as ACK_FILE_CREATED_ON,
                TO_CHAR(from_tz(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') as PROCESS_DATE_TIME,
                CAST(ACK_FILE_CREATED_ON AS TIMESTAMP) - CAST(STARTED_ON AS TIMESTAMP) AS "diff_seconds Create and ACK",
                    --round((ack_file_created_on - started_on) * 24, 1) AS diff_hours,
                    --round((ack_file_created_on - started_on) * 24 * 60, 1) AS diff_minutes,
                    --round((ack_file_created_on - started_on) * 24 * 60 * 60, 1) AS diff_seconds,
                    ite.MESSAGE_NUMBER, APDU_IDENTIFIER,
                TO_CHAR(from_tz(CAST(EXPORTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD-MM-YYYY HH24:MI:SS') AS EXPORTED_ON,
                round((EXPORTED_ON - started_on) * 24 * 60, 1) AS diff_minutes
                FROM EETS_ECM.EETS_INTEGRATION_LOG_ITEM ite 
                LEFT JOIN eets_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'SK'
                LEFT JOIN eets_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND exl.language_code = 'SK'
                LEFT JOIN EETS_ede.EDE_MESSAGE_TYPE_L msl on ite.EDE_MESSAGE_TYPE_CODE=msl.EDE_MESSAGE_TYPE_CODE and msl.LANGUAGE_CODE='SK'
                LEFT JOIN EETS_ecm.eets_provider p ON ite.eets_provider_id = p.eets_provider_id 
                LEFT JOIN eets_ede.ede_log ack on  ite.MESSAGE_NUMBER =ack.IN_RESPONSE_TO_APDU_IDENTIFIER 
                where ite.EDE_MESSAGE_TYPE_CODE=3
                and STARTED_ON >= trunc(sysdate-7)
                order by EETS_INTEGRATION_LOG_ITEM_ID desc
              """
        with con_EETSDB_STDBY.cursor() as cursor:
            cursor.execute(sql_ack)
            ack = dictfetchall(cursor)

    context = {'ack':ack, 'ack_None':ack_None}
    return render(request, 'eets/wl_bl_ack.html', context)

@login_required
def jobs(request):
    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()

    
    job_s = ''
    # print('vysledok: '+job_s)\
    q = None

    sql_job = """SELECT * FROM(
                    SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME,
                    EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS
                    FROM eets_CO.JOB_INSTANCE ji
                    left join eets_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                    left join eets_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
                    where
                    exs.LANGUAGE_CODE='SK' and START_ACTION_DATETIME >= trunc(sysdate-3)
                                   --and ji.SCHEDULED_JOB_ID=143
                    and ji.EXECUTION_STATE_CODE!=4
                    --and UNSUCCESSFULLY_PROCESSED_ITEMS>0
                    or EXPECTED_NUMBER_OF_ITEMS !=SUCCESSFULLY_PROCESSED_ITEMS and exs.LANGUAGE_CODE='SK' and START_ACTION_DATETIME >= trunc(sysdate-3)
                    order by START_ACTION_DATETIME desc)
                    --where rownum <=8
                    """
    cursor.execute(sql_job)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
    jobs_error = dictfetchall(cursor)

    sql_all = """SELECT 
                job.SCHEDULED_JOB_ID,
                JOB_NAME,
                JOB_DESCRIPTION,
                SCHEDULER_ACTION_ID,
                REPETITION_TYPE_CODE,
                REPETITION_COUNT,
                INCLUDE_WEEKENDS,
                INCLUDE_HOLIDAYS,
                FLAG_DAY_MULTIPICK,
                FLAG_MONTH_MULTIPICK,
                FLAG_DAY_OF_MONTH_MULTIPICK,
                FROM_TIME,
                TO_TIME,
                SCHEDULED_FROM,
                SCHEDULED_TO,
                job.AS_GROUP_ID,
                CAST(FROM_TZ(CAST(EXECUTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXECUTION_DATETIME,
                job.JOB_INSTANCE_ID,
                LAST_JOB_INSTANCE_ID,
                CAST(FROM_TZ(CAST(job.CHANGED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CHANGED_ON,
                SYSTEM_TASK,
                CUSTOM_INTERVAL,
                job.SCHEDULER_PARAMETER_SET_ID,
                DELETED_ON,
                EXECUTION_STATE_NAME
                FROM EETS_CO.SCHEDULED_JOB job
                left join EETS_CO.JOB_INSTANCE ins on job.LAST_JOB_INSTANCE_ID=ins.JOB_INSTANCE_ID
                left join eets_CO.EXECUTION_STATE_L exs on ins.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE and  exs.LANGUAGE_CODE='SK'
                order by CHANGED_ON desc
                    """
    cursor.execute(sql_all)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
    jobs_all = dictfetchall(cursor)

    if 'q' in request.GET:
        q=request.GET['q']

        sql_ROLE_NAME ="""SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME, EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS
                                FROM eets_CO.JOB_INSTANCE ji
                                left join eets_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                                left join eets_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
                                where
                                exs.LANGUAGE_CODE='SK'
                                and START_ACTION_DATETIME >= trunc(sysdate-180)
                                and JOB_NAME like :id
                                order by START_ACTION_DATETIME desc"""
        c = '%' + q + '%'
        cursor.execute(sql_ROLE_NAME, id=c)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
        job_s = dictfetchall(cursor)
        # logger.info("Príkaz sa úspešne vykonal.")
        messages.info(request, f"Vyhľadávanie bolo dokončené. Hľadaný reťazec: {c}")
        
        # print('sadfsadf')
            # print(job_s)
    # cursor.close()
    # connection.close()

    context = { 'jobe': jobs_error, 'job_s':job_s, 'q':q, 'jobs_all':jobs_all } #'job_s':job_s,
    return render(request,'eets/jobs.html', context)

@login_required
def eetsdb(request):
    export = ''
    column_names_list = ''
    q = None

    if 'q' in request.GET:
        q=request.GET['q']

        EETS_DB=EETSDB.objects.get(user=1)
        con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
        cursor = con_EETSDB_STDBY.cursor()
        sql_query =q

        with con_EETSDB_STDBY.cursor() as cursor:
            cursor.execute(sql_query)
            # export1 = cursor.description
            column_names_list = [x[0] for x in cursor.description]
            # export = dictfetchall(cursor)
            

            # cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
            export = cursor.fetchall()
            # print(export)

    context = {'export':export, 'column_names_list':column_names_list,  'q':q }
    return render(request, 'eets/eetsdb.html', context)

@login_required
def dwhdb(request):
    export = ''
    column_names_list = ''
    q = None

    if 'q' in request.GET:
        q=request.GET['q']

        EMS_DWH=EMS_DWHDB.objects.get(user=1)
        con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
        cur_EMSDWH = con_EMSDWH_STDBY.cursor()
        sql_query =q

        with con_EMSDWH_STDBY.cursor() as cursor:
            cursor.execute(sql_query)
            # export1 = cursor.description
            column_names_list = [x[0] for x in cursor.description]
            # export = dictfetchall(cursor)
            

            # cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
            export = cursor.fetchall()
            # print(export)

    context = {'export':export, 'column_names_list':column_names_list,  'q':q }
    return render(request, 'eets/eetsdb.html', context)

@login_required
def dwh_control(request):
    import cx_Oracle
    # cis_db=CISDB.objects.get(user=request.user)
    EMS_DWH=EMS_DWHDB.objects.get(user=1)
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()

    sql_logs = """select STEP, TO_CHAR(from_tz(CAST(STEP_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as STEP_DATE_TIME_CET
                  from EETS_STA.v_dwh_load_status"""

    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_logs)
        dwh_logs = dictfetchall(cursor)
        
    sql_detail = """select ID_DWH_LOAD_DETAIL, SOURCE_SYSTEM_NAME, LOAD_NUMBER, PARTITION_ID, LOAD_STAGE, STATUS,
                    TO_CHAR(from_tz(CAST(DATE_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as DATE_FROM_CET,
                    TO_CHAR(from_tz(CAST(DATE_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as DATE_TO_CET,
                    TO_CHAR(from_tz(CAST(LOAD_START AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as LOAD_START_CET,
                    TO_CHAR(from_tz(CAST(LOAD_END AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as LOAD_END_CET,
                    round((LOAD_END - LOAD_START) * 24 * 60, 1) AS diff_minutes,
                    TABLE_NAME, COMMAND
                    from EETS_STA.dwh_load_detail
                    where LOAD_START >= TRUNC(sysdate-3)
                    order by LOAD_START desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_detail)
        dwh_detail = dictfetchall(cursor)

    sql_error = """SELECT 
                    ID_DWH_LOAD_ERROR,
                    ID_DWH_LOAD_DETAIL,
                    ERROR ,
                    TO_CHAR(from_tz(CAST(CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as CREATED_ON
                    FROM EETS_STA.dwh_load_error order by ID_DWH_LOAD_ERROR desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_error)
        dwh_error = dictfetchall(cursor)

    sql_merge_tables = """
                        select 
                        LOAD_NUMBER,	SOURCE_SYSTEM_NAME,	PARTITION_ID,	IS_MERGED_FLAG,	
                        TO_CHAR(from_tz(CAST(MERGE_FINISHED_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as 
                        MERGE_FINISHED_DATETIME,	IS_PREPARED_TO_MERGE,	
                        IS_EXPORT_RUNNING_FLAG,	LAST_RUN_ERROR_MESSAGE
                        from EETS_STA.dwh_merge_table
                        order by LOAD_NUMBER desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_merge_tables)
        dwh_merge = dictfetchall(cursor)

    sql_tables = """SELECT ext.*, CAST(FROM_TZ(CAST(LAST_RUN AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LAST_RUN_CET  FROM EETS_STA.DWH_EXPORT_TABLE ext
                    order by LAST_RUN desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_tables)
        dwh_tables = dictfetchall(cursor)

    context={'dwh_logs': dwh_logs, 'dwh_detail':dwh_detail, 'dwh_error':dwh_error, 'dwh_tables':dwh_tables, 'dwh_merge':dwh_merge }
    return render(request, 'eets/dwh_control.html', context)

#### SAIDA ##############
@login_required
def saidamd_fronts(request):
    SAIDAMD_DB=SAIDAMDDB.objects.get(user=1)
    con_SAIDAMD_STDBY = cx_Oracle.connect(SAIDAMD_DB.SAIDAMD_username+"/"+SAIDAMD_DB.SAIDAMD_password+"@"+SAIDAMD_DB.SAIDAMD_hostname+":"+SAIDAMD_DB.SAIDAMD_port+"/"+SAIDAMD_DB.SAIDAMD_servicename)
    cursor = con_SAIDAMD_STDBY.cursor()

    sql_fonts = """
                select x.stav, x.fronta, x.sn_prefix TSP, count(*) as count, min(enq_time) as min_enq_time, min(deq_time) as min_deq_time, max(enq_time) as max_enq_time, max(deq_time) as max_deq_time, max(deq_dt) as max_deq_dt from(
                select state as stav, queue as fronta, substr(TCSOBUSERIAL, 1,7) as sn_prefix, enq_time, deq_time, deq_dt from (
                    SELECT q.ENQ_TIME, q.Q_NAME QUEUE, q.USER_DATA.header.type msg_type, q.USER_DATA.header.get_string_property('TCSObuSerial') TCSObuSerial, CAST(q.MSGID as VARCHAR2(1000)) MSG_ID, q.CORRID CORR_ID, decode(q.USER_DATA.text_vc, NULL, dbms_lob.substr(q.USER_DATA.text_lob, 4000, 1), q.USER_DATA.text_vc) msg_data, (q.DEQ_TIME-q.ENQ_TIME) DEQ_DT, q.DEQ_TIME, q.STATE FROM MD.ETBOEETSCHARGE_TABLE q     -- asi vystupna fronta smerom na Billien
                    UNION ALL
                    SELECT q.ENQ_TIME, q.Q_NAME QUEUE, q.USER_DATA.header.type msg_type, q.USER_DATA.header.get_string_property('TCSObuSerial') TCSObuSerial, CAST(q.MSGID as VARCHAR2(1000)) MSG_ID, q.CORRID CORR_ID, decode(q.USER_DATA.text_vc, NULL, dbms_lob.substr(q.USER_DATA.text_lob, 4000, 1), q.USER_DATA.text_vc) msg_data, (q.DEQ_TIME-q.ENQ_TIME) as DEQ_DT, q.DEQ_TIME, q.STATE FROM MD.ETBOEETSCHARGEPRX1_TABLE q    --  vstupna fronta smerom z TC Proxy
                    ) 
                where ENQ_TIME>SYSDATE-1/24
                AND ENQ_TIME< SYSDATE-0/24    
                )x
                group by x.stav, x.fronta, x.sn_prefix
                order by x.stav desc, x.sn_prefix desc
              """
    cursor.execute(sql_fonts)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
    fonts = dictfetchall(cursor)
    # print(fonts)


    context = {'fonts':fonts, 'fonts':fonts}
    return render(request, 'eets/saidamd_fonts.html', context)

#PROXY
@login_required
def proxy_section(request):
    PROXY_DB=PROXYDB.objects.get(user=1)
    con_PROXY_STDBY = cx_Oracle.connect(PROXY_DB.PROXYDB_username+"/"+PROXY_DB.PROXYDB_password+"@"+PROXY_DB.PROXYDB_hostname+":"+PROXY_DB.PROXYDB_port+"/"+PROXY_DB.PROXYDB_servicename)
    cursor = con_PROXY_STDBY.cursor()

    if 'x' in request.GET and request.GET['y'] =='':
        
        x = request.GET['x']
        y = request.GET['y']

        sql_x="""
                SELECT 
                    ep.EETS_PROVIDER_ABBREVIATION,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24') AS HOUR,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''') AS DAY,
                    COUNT(dsl.DETECTED_SECTION_LOG_ID) AS COUNT_DETECTED_SECTION
                FROM 
                    EETSPRX_PE.DETECTED_SECTION_LOG dsl
                LEFT JOIN 
                    EETSPRX_PE.eets_provider ep 
                    ON ep.EETS_PROVIDER_ID = dsl.EETS_PROVIDER_ID
                WHERE 
                    dsl.CREATED_ON >= TO_TIMESTAMP(:id, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                GROUP BY 
                    ep.EETS_PROVIDER_ABBREVIATION,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24'),
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''')
                ORDER BY 
                    HOUR desc, 
                    ep.EETS_PROVIDER_ABBREVIATION
                """
 
        with con_PROXY_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_x, id=x)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sections = dictfetchall(cursor)
            
    
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_y="""
                SELECT 
                    ep.EETS_PROVIDER_ABBREVIATION,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24') AS HOUR,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''') AS DAY,
                    COUNT(dsl.DETECTED_SECTION_LOG_ID) AS COUNT_DETECTED_SECTION
                FROM 
                    EETSPRX_PE.DETECTED_SECTION_LOG dsl
                LEFT JOIN 
                    EETSPRX_PE.eets_provider ep 
                    ON ep.EETS_PROVIDER_ID = dsl.EETS_PROVIDER_ID
                WHERE 
                    dsl.CREATED_ON <= TO_TIMESTAMP(:id, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                GROUP BY 
                    ep.EETS_PROVIDER_ABBREVIATION,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24'),
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''')
                ORDER BY 
                    HOUR desc, 
                    ep.EETS_PROVIDER_ABBREVIATION  
        """

        with con_PROXY_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_y, id=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sections = dictfetchall(cursor)

    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
                SELECT 
                    ep.EETS_PROVIDER_ABBREVIATION,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24') AS HOUR,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''') AS DAY,
                    COUNT(dsl.DETECTED_SECTION_LOG_ID) AS COUNT_DETECTED_SECTION
                FROM 
                    EETSPRX_PE.DETECTED_SECTION_LOG dsl
                LEFT JOIN 
                    EETSPRX_PE.eets_provider ep 
                    ON ep.EETS_PROVIDER_ID = dsl.EETS_PROVIDER_ID
                WHERE 
                    dsl.CREATED_ON >= to_date(:id_x, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                    AND dsl.CREATED_ON <= to_date(:id_y, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                GROUP BY 
                    ep.EETS_PROVIDER_ABBREVIATION,
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24'),
                    TO_CHAR(FROM_TZ(CAST(dsl.CREATED_ON AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''')
                ORDER BY 
                    HOUR desc, 
                    ep.EETS_PROVIDER_ABBREVIATION
        """
        with con_PROXY_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_xy, id_x=x, id_y=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sections = dictfetchall(cursor)

    else:
        sql_section = """
                        WITH hours AS (
                            SELECT TO_CHAR(SYSDATE - (LEVEL - 1) / 24, 'YYYY-MM-DD HH24') AS hour
                            FROM dual
                            CONNECT BY LEVEL <= 24 -- Predpokladáme, že chceme hodiny za posledných 24 hodín
                        ),
                        providers AS (
                            SELECT DISTINCT ep.eets_provider_abbreviation
                            FROM eetsprx_pe.eets_provider ep
                        )
                        SELECT
                            p.eets_provider_abbreviation,
                            h.hour,
                            NVL(COUNT(dsl.detected_section_log_id), 0) AS count_detected_section
                        FROM
                            providers p
                            CROSS JOIN hours h
                            LEFT JOIN (
                                SELECT
                                    ep.eets_provider_abbreviation,
                                    TO_CHAR(from_tz(CAST(dsl.created_on AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24') AS hour,
                                    dsl.detected_section_log_id
                                FROM
                                    eetsprx_pe.detected_section_log dsl
                                    LEFT JOIN eetsprx_pe.eets_provider ep ON ep.eets_provider_id = dsl.eets_provider_id
                                WHERE
                                    dsl.created_on > (SYSDATE -1) - 2/24
                            ) dsl ON p.eets_provider_abbreviation = dsl.eets_provider_abbreviation AND h.hour = dsl.hour
                        GROUP BY
                            p.eets_provider_abbreviation,
                            h.hour
                        ORDER BY
                            h.hour DESC,
                            p.eets_provider_abbreviation
                """
        cursor.execute(sql_section)
                #rows = cursor.fetchall()        
                #rows = namedtuplefetchall(cursor)
        sections = dictfetchall(cursor)
        # print(fonts)

    context = {'sections':sections}
    return render(request, 'eets/proxy_section.html', context)

# TC Rating
@login_required
def tc_rating(request):
    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()


    if 'x' in request.GET and request.GET['y'] =='':
        
        x = request.GET['x']
        y = request.GET['y']

        sql_x="""
                WITH converted_timestamps AS (
                        SELECT 
                            rtee.VEHICLE_ID,
                            rtee.EETS_PROVIDER_ID,
                            FROM_TZ(CAST(rtee.OBU_TIMESTAMP AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague' AS OBU_TIMESTAMP_PRAGUE,
                            rtee.toll_event_type_code,
                            rtee.OBU_TIMESTAMP
                        FROM EETS_BE.EETS_RTE rtee
                    )
                    SELECT 
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') AS ROK_MES_HOD,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''') AS DAY,
                        SUM(DECODE(toll_event_type_code, 1, 1, 2, -1, 3, 1)) AS MT
                    FROM 
                        converted_timestamps rtee
                    INNER JOIN 
                        EETS_ECM.VEHICLE v ON v.VEHICLE_ID = rtee.VEHICLE_ID
                    INNER JOIN 
                        EETS_ECM.EETS_PROVIDER ep ON ep.EETS_PROVIDER_ID = rtee.EETS_PROVIDER_ID
                    WHERE 
                        rtee.OBU_TIMESTAMP >= TO_TIMESTAMP(:id, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                    GROUP BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24'),
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH'''),
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION
                    ORDER BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') DESC,
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION     
                """
 
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_x, id=x)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sections = dictfetchall(cursor)
            
    
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_y="""
                WITH converted_timestamps AS (
                        SELECT 
                            rtee.VEHICLE_ID,
                            rtee.EETS_PROVIDER_ID,
                            FROM_TZ(CAST(rtee.OBU_TIMESTAMP AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague' AS OBU_TIMESTAMP_PRAGUE,
                            rtee.toll_event_type_code,
                            rtee.OBU_TIMESTAMP
                        FROM EETS_BE.EETS_RTE rtee
                    )
                    SELECT 
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') AS ROK_MES_HOD,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''') AS DAY,
                        SUM(DECODE(toll_event_type_code, 1, 1, 2, -1, 3, 1)) AS MT
                    FROM 
                        converted_timestamps rtee
                    INNER JOIN 
                        EETS_ECM.VEHICLE v ON v.VEHICLE_ID = rtee.VEHICLE_ID
                    INNER JOIN 
                        EETS_ECM.EETS_PROVIDER ep ON ep.EETS_PROVIDER_ID = rtee.EETS_PROVIDER_ID
                    WHERE 
                        rtee.OBU_TIMESTAMP <= TO_TIMESTAMP(:id, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                    GROUP BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24'),
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH'''),
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION
                    ORDER BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') DESC,
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION   
        """

        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_y, id=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sections = dictfetchall(cursor)

    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
                WITH converted_timestamps AS (
                        SELECT 
                            rtee.VEHICLE_ID,
                            rtee.EETS_PROVIDER_ID,
                            FROM_TZ(CAST(rtee.OBU_TIMESTAMP AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague' AS OBU_TIMESTAMP_PRAGUE,
                            rtee.toll_event_type_code,
                            rtee.OBU_TIMESTAMP
                        FROM EETS_BE.EETS_RTE rtee
                    )
                    SELECT 
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') AS ROK_MES_HOD,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''') AS DAY,
                        SUM(DECODE(toll_event_type_code, 1, 1, 2, -1, 3, 1)) AS MT
                    FROM 
                        converted_timestamps rtee
                    INNER JOIN 
                        EETS_ECM.VEHICLE v ON v.VEHICLE_ID = rtee.VEHICLE_ID
                    INNER JOIN 
                        EETS_ECM.EETS_PROVIDER ep ON ep.EETS_PROVIDER_ID = rtee.EETS_PROVIDER_ID
                    WHERE 
                        rtee.OBU_TIMESTAMP >= to_date(:id_x, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                        AND rtee.OBU_TIMESTAMP <= to_date(:id_y, 'DD-MM-YYYY HH24:MI:SS') - 2/24
                        
                    GROUP BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24'),
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH'''),
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION
                    ORDER BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') DESC,
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION 
        """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_xy, id_x=x, id_y=y)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sections = dictfetchall(cursor)

    else:
        sql_ack = """
                WITH converted_timestamps AS (
                        SELECT 
                            rtee.VEHICLE_ID,
                            rtee.EETS_PROVIDER_ID,
                            FROM_TZ(CAST(rtee.OBU_TIMESTAMP AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Prague' AS OBU_TIMESTAMP_PRAGUE,
                            rtee.toll_event_type_code,
                            rtee.OBU_TIMESTAMP
                        FROM EETS_BE.EETS_RTE rtee
                    )
                    SELECT 
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') AS ROK_MES_HOD,
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH''') AS DAY,
                        SUM(DECODE(toll_event_type_code, 1, 1, 2, -1, 3, 1)) AS MT
                    FROM 
                        converted_timestamps rtee
                    INNER JOIN 
                        EETS_ECM.VEHICLE v ON v.VEHICLE_ID = rtee.VEHICLE_ID
                    INNER JOIN 
                        EETS_ECM.EETS_PROVIDER ep ON ep.EETS_PROVIDER_ID = rtee.EETS_PROVIDER_ID
                    WHERE 
                        rtee.OBU_TIMESTAMP >= TRUNC(SYSDATE) - 2/24
                    GROUP BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24'),
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'DY', 'NLS_DATE_LANGUAGE = ''ENGLISH'''),
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION
                    ORDER BY 
                        TO_CHAR(OBU_TIMESTAMP_PRAGUE, 'YYYY-MM-DD HH24') DESC,
                        v.EETS_PROVIDER_ID,
                        ep.PROVIDER_ABBREVIATION 
              """
        with con_EETSDB_STDBY.cursor() as cursor:
            cursor.execute(sql_ack)
            sections = dictfetchall(cursor)


    context = {'sections':sections}
    return render(request, 'eets/rating.html', context)

# TC Rating preparation
@login_required
def td_preparation(request):
    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()

    sql="""
            SELECT 
                subquery.PROVIDER_ABBREVIATION,
                COUNT(*) AS ROW_COUNT,
                MIN(EVENT_DATETIME_CET) AS FIRST_EVENT_DATETIME_CET,
                MAX(EVENT_DATETIME_CET) AS LAST_EVENT_DATETIME_CET
            FROM (
                SELECT 
                    prov.PROVIDER_ABBREVIATION,
                    tdr.EETS_TOLL_DATA_RECORD_ID,
                    tdr.OBE_NUMBER,
                    tdr.EVENT_DATETIME + INTERVAL '2' HOUR AS EVENT_DATETIME_CET
                FROM 
                    EETS_RE.eets_toll_data_record tdr
                LEFT JOIN 
                    EETS_ECM.IMP_VEHICLE imp ON tdr.OBE_NUMBER = imp.OBE_NUMBER
                LEFT JOIN 
                    EETS_ECM.vehicle veh ON imp.EETS_REGISTRATION_NUMBER = veh.EETS_REGISTRATION_NUMBER
                LEFT JOIN 
                    EETS_ECM.EETS_PROVIDER prov ON veh.EETS_PROVIDER_ID = prov.EETS_PROVIDER_ID
            /* WHERE 
                    prov.PROVIDER_ABBREVIATION = 'TELEPASS'
                    --AND tdr.OBE_NUMBER = '3AC976B9' */
                GROUP BY 
                    prov.PROVIDER_ABBREVIATION,
                    tdr.EETS_TOLL_DATA_RECORD_ID,
                    tdr.OBE_NUMBER,
                    tdr.EVENT_DATETIME
            ) subquery
            GROUP BY 
                subquery.PROVIDER_ABBREVIATION    
                """
 
    with con_EETSDB_STDBY.cursor() as cursor:
            
            # c = '%' + q + '%'
            cursor.execute(sql)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sections = dictfetchall(cursor)
    

    context = {'sections':sections}
    return render(request, 'eets/pre_rating.html', context)


@login_required
def eets_rte(request):
    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()
    
    # sql_ = """SELECT POS_ID, POS_NUMBER, POS_NAME, pos.POS_TYPE_CODE, POS_TYPE_NAME, pos.RETAIL_PARTNER_ID, rp.RETAIL_PARTNER_NAME
    #                                 from edz_co.pos pos
    #                                 left join edz_co.POS_TYPE_L typ on pos.POS_TYPE_CODE=typ.POS_TYPE_CODE
    #                                 left join edz_co.retail_partner rp on pos.retail_partner_id = rp.retail_partner_id
    #                                 where /*pos.priority != '-1'
    #                                 and */ typ.LANGUAGE_CODE='SK'
    #                                 order by POS_NUMBER
    #                             """
    # with con_EDZDB_STDBY.cursor() as cursor:
    #     cursor.execute(sql_)
    #         #rows = cursor.fetchall()        
    #         #rows = namedtuplefetchall(cursor)
    #     Poses = dictfetchall(cursor)
    rte = ''
    if 'a' in request.GET and request.GET['b'] =='' and request.GET['c'] =='' and request.GET['d'] =='':
        a = request.GET['a']
        b = request.GET['b']
        c = request.GET['c']
        d = request.GET['d']

        db_id ="""select
                            etd.*,
                            el.integration_log_id,
                            etd.vehicle_id,
                            el.exported_on,
                            v.REGISTRATION_NUMBER
                            from EETS_EDE.ede_log el
                            full join EETS_BE.eets_rte etd on etd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join EETS_BE.eets_rte_delayed etdd on etdd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join eets_ecm.vehicle v on v.vehicle_id = etd.vehicle_id 
                            where el.INTEGRATION_LOG_ID IN (:id)
                            order by etd.EETS_RTE_ID desc
                                """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(db_id, id=a)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            rte = dictfetchall(cursor)
            # print(rte)

    elif 'b' in request.GET and request.GET['a'] =='' and request.GET['c'] =='' and request.GET['d'] =='':
        a = request.GET['a']
        b = request.GET['b']
        c = request.GET['c']
        d = request.GET['d']

        db_id ="""select
                            etd.*,
                            el.integration_log_id,
                            etd.vehicle_id,
                            el.exported_on,
                            v.REGISTRATION_NUMBER
                            from EETS_EDE.ede_log el
                            full join EETS_BE.eets_rte etd on etd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join EETS_BE.eets_rte_delayed etdd on etdd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join eets_ecm.vehicle v on v.vehicle_id = etd.vehicle_id 
                            where etd.EETS_RTE_ID IN (:id)
                            order by etd.EETS_RTE_ID desc
                                """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(db_id, id=b)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            rte = dictfetchall(cursor)
    elif 'c' in request.GET and request.GET['a'] =='' and request.GET['b'] =='' and request.GET['d'] =='':
        
    # if x is not None and x != '' :
        a = request.GET['a']
        b = request.GET['b']
        c = request.GET['c']
        d = request.GET['d']

        db_id ="""select
                            etd.*,
                            el.integration_log_id,
                            etd.vehicle_id,
                            el.exported_on,
                            v.REGISTRATION_NUMBER
                            from EETS_EDE.ede_log el
                            full join EETS_BE.eets_rte etd on etd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join EETS_BE.eets_rte_delayed etdd on etdd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join eets_ecm.vehicle v on v.vehicle_id = etd.vehicle_id 
                            where etd.OBE_NUMBER IN (:id)
                            order by etd.EETS_RTE_ID desc
                                """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(db_id, id=c)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            rte = dictfetchall(cursor)

    elif 'd' in request.GET and request.GET['a'] =='' and request.GET['b'] =='' and request.GET['c'] =='':
        
    # if x is not None and x != '' :
        a = request.GET['a']
        b = request.GET['b']
        c = request.GET['c']
        d = request.GET['d']

        db_id ="""select
                            etd.*,
                            el.integration_log_id,
                            etd.vehicle_id,
                            el.exported_on,
                            v.REGISTRATION_NUMBER
                            from EETS_EDE.ede_log el
                            full join EETS_BE.eets_rte etd on etd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join EETS_BE.eets_rte_delayed etdd on etdd.EETS_EXPORT_ILOG_ID = el.integration_log_id
                            full join eets_ecm.vehicle v on v.vehicle_id = etd.vehicle_id 
                            where v.REGISTRATION_NUMBER IN (:id)
                            order by etd.EETS_RTE_ID desc
                                """
        with con_EETSDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(db_id, id=d)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            rte = dictfetchall(cursor)

    context = { 'rte':rte }
    return render(request,'eets/rte.html', context)



##################################################################################################################################
############################# LEGO REPORT PDF
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

@login_required
def dwh_rep_CRM(request):
    export = ''
    column_names_list = ''
    q = None

    con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@scan-dwh.etc.example:1521/dwh")
    
    sql_logs = """select * from V_EETS_LEGO_REP_01
                    order by TRANSACTION_ARRIVAL_MONTH desc"""

    with con_DWH_REP_CRM.cursor() as cursor:
        cursor.execute(sql_logs)
        dwh_lego_view = dictfetchall(cursor)

    sql_removed_bilds = """select * from KDX_REMOVED_BILL_IDS"""

    with con_DWH_REP_CRM.cursor() as cursor:
        cursor.execute(sql_removed_bilds)
        dwh_lego_removed_bill = dictfetchall(cursor)
        # print(dwh_lego_removed_bill)

    if request.method == 'POST':
        if 'generation_pdf' in request.POST:
            from datetime import datetime
            MM = request.POST.get('MM')

            # Fonty
            pdfmetrics.registerFont(TTFont('DejaVuSans', './eets/static/fonts/DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('Arial Unicode MS', './eets/static/fonts/arial-unicode-ms.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', './eets/static/fonts/DejaVuSans-Bold.ttf')) # Nová registrácia pre tučné písmo

            # Dátumy
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("Dátum vygenerovania: %d. %m. %Y %H:%M:%S")
            previous_month = current_datetime - relativedelta(months=1)
            formatted_previous_year = previous_month.strftime("%Y")

            # Oracle connection
            con_DWH_REP_CRM = cx_Oracle.connect(
                "DB_USER/DB_PASSWORD@scan-dwh.etc.example:1521/dwh"
            )

            # -------------------- NAČÍTANIE DÁT --------------------

            # Hlavné dáta
            pdf_sql = """
                select * from V_EETS_LEGO_REP_01_EXCEL_3COMP_ALL
                where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY')
                order by PASSAGEDATE_MONTHLY asc
            """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(pdf_sql, MM=MM)
                pdf_data = dictfetchall(cursor)

            # Filtrovanie podľa vlastníkov
            filtered_data_granvia = [x for x in pdf_data if x['OWNER_NAME'] == 'Granvia']
            sum_spolu_granvia = sum(row['EETS_INFRASTRUCTURE'] for row in filtered_data_granvia)

            filtered_data_zbl = [x for x in pdf_data if x['OWNER_NAME'] == 'Zero Bypass Limited']
            sum_spolu_zbl = sum(row['EETS_INFRASTRUCTURE'] for row in filtered_data_zbl)

            filtered_data_stat = [x for x in pdf_data if x['OWNER_NAME'] == 'Štát']
            sum_spolu_stat = round(sum(row['EETS_INFRASTRUCTURE'] or 0 for row in filtered_data_stat), 2)

            # PPP
            ppp_sql = """
                select PASSAGEDATE_MONTHLY, SUM(EETS_INFRASTRUCTURE) as SPOLU
                from V_EETS_LEGO_REP_01_EXCEL_3COMP_ALL
                where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY')
                and OWNER_NAME in ('Granvia','Zero Bypass Limited')
                group by PASSAGEDATE_MONTHLY
                order by PASSAGEDATE_MONTHLY asc
            """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(ppp_sql, MM=MM)
                ppp_data = dictfetchall(cursor)
            sum_spolu_ppp = round(sum(row['SPOLU'] for row in ppp_data), 2)

            # Spolu všetci
            spolu_sql = """
                select PASSAGEDATE_MONTHLY, SUM(EETS_INFRASTRUCTURE) as SPOLU
                from V_EETS_LEGO_REP_01_EXCEL_3COMP_ALL
                where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY')
                group by PASSAGEDATE_MONTHLY
                order by PASSAGEDATE_MONTHLY asc
            """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(spolu_sql, MM=MM)
                spolu_data = dictfetchall(cursor)
            sum_spolu = round(sum(row['SPOLU'] for row in spolu_data), 2)
            
            # Spolu co2
            spolu_sql_co2 = """
                SELECT 
                    PASSAGEDATE_MONTHLY, 
                    EETS_CO2, 
                    EETS_POLLUTION, 
                    EETS_INFRASTRUCTURE,
                    SPOLU
                FROM (
                    SELECT 
                        PASSAGEDATE_MONTHLY, 
                        SUM(EETS_CO2) as EETS_CO2, 
                        SUM(EETS_POLLUTION) as EETS_POLLUTION, 
                        SUM(EETS_INFRASTRUCTURE) as EETS_INFRASTRUCTURE,
                        SUM(EETS_CO2 + EETS_POLLUTION + EETS_INFRASTRUCTURE) as SPOLU,
                        0 as ORDER_COL
                    FROM V_EETS_LEGO_REP_01_EXCEL_3COMP_ALL
                    WHERE TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY')
                    GROUP BY PASSAGEDATE_MONTHLY

                    UNION ALL

                    SELECT 
                        'Celková suma:' as PASSAGEDATE_MONTHLY,
                        SUM(EETS_CO2) as EETS_CO2,
                        SUM(EETS_POLLUTION) as EETS_POLLUTION,
                        SUM(EETS_INFRASTRUCTURE) as EETS_INFRASTRUCTURE,
                        SUM(EETS_CO2 + EETS_POLLUTION + EETS_INFRASTRUCTURE) as SPOLU,
                        1 as ORDER_COL
                    FROM V_EETS_LEGO_REP_01_EXCEL_3COMP_ALL
                    WHERE TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY')
                )
                ORDER BY ORDER_COL, PASSAGEDATE_MONTHLY
            """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(spolu_sql_co2, MM=MM)
                data_co2 = dictfetchall(cursor)
            
            # -------------------- PRÍPRAVA TABULIEK --------------------

            # GRANVIA
            table_data_GRANVIA = [["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"]]
            for row in filtered_data_granvia:
                table_data_GRANVIA.append([
                    row['PASSAGEDATE_MONTHLY'],
                    f"{row['EETS_INFRASTRUCTURE']:,.2f}".replace(',', ' ').replace('.',','), # Zmena formátovania
                    f"{row['EETS_INFRASTRUCTURE']:,.2f}".replace(',', ' ').replace('.',',')
                ])
            table_data_GRANVIA.append([
                'Celková suma:',
                f"{sum_spolu_granvia:,.2f}".replace(',', ' ').replace('.',','),
                f"{sum_spolu_granvia:,.2f}".replace(',', ' ').replace('.',',')
            ])

            # ZBL
            table_data_ZBL = [["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"]]
            for row in filtered_data_zbl:
                table_data_ZBL.append([
                    row['PASSAGEDATE_MONTHLY'],
                    f"{row['EETS_INFRASTRUCTURE']:,.2f}".replace(',', ' ').replace('.',','),
                    f"{row['EETS_INFRASTRUCTURE']:,.2f}".replace(',', ' ').replace('.',',')
                ])
            table_data_ZBL.append([
                'Celková suma:',
                f"{sum_spolu_zbl:,.2f}".replace(',', ' ').replace('.',','),
                f"{sum_spolu_zbl:,.2f}".replace(',', ' ').replace('.',',')
            ])

            # PPP
            table_data_PPP = [["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"]]
            for row in ppp_data:
                table_data_PPP.append([
                    row['PASSAGEDATE_MONTHLY'],
                    f"{row['SPOLU']:,.2f}".replace(',', ' ').replace('.',','),
                    f"{row['SPOLU']:,.2f}".replace(',', ' ').replace('.',',')
                ])
            table_data_PPP.append([
                'Celková suma:',
                f"{sum_spolu_ppp:,.2f}".replace(',', ' ').replace('.',','),
                f"{sum_spolu_ppp:,.2f}".replace(',', ' ').replace('.',',')
            ])

            # STAT
            table_data_stat = [["MESIAC PREJAZDU MÝTNEHO ÚSEKU", "EETS", "SPOLU"]]
            for row in filtered_data_stat:
                table_data_stat.append([
                    row['PASSAGEDATE_MONTHLY'],
                    "{:,.2f}".format(row['EETS_INFRASTRUCTURE'] or 0).replace(',', ' ').replace('.', ','),
                    "{:,.2f}".format(row['EETS_INFRASTRUCTURE'] or 0).replace(',', ' ').replace('.', ',')
                ])
            table_data_stat.append([
                'CELKOVÁ SUMA:',
                "{:,.2f}".format(sum_spolu_stat).replace(',', ' ').replace('.', ','),
                "{:,.2f}".format(sum_spolu_stat).replace(',', ' ').replace('.', ',')
            ])

            # SPOLU
            table_data_spolu = [["MESIAC PREJAZDU MÝTNEHO ÚSEKU", "EETS", "SPOLU"]]
            for row in spolu_data:
                table_data_spolu.append([
                    row['PASSAGEDATE_MONTHLY'],
                    "{:,.2f}".format(row['SPOLU'] or 0).replace(',', ' ').replace('.', ','),
                    "{:,.2f}".format(row['SPOLU'] or 0).replace(',', ' ').replace('.', ',')
                ])
            table_data_spolu.append([
                'CELKOVÁ SUMA:',
                "{:,.2f}".format(sum_spolu).replace(',', ' ').replace('.', ','),
                "{:,.2f}".format(sum_spolu).replace(',', ' ').replace('.', ',')
            ])
            
            # CO2
            table_data_CO2 = [["MESIAC PREJAZDU MÝTNEHO ÚSEKU", "EETS CO2", "EETS Znečistenie", "EETS Infraštruktúra", "SPOLU"]]
            for row in data_co2:
                table_data_CO2.append([
                    row['PASSAGEDATE_MONTHLY'],
                    "{:,.2f}".format(row['EETS_CO2'] or 0).replace(',', ' ').replace('.', ','),
                    "{:,.2f}".format(row['EETS_POLLUTION'] or 0).replace(',', ' ').replace('.', ','),
                    "{:,.2f}".format(row['EETS_INFRASTRUCTURE'] or 0).replace(',', ' ').replace('.', ','),
                    "{:,.2f}".format(row['SPOLU'] or 0).replace(',', ' ').replace('.', ',')
                ])


            # -------------------- GENERÁTOR PDF --------------------
            
            # Globálne konštanty pre PDF
            PAGE_HEIGHT = A4[1]
            PAGE_WIDTH = A4[0]
            TOP_MARGIN = 130    # Priestor pre logo, hlavičku, titulok
            BOTTOM_MARGIN = 90  # Výška, ktorú zaberá footer (90px)
            spacing_between_tables = 15
            
            # Štýl tabuliek (musí byť definovaný globálne pre funkcie)
            table_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'DejaVuSans-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
                ('LEADING', (0, 0), (-1, -1), 5),
            ])

            # --- Funkcia na kreslenie hlavičky a päty ---
            def draw_page_elements(c, total_pages, title_page_2, current_page_number, formatted_datetime, MM, formatted_previous_year):
                # Logo a hlavička
                c.drawImage("./eets/static/img/logo_myto.png", 35, 780, width=80, height=50)
                c.setFont("Arial Unicode MS", 8)
                c.drawString(414, 800, "Číslo zostavy: EETS_LEGO_REP_01")
                c.drawString(503, 785, "PDF formát")
                c.drawString(385, 770, formatted_datetime)

                c.setFont("Helvetica-Bold", 14)
                if current_page_number == 1:
                    c.drawString(165, 750 , "Prerozdelenie mýta medzi vlastníkov ciest")
                else:
                    c.drawString(165, 750, title_page_2)

                c.setFont("Helvetica-Bold", 10)
                c.drawString(35, 720, "Mýtne transakcie spracované za obdobie:")
                c.setFont("Arial Unicode MS", 8)
                c.drawString(250, 720, MM + '/' + formatted_previous_year)

                # Červené čiary
                c.setStrokeColorRGB(1, 0, 0)
                c.line(560, BOTTOM_MARGIN, 560, 830) # BOTTOM_MARGIN (90) je dolná línia
                c.line(35, BOTTOM_MARGIN, 560, BOTTOM_MARGIN)

                # Poznámka
                c.setFont("Arial Unicode MS", 7)
                c.drawString(448, 80, "Sumy sú uvedené v EUR bez DPH.")

                # Footer
                c.setFont("Arial Unicode MS", 6)
                text = """
                example, a.s., Westend Plazza, Lamačská cesta 3/B, 841 04 Bratislava, Slovenská republika
                IČO/ID Nr.: 44 500 734, DIČ/Tax ID Nr.: 2022712153, IČ DPH/VAT Nr.: SK2022712153
                Spoločnosť je zapísaná v Obchodnom registri Okresného súdu Bratislava I. v Odd.: Sa, vložka č.: 4646/B
                Company is registered at Companies Register of the District Court Bratislava I. in Section: Sa, Insert No.: 4646/B"""
                lines = [line for line in text.split('\n') if line.strip()]
                y = 70
                for line in lines:
                    c.drawString(9, y, line)
                    y -= 10

                # Číslo strany (dynamické)
                # Číslo strany (dynamické)
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont

                # Registrácia fontu (ak máte súbor)
                pdfmetrics.registerFont(TTFont('ArialUnicodeMS', './eets/static/fonts/arial-unicode-ms.ttf'))

                # Použitie v kóde
                c.saveState()
                c.setFont("ArialUnicodeMS", 7)  # alebo "Helvetica" ak font nie je dostupný

                page_info = "Strana (Page) %d" % current_page_number
                if total_pages is not None:
                    page_info += "/%d" 

                c.drawRightString(550, 20, page_info)
                c.restoreState()


            # --- Funkcia na kreslenie sekcie (hlavné tabuľky) ---
            def draw_section(c, title, table_data, y_position, colWidths=None):
                # Tabuľka
                if colWidths is None:
                    colWidths = [2.5*inch, 1.5*inch + 2.5*inch/2.54, 1.5*inch]
                table = Table(table_data, colWidths=colWidths)
                table.setStyle(table_style)
                table.wrapOn(c, PAGE_WIDTH, PAGE_HEIGHT)
                tw, th = table.wrap(0, 0)

                # Odhadovaná výška sekcie (Nadpis ~10px + Tabuľka + Medzera)
                section_height = 10 + th + spacing_between_tables 
                
                # KONTROLA PRETEČENIA: Ak by nová sekcia presiahla dolný okraj
                if y_position - section_height < BOTTOM_MARGIN:
                    # Ak sa nevojde, začíname novú stranu
                    c.showPage()
                    # Znovu vykreslíme hlavičku/pätu (číslo strany sa aktualizuje automaticky)
                    draw_page_elements(c, TOTAL_PAGES, "Detailná evidencia EETS", c.getPageNumber(), formatted_datetime, MM, formatted_previous_year)
                    # Nová pozícia na vrchu
                    y_position = 690 # Nový štart pod hlavičkou

                # Nadpis
                c.setFont("Helvetica-Bold", 10)
                c.drawString(35, y_position, title)
                y_position -= 1

                # Vykreslenie tabuľky
                table.drawOn(c, (A4[0] - tw) / 4.4, y_position - th)
                y_position -= (th + spacing_between_tables)

                return y_position

            # --- Funkcia na kreslenie sekcie CO2 (draw_section_z) ---
            def draw_section_z(c, title, table_data, y_position, colWidths=None):
                # Tabuľka
                if colWidths is None:
                    # Upravené pre 5 stĺpcov
                    colWidths = [1.6*inch, 1.1*inch, 1.1*inch, 1.5*inch, 1.1*inch]
                table = Table(table_data, colWidths=colWidths)
                table.setStyle(table_style)
                table.wrapOn(c, PAGE_WIDTH, PAGE_HEIGHT)
                tw, th = table.wrap(0, 0)
                
                # Odhadovaná výška sekcie
                section_height = 15 + th + 30 

                # KONTROLA PRETEČENIA (aj keď predpokladáme, že CO2 je na poslednej strane a už by nemal pretekať do footeru)
                if y_position - section_height < BOTTOM_MARGIN:
                    c.showPage()
                    # Znovu vykreslíme hlavičku/pätu (číslo strany sa aktualizuje automaticky)
                    draw_page_elements(c, TOTAL_PAGES, "Detailná evidencia EETS", c.getPageNumber(), formatted_datetime, MM, formatted_previous_year)
                    # Nová pozícia
                    y_position = 690 # Nový štart pod hlavičkou

                # Nadpis
                c.setFont("Helvetica-Bold", 10)
                c.drawString(35, y_position, title)
                y_position -= 5

                # Vykreslenie tabuľky
                # Upravená pozícia, aby bola tabuľka vycentrovaná so 4 stĺpcami na prvých stranách
                table.drawOn(c, (A4[0] - tw) / 4.4, y_position - th) 
                y_position -= (th + 30)

                return y_position
            
            # --- Inicializácia PDF a správa stránok ---

            # Vyčistenie adresára
            directory = './Reports/Lego/'
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                except Exception:
                    pass

            output_filename = f'./Reports/Lego/EETS_LEGO_REP_{MM}2026.pdf'
            c = canvas.Canvas(output_filename, pagesize=A4)
            
            # Predpokladáme 2 strany, ak by tabuľky presiahli 2. stranu, číslovanie sa nemusí zhodovať
            TOTAL_PAGES = 3

            # --- Strana 1: Prerozdelenie mýta ---
            draw_page_elements(c, TOTAL_PAGES, "Detailná evidencia EETS", 1, formatted_datetime, MM, formatted_previous_year)

            # Dynamické rozmiestnenie blokov
            y_position = 690
            y_position = draw_section(c, "Vlastník: Granvia", table_data_GRANVIA, y_position)
            y_position = draw_section(c, "Vlastník: Zero Bypass Limited", table_data_ZBL, y_position)
            y_position = draw_section(c, "Celkom (PPP úseky) - Granvia + R7/D4", table_data_PPP, y_position)
            y_position = draw_section(c, "Vlastník: Štát", table_data_stat, y_position)
            y_position = draw_section(c, "Celkom - PPP + Štát", table_data_spolu, y_position)
            
            # Uloženie aktuálnej strany a vytvorenie novej strany pre Detailnú evidenciu EETS
            c.showPage()

            # --- Strana 2: Detailná evidencia EETS ---
            draw_page_elements(c, TOTAL_PAGES, "Detailná evidencia EETS", 2, formatted_datetime, MM, formatted_previous_year)

            # Vykreslenie detailnej tabuľky
            y_position = 690
            y_position = draw_section_z(c, "Detailná evidencia EETS", table_data_CO2, y_position)

            # Uloženie
            c.save()

            # Response
            with open(output_filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="EETS_LEGO_REP_{MM}2026.pdf"'
            return response

        if 'delete_procedure' in request.POST:
            MM = request.POST.get('MM')  # Get the value of MM from the form
            YYYY = request.POST.get('YYYY')  # Get the value of YYYY from the form
            procedure_sql = """
                DECLARE
                    o_result_code NUMBER;
                    o_error_message VARCHAR2(4000);
                BEGIN
                kdx_pkg_eets_lego_ppp_2025_3COMP.lego_drop_temporary_agg_tables(
                    o_result_code => o_result_code,
                    o_error_message => o_error_message,
                    i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
                );

                kdx_pkg_eets_lego_ppp_2025_3COMP.lego_del_kpbpm_by_trans_ar_mon(
                    o_result_code => o_result_code,
                    o_error_message => o_error_message,
                    i_date => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
                );

                kdx_pkg_eets_lego_ppp_2025_3COMP.lego_del_kspoi_by_trans_ar_mon(
                    o_result_code => o_result_code,
                    o_error_message => o_error_message,
                    i_date => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
                );
                END;
                """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(procedure_sql, MM=MM, YYYY=YYYY)
                con_DWH_REP_CRM.commit()  # Commit the changes
                    # print("Procedura spuštěna")
            messages.info(request, f"Vymazanie dat za: {MM}-{YYYY} dokončené")
            return HttpResponseRedirect(reverse('eets:DB_USER'))

        if 'delete_REMOVED_BILL_ID' in request.POST:
            TRUNCATE_sql = """TRUNCATE TABLE KDX_REMOVED_BILL_IDS
                """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(TRUNCATE_sql)
                con_DWH_REP_CRM.commit()  # Commit the changes
                    # print("Procedura spuštěna")
            messages.info(request, f"Vymazanie dat z tabulky KDX_REMOVED_BILL_IDS dokončené")
            return HttpResponseRedirect(reverse('eets:DB_USER'))
        
        if 'insert_REMOVED_BILL_ID' in request.POST:
            insert_sql = """
                        INSERT INTO kdx_removed_bill_ids (transaction_arrival_month, removed_bill_id)
                        SELECT to_date(TO_CHAR(ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -1), 'dd.mm.yyyy'), 'dd.mm.yyyy'), 
                             bill_id
                        FROM (
                        SELECT 
                            bill_id
                        FROM 
                            eets_maa.BILL 
                        WHERE bill_status_code != 10)
                        
                """

                        #                 INSERT INTO kdx_removed_bill_ids (transaction_arrival_month, removed_bill_id)
                        # SELECT to_date(TO_CHAR(ADD_MONTHS(TRUNC(Passage_month, 'MM'), -1), 'dd.mm.yyyy'), 'dd.mm.yyyy'), 
                        #     bill_id
                        # FROM (
                        # SELECT distinct
                        #     /*+ FULL(rte) PARALLEL(6) */
                        #     TRUNC(rte.OBU_TIMESTAMP, 'MM') AS Passage_month,
                        #     b.bill_id
                        # FROM eets_maa.EETS_RTE_ALL rte
                        #     inner join eets_maa.BILL_ITEM bi on bi.bill_item_id = rte.bill_item_id
                        #     inner join eets_maa.BILL b on b.bill_id = bi.bill_id
                        # where (b.ISSUE_DATE_TIME >= TRUNC(ADD_MONTHS(SYSDATE, -1), 'MM') 
                        #     AND b.ISSUE_DATE_TIME < TRUNC(ADD_MONTHS(SYSDATE, 1), 'MM') 
                        #     AND b.BILL_SESSION_ID IS NOT NULL AND b.BILL_ISSUER_CODE=20)   
                        #     and rte.obu_timestamp >= TRUNC(SYSDATE, 'MM')
                        # )

            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(insert_sql)
                con_DWH_REP_CRM.commit()  # Commit the changes
                    # print("Procedura spuštěna")
            messages.info(request, f"Naplnenie tabulky KDX_REMOVED_BILL_IDS dokončené")
            return HttpResponseRedirect(reverse('eets:DB_USER'))

        if 'run_procedure' in request.POST:
            MM = request.POST.get('MM')  # Get the value of MM from the form
            mydate = request.POST.get('mydate')  # Get the value of mydate from the form
            procedure_sql = """
                DECLARE
                    o_result_code NUMBER;
                    o_error_message VARCHAR2(4000);
                BEGIN
                    kdx_pkg_eets_lego_ppp_2025_3COMP.lego_prepare_kpbpm_agg (
                      o_result_code => o_result_code,
                      o_error_message => o_error_message,
                      i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY'),
                      i_date_from_0203_mm_yyyy => TO_DATE('03-' || :MM || '-2026', 'DD-MM-YYYY'),
                      i_parallel_degree => 6,
                      i_discount_calculated_on_from => TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY'),
                      i_discount_calculated_on_to => TO_DATE(:mydate, 'DD-MM-YYYY')
                    );
                    kdx_pkg_eets_lego_ppp_2025_3COMP.lego_insert_kpbpm (
                      o_result_code => o_result_code,
                      o_error_message => o_error_message,
                      i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY')
                    );
                    kdx_pkg_eets_lego_ppp_2025_3COMP.lego_prepare_kspoi_agg (
                      o_result_code => o_result_code,
                      o_error_message => o_error_message,
                      i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY'),
                      i_date_from_0203_mm_yyyy => TO_DATE('03-' || :MM || '-2026', 'DD-MM-YYYY'),
                      i_discount_calculated_on_from => TO_DATE('01-' || :MM || '-2026', 'DD-MM-YYYY'),
                      i_discount_calculated_on_to => TO_DATE(:mydate, 'DD-MM-YYYY'),
                      i_include_invoices_in_progress => 0
                    );
                END;
            """

            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(procedure_sql, MM=MM, mydate=mydate)
                con_DWH_REP_CRM.commit()  # Commit the changes
            # print("Procedura dokoncena")
            messages.info(request, f"Procedura dokoncena i_date_from_01_mm_yyyy => 01-{MM}-2026 a i_discount_calculated_on_to => {mydate}")
            return HttpResponseRedirect(reverse('eets:DB_USER'))

    con_DWH_REP_CRM.close()  # Close the connection

    context = {'dwh_lego_view':dwh_lego_view, 'dwh_lego_removed_bill':dwh_lego_removed_bill }
    return render(request, 'eets/lego_view.html', context)

#######################################################################
###### Schedule job ###################################################
def report_EETS_Lego():
    print('ahoj')

@login_required
def reports_View(request):
    return render(request, 'eets/reports_View.html')

#### Edit html Lego report ##########################################################
def report_eets_lego_html(request):

    head_info='EMS-EETS from DWH generating and sending PDF'
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'eets', 'static', 'json', 'jobs.json')

    with open(file_name, 'r') as file:
        json_inputs = json.load(file)

    emails = [email for json_input in json_inputs if json_input['model'] == 'EETS_Lego' for email in json_input['fields']['emails']]
    head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None
    body = [json_input['fields']['body'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None
    # username = [json_input['fields']['username'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None
    # password = [json_input['fields']['password'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None

    
    # print(body)
    rune = [json_input['fields']['run'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else {}

    # Načítanie pôvodných údajov
    original_inputs = [json_input for json_input in json_inputs if json_input['model'] == 'EETS_Lego']
    original_data = original_inputs[0]['fields'] if original_inputs else {}

    # Získanie pôvodných hodnôt
    original_emails = original_data.get('emails', [])
    original_rune = original_data.get('run', '')
    original_head = original_data.get('head', '')
    original_body = original_data.get('body', '')

    if request.method == 'POST':
        if 'emails' in request.POST:
            emails = request.POST['emails'].strip().split(',')
        if 'rune' in request.POST:
            rune = request.POST['rune']
        if 'head' in request.POST:
            head = request.POST['head']
        if 'body' in request.POST:
            body = request.POST['body']
        # if 'username' in request.POST:
        #     username = request.POST['username']
        # if 'password' in request.POST:
        #     password = request.POST['password']
            # body = body.replace('\\n', '\n')
        json_inputs = [json_input for json_input in json_inputs if json_input['model'] != 'EETS_Lego']
        json_inputs.append({
            'model': 'EETS_Lego',
            'fields': {
                'emails': emails,
                'run': rune,
                'head': head,
                'body':body,
                # 'username':username,
                # 'password':password,

            }
        })
        with open(file_name, 'w') as file:
            json.dump(json_inputs, file, indent=4)

        # Porovnanie s pôvodnými hodnotami a vybratie len zmien
        changes = {}
        if emails != original_emails:
            changes['emails'] = emails
        if rune != original_rune:
            changes['run'] = rune
        if head != original_head:
            changes['head'] = head
        if body != original_body:
            changes['body'] = body
        
        logger.info('Update job EETS_Lego ('+str(request.user)+') ' +str(changes))

        #planovac aktualizacia
        # Trigger the job
        from scheduler import reload_job_if_lego
        # Reload job pre EETS_Lego
        reload_job_if_lego('EETS_Lego', 'eets/static/json/jobs.json')


        return render(request, 'eets/eets_edit_job.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body, 'head_info':head_info})
    
    return render(request, 'eets/eets_edit_job.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body, 'head_info':head_info})

@login_required
def awr(request):
    import sys
    # https://varmarakesh.bitbucket.io/python/2015/05/23/Oracle-AWR-Using-Python.html
    # cursor = con_CISDB_STDBY.cursor()

    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()

    sql_awr_SNAP_ID = """
                        SELECT SNAP_ID,
                        DBID,
                        INSTANCE_NUMBER,
                        TO_CHAR(BEGIN_INTERVAL_TIME, 'YYYY-MM-DD HH24:MI') BEGIN_INTERVAL_TIME,
                        TO_CHAR(END_INTERVAL_TIME, 'YYYY-MM-DD HH24:MI') END_INTERVAL_TIME
                        FROM dba_hist_snapshot
                        WHERE BEGIN_INTERVAL_TIME > SYSDATE - 1
                        ORDER BY SNAP_ID desc,
                        INSTANCE_NUMBER 
                    """
 
    with con_EETSDB_STDBY.cursor() as cursor:
        cursor.execute(sql_awr_SNAP_ID)
        AWR = dictfetchall(cursor)
    
    if 'a' in request.GET and 'b' in request.GET:
        a=request.GET['a']
        b=request.GET['b']

        sql_awr_report = """
                        SELECT output FROM TABLE (dbms_workload_repository.awr_report_html(1125152219,1,:a,:b))
                        """
    
        with con_EETSDB_STDBY.cursor() as cursor:
            
            cursor.execute(sql_awr_report, {'a': a, 'b':b})
                #rows = cursor.fetchall()        
                #rows = namedtuplefetchall(cursor)
            awr_report2 = cursor.fetchall()
            # for awr_report in awr_report2:
            #     print(awr_report[0], end='')

        # print(connect)
        # print(awr_report)
       
        # if glob.glob(os.path.join("download_awr/a*")):
        # # if os.path.glob('*.html'):
        #     print(f'nasiels som')
        #     os.remove("download_awr/ar*")

        # files = glob.glob(os.path.join('download_awr/a*'))
        if glob.glob(os.path.join('work/templates/awr/*.html')): # It will give all csv files in folder
            files = glob.glob(os.path.join('work/templates/awr/*.html'))
            for file in files:
                os.remove(file)
    
        with open("work/templates/awr/awr.html", "w") as file:
            for item in awr_report2:
                file.write(f"{item[0]}\n")
            #     awr_report.write(str(awr_report[0]))
            # file.writelines(awr_report2[0])
    # cursor.close()
    # connection.close()           
    context = {'AWR': AWR} 
    return render(request,'eets/awr.html', context)

##################### jira ################

from django.http import JsonResponse
# from .jira_service import get_jira_connection
import os

from django.shortcuts import render
# from .jira_service import get_jira_connection

# def get_jira_issues(request):
#     jira = get_jira_connection()

#     jql_query = """
#     project = EMSW AND status != Resolved AND (
#         assignee = 5eb1ce73a4c57d0b8b0cb39e AND status != Closed
#     )
#     ORDER BY created DESC, assignee ASC
#     """

#     issues = jira.search_issues(jql_query, maxResults=50)
#     results = []

#     for issue in issues:
#         results.append({
#             "key": issue.key,
#             "summary": issue.fields.summary,
#             "status": issue.fields.status.name,
#             "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Nepridelené",
#             "created": issue.fields.created.split("T")[0],
#             "original_reporter": getattr(issue.fields, 'customfield_10160', 'Neznámy'),
#             "planned_release": getattr(issue.fields, 'customfield_10056', 'Nezadané')
#         })

#     # print("Získaný zoznam issues z EMSW")
#     return render(request, "eets/jira_issues.html", {"issues": results})

from django.shortcuts import render
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

# Jira Cloud nastavenia
JIRA_BASE_URL = os.getenv("JIRA_SERVER")  # napr. https://example.atlassian.net
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Proxy nastavenie (ak je potrebné)
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = 'login.microsoftonline.com,sharepoint.com'

def get_jira_issues(request):
    from dotenv import load_dotenv
    server = os.getenv("JIRA_SERVER")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    proxies = {
        "http": "http://proxy.example.local:3128",
        "https": "http://proxy.example.local:3128"
    }

    headers = {
        "Accept": "application/json"
    }

    auth = (email, api_token)

    url = f"{server}/rest/api/3/search/jql"

    jql_query = """
    project = EMSW AND status != Resolved AND (
        assignee = 5eb1ce73a4c57d0b8b0cb39e AND status != Closed
    )
    ORDER BY created DESC, assignee ASC
    """
    

    params = {
        "jql": jql_query,
        "maxResults": 500,
        "fields": "summary,status,assignee,created,customfield_10160,customfield_10056"
    }


    response = requests.get(url, headers=headers, auth=auth, params=params, proxies=proxies)

    issues = []
    if response.status_code == 200:
        data = response.json()
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})

            # Získanie original_reporter
            original_reporter = fields.get("customfield_10160", "Neznámy")
            if isinstance(original_reporter, dict):
                original_reporter = original_reporter.get("displayName", "Neznámy")

            issues.append({
                "key": issue.get("key", "Neznáme"),
                "summary": fields.get("summary", "Bez popisu"),
                "status": fields.get("status", {}).get("name", "Neznámy"),
                "assignee": fields.get("assignee", {}).get("displayName", "Nepridelené"),
                "created": fields.get("created", "").split("T")[0],
                "original_reporter": original_reporter,
                "planned_release": fields.get("customfield_10056", "Nezadané")
            })
    else:
        print(f"Chyba: {response.status_code}")
        print(response.text)

    return render(request, "eets/jira_issues.html", {"issues": issues})


def get_jira_emsw(request):
    from dotenv import load_dotenv
    import os
    import requests

    load_dotenv()

    server = os.getenv("JIRA_SERVER")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    proxies = {
        "http": "http://proxy.example.local:3128",
        "https": "http://proxy.example.local:3128"
    }

    headers = {
        "Accept": "application/json"
    }

    auth = (email, api_token)

    url = f"{server}/rest/api/3/search/jql"

    jql_query = """
    project = EMSW AND status != Resolved AND status != Closed
    ORDER BY created DESC, assignee ASC
    """

    params = {
        "jql": jql_query,
        "maxResults": 500,
        "fields": "summary,status,assignee,created,customfield_10160,customfield_10056"
    }

    response = requests.get(url, headers=headers, auth=auth, params=params, proxies=proxies)

    issues = []
    if response.status_code == 200:
        data = response.json()
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})

            # Získanie original_reporter
            original_reporter = fields.get("customfield_10160", "Neznámy")
            if isinstance(original_reporter, dict):
                original_reporter = original_reporter.get("displayName", "Neznámy")

            issues.append({
                "key": issue.get("key", "Neznáme"),
                "summary": fields.get("summary", "Bez popisu"),
                "status": fields.get("status", {}).get("name", "Neznámy"),
                "assignee": fields.get("assignee", {}).get("displayName", "Nepridelené"),
                "created": fields.get("created", "").split("T")[0],
                "original_reporter": original_reporter,
                "planned_release": fields.get("customfield_10056", "Nezadané")
            })
    else:
        print(f"Chyba: {response.status_code}")
        print(response.text)

    return render(request, "eets/jira_issues.html", {"issues": issues})

# projects = get_projects()
# print("Projekty dostupné cez API:")
# for p in projects.get("values", []):
#     print(f"{p['key']}: {p['name']}")
