from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import EDZDBUpdateForm
from django.contrib import messages
import cx_Oracle
from django.core.mail import EmailMessage
from django.shortcuts import render
import os, shutil
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import zipfile
import json
from work.models import EMS_DWHDB
from work.forms import EMSDWHDBUpdateForm
import mimetypes
from django.http import HttpResponse 
import logging
logger = logging.getLogger('my_app')  # Použite názov loggera, ktorý ste definovali



def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
# Create your views here.


@login_required
def edz(request):
    edz_db=EDZDB.objects.get(user=request.user)
    form_edz = EDZDBUpdateForm(request.POST, instance=edz_db)
    if form_edz.is_valid():
        form_edz.save()
        messages.success(request,'Your Profile has been updated!')
        form_edz = EDZDBUpdateForm(instance=edz_db)
    else:
        form_edz = EDZDBUpdateForm(instance=edz_db)

    ems_dwh_db=EMS_DWHDB.objects.get(user=request.user)
    form_ems_dwh = EMSDWHDBUpdateForm(request.POST or None, instance=ems_dwh_db)
    if form_ems_dwh.is_valid():
        form_ems_dwh.save()
        messages.success(request,'Your Profile has been updated!')
        form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)
    else:
        form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)

    context = { 'form_edz':form_edz, 'key': 'value', 'form_ems_dwh':form_ems_dwh}
    return render(request, 'edz/home_edz.html', context)

@login_required
def connect(request):
    print('ahoj edz')

    EDZ_DB=EDZDB.objects.get(user=request.user)
    con_EDZDB_STDBY = cx_Oracle.connect(EDZ_DB.EDZDB_username+"/"+EDZ_DB.EDZDB_password+"@"+EDZ_DB.EDZDB_hostname+":"+EDZ_DB.EDZDB_port+"/"+EDZ_DB.EDZDB_servicename)
    cursor = con_EDZDB_STDBY.cursor()
    print('connect'+' / ' +EDZ_DB.EDZDB_username+" / "+EDZ_DB.EDZDB_password )
    print(cursor)

    return render(request, 'edz/base.html', {'key': 'value'})

@login_required
def jobs(request):
    
    EDZ_DB=EDZDB.objects.get(user=request.user)
    con_EDZDB_STDBY = cx_Oracle.connect(EDZ_DB.EDZDB_username+"/"+EDZ_DB.EDZDB_password+"@"+EDZ_DB.EDZDB_hostname+":"+EDZ_DB.EDZDB_port+"/"+EDZ_DB.EDZDB_servicename)
    cursor = con_EDZDB_STDBY.cursor()
    
    job_s = ''
    # print('vysledok: '+job_s)\
    q = None

    sql_job = """SELECT * FROM(
                    SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME,
                    EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS
                    FROM edz_CO.JOB_INSTANCE ji
                    left join edz_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                    left join edz_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
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

    # print(q)
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
                FROM EDZ_CO.SCHEDULED_JOB job
                left join EDZ_CO.JOB_INSTANCE ins on job.LAST_JOB_INSTANCE_ID=ins.JOB_INSTANCE_ID
                left join EDZ_CO.EXECUTION_STATE_L exs on ins.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE and  exs.LANGUAGE_CODE='SK'
                order by CHANGED_ON desc
                    """
    cursor.execute(sql_all)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
    jobs_all = dictfetchall(cursor)

    if 'q' in request.GET:
        q=request.GET['q']

        sql_ROLE_NAME ="""SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME, EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS
                                FROM EDZ_CO.JOB_INSTANCE ji
                                left join EDZ_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                                left join EDZ_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
                                where
                                exs.LANGUAGE_CODE='SK'
                                and START_ACTION_DATETIME >= trunc(sysdate-7)
                                and JOB_NAME like :id
                                order by START_ACTION_DATETIME desc"""
        c = '%' + q + '%'
        cursor.execute(sql_ROLE_NAME, id=c)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
        job_s = dictfetchall(cursor)
            # print(job_s)
    # cursor.close()
    # connection.close()

    context = { 'jobe': jobs_error, 'job_s':job_s, 'q':q, 'jobs_all':jobs_all } #'job_s':job_s,
    return render(request,'edz/jobs.html', context)

@login_required
def edzdb(request):
    export = ''
    column_names_list = ''
    q = None

    if 'q' in request.GET:
        q=request.GET['q']

        EDZ_DB=EDZDB.objects.get(user=request.user)
        con_EDZDB_STDBY = cx_Oracle.connect(EDZ_DB.EDZDB_username+"/"+EDZ_DB.EDZDB_password+"@"+EDZ_DB.EDZDB_hostname+":"+EDZ_DB.EDZDB_port+"/"+EDZ_DB.EDZDB_servicename)
        cursor = con_EDZDB_STDBY.cursor()
        sql_query =q

        cursor.execute(sql_query)
            # export1 = cursor.description
        column_names_list = [x[0] for x in cursor.description]
            # export = dictfetchall(cursor)
            

            # cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
        export = cursor.fetchall()
            # print(export)

    context = {'export':export, 'column_names_list':column_names_list, 'q':q }
    return render(request, 'edz/edzdb.html', context)

@login_required
def pos(request):
    EDZ_DB=EDZDB.objects.get(user=request.user)
    con_EDZDB_STDBY = cx_Oracle.connect(EDZ_DB.EDZDB_username+"/"+EDZ_DB.EDZDB_password+"@"+EDZ_DB.EDZDB_hostname+":"+EDZ_DB.EDZDB_port+"/"+EDZ_DB.EDZDB_servicename)
    cursor = con_EDZDB_STDBY.cursor()
    
    sql_poss = """select 
                    po.pos_id, po.pos_number, po.pos_name, po.priority, rp.retail_partner_name, po.retail_partner_id, po.pos_type_code, typ.POS_TYPE_NAME
                    from 
                    edz_co.retail_partner rp
                    left join edz_co.pos po on rp.retail_partner_id = po.retail_partner_id
                    left join edz_co.pos_type_l typ on po.POS_TYPE_CODE=typ.POS_TYPE_CODE
                    where typ.LANGUAGE_CODE='SK'
                    order by po.pos_number
                    """
    cursor.execute(sql_poss)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
    pos_all = dictfetchall(cursor)
    
    pos_input = None
    x = None
    y = None
    query = None
    
    if 'posid' in request.GET and 'x' in request.GET and request.GET['y'] =='' :
        x = request.GET['x']
        y = None
        pos_input = request.GET['posid']
        
        sql_x="""select 
                    rp.retail_partner_name,
                    po.pos_number,
                    po.pos_name,
                    pay.payment_amount,
                    met.PAYMENT_METHOD_NAME,
                    --pay.date_of_payment,
                    CAST(FROM_TZ(CAST(pay.date_of_payment AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as date_of_payment,
                    pay.variable_symbol,
                    pay.pos_operator_username,
                    pay.PAYMENT_ID
                    from 
                    edz_co.retail_partner rp
                    left join edz_co.pos po on rp.retail_partner_id = po.retail_partner_id
                    left join edz_ar.payment pay on pay.cash_box_id like CONCAT( po.pos_number ,'%')
                    left join edz_ar.payment_method_l met on pay.payment_method_code = met.PAYMENT_METHOD_CODE and met.language_code = 'SK'
                    where po.POS_NUMBER=:cd
                    and pay.date_of_payment>= to_date(:cd, 'DD-MM-YYYY HH24:MI:SS')
                    order by date_of_payment desc
        
                """
        # data = [{'cd' : x}, {'cd': 2}, {'cd': 3}]
        data = [pos_input, x]
        cursor.execute(sql_x, data)
        query = dictfetchall(cursor)
    elif 'posid' in request.GET and 'y' in request.GET and request.GET['x'] =='' :
        x = None
        y = request.GET['y']
        pos_input = request.GET['posid']
        
        sql_x="""select 
                    rp.retail_partner_name,
                    po.pos_number,
                    po.pos_name,
                    pay.payment_amount,
                    met.PAYMENT_METHOD_NAME,
                    --pay.date_of_payment,
                    CAST(FROM_TZ(CAST(pay.date_of_payment AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as date_of_payment,
                    pay.variable_symbol,
                    pay.pos_operator_username,
                    pay.PAYMENT_ID
                    from 
                    edz_co.retail_partner rp
                    left join edz_co.pos po on rp.retail_partner_id = po.retail_partner_id
                    left join edz_ar.payment pay on pay.cash_box_id like CONCAT( po.pos_number ,'%')
                    left join edz_ar.payment_method_l met on pay.payment_method_code = met.PAYMENT_METHOD_CODE and met.language_code = 'SK'
                    where po.POS_NUMBER=:cd
                    and pay.date_of_payment <= to_date(:cd, 'DD-MM-YYYY HH24:MI:SS')
                    order by date_of_payment desc
        
                """
        # data = [{'cd' : x}, {'cd': 2}, {'cd': 3}]
        data = [pos_input, y]
        cursor.execute(sql_x, data)
        query = dictfetchall(cursor)
        
    elif 'posid' in request.GET and 'x' in request.GET and 'y' in request.GET :
        x=request.GET['x']
        y=request.GET['y']
        pos_input = request.GET['posid']
        
        sql_x="""select 
                    rp.retail_partner_name,
                    po.pos_number,
                    po.pos_name,
                    pay.payment_amount,
                    met.PAYMENT_METHOD_NAME,
                    --pay.date_of_payment,
                    CAST(FROM_TZ(CAST(pay.date_of_payment AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as date_of_payment,
                    pay.variable_symbol,
                    pay.pos_operator_username,
                    pay.PAYMENT_ID
                    from 
                    edz_co.retail_partner rp
                    left join edz_co.pos po on rp.retail_partner_id = po.retail_partner_id
                    left join edz_ar.payment pay on pay.cash_box_id like CONCAT( po.pos_number ,'%')
                    left join edz_ar.payment_method_l met on pay.payment_method_code = met.PAYMENT_METHOD_CODE and met.language_code = 'SK'
                    where po.POS_NUMBER=:cd
                    and pay.date_of_payment >= to_date(:cd, 'DD-MM-YYYY HH24:MI:SS')
                    and pay.date_of_payment <= to_date(:cd, 'DD-MM-YYYY HH24:MI:SS')
                    order by date_of_payment desc
        
                """
        # data = [{'cd' : x}, {'cd': 2}, {'cd': 3}]
        data = [pos_input, x, y]
        cursor.execute(sql_x, data)
        query = dictfetchall(cursor)
    
    
    context = { 'pos_all': pos_all, 'query':query } 
    return render(request,'edz/pos.html', context)

# from django.core.mail import send_mail
def EDZ_bad_trans(request):
    # con_CISDB_STDBY = cx_Oracle.connect("DB_USER/DB_PASSWORD@db-host-b.internal.example.com:1521/cissrv_rdo")
    EDZ_DB=EDZDB.objects.get(user=request.user)
    con_EDZDB_STDBY = cx_Oracle.connect(EDZ_DB.EDZDB_username+"/"+EDZ_DB.EDZDB_password+"@"+EDZ_DB.EDZDB_hostname+":"+EDZ_DB.EDZDB_port+"/"+EDZ_DB.EDZDB_servicename)
    cursor = con_EDZDB_STDBY.cursor()

    sql_REJECTED_TRANSACTION = """Select *
                                from EDZ_FA.REJECTED_TRANSACTION
                                where DELETED_ON is NULL
                                ORDER BY TRANSACTION_DATA_ID
                                """
    with con_EDZDB_STDBY.cursor() as cursor:
        cursor.execute(sql_REJECTED_TRANSACTION)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        REJECTED_TRANSACTION = dictfetchall(cursor)

    if os.path.exists("download_trans/Top_5_best_criteria.txt"): 
        os.remove("download_trans/Top_5_best_criteria.txt")
        file_name = r"download_trans/Top_5_best_criteria.txt"
        with open(file_name, 'a') as f:
            f.write(str('Top 5 best-fit criteria'))
        # print('delete file')
    # else:
        # print("The file does not exist")
    # con_CISDB_STDBY = cx_Oracle.connect("DB_USER/DB_PASSWORD@db-host-b.internal.example.com:1521/cissrv_rdo")
    cursor = con_EDZDB_STDBY.cursor()

    # cursor = connections['cis_db'].cursor()

    cursor.callproc("dbms_output.enable")
    
    sqlCode = """
                declare
                ----------------------------------------------------------------------------------------------
                v_transaction_data_id       EDZ_fa.table_of_number_18_t := EDZ_fa.table_of_number_18_t(:cd);
                tid_to_display_count        number := 5;
                consider_deleted_definition number := 0;
                ----------------------------------------------------------------------------------------------
                type t is table of varchar2(4000);
                criteria_ok                t := t();
                criteria_bad               t := t();
                transaction_item_def_id    EDZ_fa.table_of_number_18_t := EDZ_fa.table_of_number_18_t();
                transaction_item_def_short EDZ_fa.table_of_varchar2_50_t := EDZ_fa.table_of_varchar2_50_t();
                oktab                      EDZ_fa.table_of_number_18_t := EDZ_fa.table_of_number_18_t();
                badtab                     EDZ_fa.table_of_number_18_t := EDZ_fa.table_of_number_18_t();
                val                        number;
                ok                         number;
                bad                        number;
                begin
                dbms_output.put_line('Top ' || tid_to_display_count ||
                                    ' best-fit criteria');
                dbms_output.new_line;
                -- transaction data loop
                for i in (select td.transaction_data_id, ft.accounting_datetime
                            from EDZ_fa.transaction_data td
                            left join EDZ_fa.financial_transaction ft
                                on ft.transaction_data_id = td.transaction_data_id
                            where td.transaction_data_id in
                                (select column_value from table(v_transaction_data_id))) loop
                    dbms_output.put_line(lpad('*', 100, '*'));
                    dbms_output.put_line(rpad(' ', 18, ' ') ||
                                        'check transaction_data_id ' ||
                                        i.transaction_data_id ||
                                        ', accounting datetime: ' ||
                                        to_char(EDZ_co.to_local_datetime(i.accounting_datetime)
                                                ,'dd.mm.yyyy'));
                    dbms_output.put_line(lpad('*', 100, '*'));
                    -- clear variables
                    transaction_item_def_id.delete;
                    criteria_ok.delete;
                    criteria_bad.delete;
                    transaction_item_def_short.delete;
                    oktab.delete;
                    badtab.delete;
                    -- transaction item def
                    for j in (select transaction_item_def_id
                                    ,transaction_item_def_short
                                    ,rownum ord
                                from EDZ_fa.transaction_item_def td
                                join EDZ_fa.transaction_def d
                            using (transaction_def_id)
                            where exists
                            (select 1.0
                                        from EDZ_fa.selection_criteria sc
                                    where sc.transaction_item_def_id =
                                            td.transaction_item_def_id)
                                and (deleted_on is null and consider_deleted_definition = 0 or
                                    consider_deleted_definition = 1)
                            
                            order by transaction_item_def_short) loop
                    -- initialize variables
                    transaction_item_def_id.extend(1);
                    transaction_item_def_id(transaction_item_def_id.count) := j.transaction_item_def_id;
                    transaction_item_def_short.extend(1);
                    transaction_item_def_short(transaction_item_def_short.count) := j.transaction_item_def_short;
                    criteria_ok.extend(1);
                    criteria_ok(criteria_ok.count) := '';
                    criteria_bad.extend(1);
                    criteria_bad(criteria_bad.count) := '';
                    ok := 0;
                    bad := 0;
                    -- criteria
                    for k in (select data_column_system_name
                                    ,'nvl(to_char(' || case upper(data_column_system_name)
                                        when 'OBU_OPERATION_TYPE_CODE' then
                                        'OBU_STOCK_OPERATION_CODE'
                                        else
                                        data_column_system_name
                                    end || '),''null'')' || ' in (' ||
                                    listagg('''' || nvl(to_char(criteria_value), 'null') || ''''
                                            ,', ') within group(order by criteria_value nulls last) || ')' criteria
                                    , data_column_system_name || case count(*)
                                        when 1 then
                                        ' = '
                                        else
                                        ' in ('
                                        end ||
                                        listagg(nvl(to_char(criteria_value), 'null'), ', ') within group(order by criteria_value nulls last) ||case
                                        count(*)
                                        when 1 then
                                        ''
                                        else
                                        ')'
                                    end disp_criteria
                                from EDZ_fa.selection_criteria sc
                                join EDZ_fa.data_column
                                using (data_column_code)
                                where sc.transaction_item_def_id =
                                    j.transaction_item_def_id
                                group by data_column_system_name
                                order by data_column_system_name) loop
                        begin
                        execute immediate 'select ' ||
                                            case upper(k.data_column_system_name)
                                            when 'OBU_OPERATION_TYPE_CODE' then
                                            'OBU_STOCK_OPERATION_CODE'
                                            else
                                            k.data_column_system_name
                                            end ||
                                            ' from EDZ_fa.transaction_data where transaction_data_id = ' ||
                                            i.transaction_data_id || ' and ' || k.criteria
                            into val;
                        criteria_ok(criteria_ok.count) := criteria_ok(criteria_ok.count) || case
                                                            when ok = 0 then
                                                            ''
                                                            else
                                                            chr(10)
                                                            end || '          ' || k.disp_criteria ||
                                                            ' --> ' || nvl(to_char(val), 'null');
                        ok := ok + 1;
                        exception
                        when no_data_found then
                            execute immediate 'select ' ||
                                            case upper(k.data_column_system_name)
                                                when 'OBU_OPERATION_TYPE_CODE' then
                                                'OBU_STOCK_OPERATION_CODE'
                                                else
                                                k.data_column_system_name
                                            end ||
                                            ' from EDZ_fa.transaction_data where transaction_data_id = ' ||
                                            i.transaction_data_id
                            into val;
                            criteria_bad(criteria_bad.count) := criteria_bad(criteria_bad.count) || case
                                                                when bad = 0 then
                                                                ''
                                                                else
                                                                chr(10)
                                                                end || '        x ' ||
                                                                k.disp_criteria || ' --> ' ||
                                                                nvl(to_char(val), 'null');
                            bad := bad + 1;
                        end;
                    end loop;
                    oktab.extend(1);
                    oktab(oktab.count) := ok;
                    badtab.extend(1);
                    badtab(badtab.count) := bad;
                    end loop;
                    -- display results
                    for i in (with b as
                                (select column_value bad, rownum rn from table(badtab)),
                                o as
                                (select column_value ok, rownum rn from table(oktab)),
                                tid as
                                (select column_value transaction_item_def_id, rownum rn
                                from table(transaction_item_def_id)),
                                tsh as
                                (select column_value transaction_item_def_short, rownum rn
                                from table(transaction_item_def_short))
                                select t.*, rownum ord
                                from (select ok
                                            ,bad
                                            ,rn
                                            ,transaction_item_def_short
                                            ,transaction_item_def_id
                                            ,td.deleted_on
                                            ,td.validity_start
                                            ,td.validity_end
                                        from b
                                        join o
                                        using (rn)
                                        join tid
                                        using (rn)
                                        join tsh
                                        using (rn)
                                        join EDZ_fa.transaction_item_def tid
                                        using (transaction_item_def_id, transaction_item_def_short)
                                        join EDZ_fa.transaction_def td
                                            on td.transaction_def_id = tid.transaction_def_id
                                        order by case
                                                    when ok + bad = 0 then
                                                    0
                                                    else
                                                    ok / (ok + bad)
                                                end desc
                                                ,ok + bad desc
                                                ,transaction_item_def_short
                                                ,deleted_on desc nulls first) t
                                where rownum <= tid_to_display_count) loop
                    dbms_output.put_line(case when i.ok + i.bad = 0 then '0%' else
                                        to_char(round(i.ok / (i.ok + i.bad) * 100)) || '%'
                                        end || ' ' || i.transaction_item_def_short ||
                                        ' (item id ' || i.transaction_item_def_id || '),' ||
                                        ' validity: ' ||
                                        to_char(EDZ_co.to_local_datetime(i.validity_start)
                                                ,'dd.mm.yyyy') || ' - ' ||
                                        nvl(to_char(EDZ_co.to_local_datetime(i.validity_end)
                                                    ,'dd.mm.yyyy')
                                            ,'...') || case when
                                        i.deleted_on is not null then
                                        ' deleted on: ' ||
                                        to_char(EDZ_co.to_local_datetime(i.deleted_on)
                                                ,'dd.mm.yyyy') else '' end);
                    if criteria_bad(i.rn) is not null then
                        dbms_output.put_line(criteria_bad(i.rn));
                    end if;
                    if criteria_ok(i.rn) is not null then
                        dbms_output.put_line(criteria_ok(i.rn));
                    end if;
                    end loop;
                end loop;
                end;
                """
    q = None
    q2 = None
    q3 = None
    if 'q' in request.GET:
        q=request.GET['q']
    if 'q2' in request.GET:
        q2=request.GET['q2']
    if 'q3' in request.GET:
        q3=request.GET['q3']
    # if 'q2' in request.GET:
    #     q=request.GET['q2']
    # if 'q3' in request.GET:
    #     q=request.GET['q3']
    
    data =[{'cd' : q}, {'cd': q2}, {'cd': q3}]
    # data = [{'cd' : 71194061}, {'cd': 64675259}]
    # cursor.execute(sqlCode, data)
    cursor.executemany(sqlCode, data)

    statusVar = cursor.var(cx_Oracle.NUMBER)
    lineVar = cursor.var(cx_Oracle.STRING)
    while True:
        cursor.callproc("dbms_output.get_line", (lineVar, statusVar))
        if statusVar.getvalue() != 0:
            break
        # l = str(statusVar.getvalue())
        m = lineVar.getvalue()
        # print (m)
        # print(type(m))

        file_name = r"download_trans/Top_5_best_criteria.txt"
        with open(file_name, 'a') as f:
            f.write(str(m)+ '\n')
        #     # f.write(str(l))
        #     f.writelines(str(m)
    folder_ = r"download_trans/Top_5_best_criteria.txt"

    p = open(folder_, 'r')
    file_content = p.read()
    p.close()

    # cursor.close()
    # connection.close()   
    
    context = { 'file_content':file_content, 'REJECTED_TRAN':REJECTED_TRANSACTION }
    # context = {  'REJECTED_TRAN':REJECTED_TRANSACTION }

    
    return render(request,'edz/transakce.html', context)

@login_required
def users(request):
    EDZ_DB=EDZDB.objects.get(user=request.user)
    con_EDZDB_STDBY = cx_Oracle.connect(EDZ_DB.EDZDB_username+"/"+EDZ_DB.EDZDB_password+"@"+EDZ_DB.EDZDB_hostname+":"+EDZ_DB.EDZDB_port+"/"+EDZ_DB.EDZDB_servicename)
    cursor = con_EDZDB_STDBY.cursor()

    sql_ = """SELECT POS_ID, POS_NUMBER, POS_NAME, pos.POS_TYPE_CODE, POS_TYPE_NAME, pos.RETAIL_PARTNER_ID, rp.RETAIL_PARTNER_NAME
                                    from edz_co.pos pos
                                    left join edz_co.POS_TYPE_L typ on pos.POS_TYPE_CODE=typ.POS_TYPE_CODE
                                    left join edz_co.retail_partner rp on pos.retail_partner_id = rp.retail_partner_id
                                    where /*pos.priority != '-1'
                                    and */ typ.LANGUAGE_CODE='SK'
                                    order by POS_NUMBER
                                """
    with con_EDZDB_STDBY.cursor() as cursor:
        cursor.execute(sql_)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        Poses = dictfetchall(cursor)
    users = ''
    if 'x' in request.GET and request.GET['y'] =='':
        
    # if x is not None and x != '' :
        x = request.GET['x']
        y = request.GET['y']

        sql_ROLE_NAME ="""SELECT
                                pos.pos_id,
                                ad.user_id,
                                ad.user_name,
                                ad.first_name,
                                ad.last_name,
                                ad.user_status_code,
                                USER_STATUS_NAME,
                                ad.selfcare_user_group_id,
                                CAST(from_tz(CAST(ad.creation_datetime AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) AS creation_datetime,
                                CAST(from_tz(CAST(ad.expiration_date AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) AS expiration_date,
                                CAST(from_tz(CAST(ad.deleted_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) AS deleted_on,
                                LISTAGG(rl.role_name || '; ') WITHIN GROUP(
                                    ORDER BY
                                        usr.user_id
                                ) as "ROLE"
                            FROM
                                edz_ac.user_detail    ad
                                LEFT JOIN edz_ac.user_in_role   usr ON ad.user_id = usr.user_id
                                LEFT JOIN edz_ac.role           rl ON usr.role_id = rl.role_id
                                LEFT JOIN edz_ac.user_in_pos    pos ON ad.user_id = pos.user_id
                                left join edz_AC.user_status_l stat on ad.USER_STATUS_CODE=stat.USER_STATUS_CODE
                            WHERE
                                POS_ID= :id
                                and stat.LANGUAGE_CODE='SK'
                            GROUP BY
                                pos.pos_id,
                                ad.user_id,
                                ad.first_name,
                                ad.last_name,
                                ad.user_status_code,
                                stat.USER_STATUS_NAME,
                                ad.selfcare_user_group_id,
                                ad.user_name,
                                ad.selfcare_user_group_id,
                                ad.creation_datetime,
                                ad.expiration_date,
                                ad.deleted_on
                            ORDER BY
                                creation_datetime DESC
                                """
        with con_EDZDB_STDBY.cursor() as cursor:
            # c = '%' + q + '%'
            cursor.execute(sql_ROLE_NAME, id=x)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            users = dictfetchall(cursor)
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_ROLE_NAME ="""SELECT
                                pos.pos_id,
                                ad.user_id,
                                ad.user_name,
                                ad.first_name,
                                ad.last_name,
                                ad.user_status_code,
                                USER_STATUS_NAME,
                                ad.selfcare_user_group_id,
                                CAST(from_tz(CAST(ad.creation_datetime AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) AS creation_datetime,
                                CAST(from_tz(CAST(ad.expiration_date AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) AS expiration_date,
                                CAST(from_tz(CAST(ad.deleted_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) AS deleted_on,
                                LISTAGG(rl.role_name || '; ') WITHIN GROUP(
                                    ORDER BY
                                        usr.user_id
                                ) as "ROLE"
                            FROM
                                edz_ac.user_detail    ad
                                LEFT JOIN edz_ac.user_in_role   usr ON ad.user_id = usr.user_id
                                LEFT JOIN edz_ac.role           rl ON usr.role_id = rl.role_id
                                LEFT JOIN edz_ac.user_in_pos    pos ON ad.user_id = pos.user_id
                                left join edz_AC.user_status_l stat on ad.USER_STATUS_CODE=stat.USER_STATUS_CODE
                            WHERE
                                USER_NAME like :usr
                                and stat.LANGUAGE_CODE='SK'
                            GROUP BY
                                pos.pos_id,
                                ad.user_id,
                                ad.first_name,
                                ad.last_name,
                                ad.user_status_code,
                                stat.USER_STATUS_NAME,
                                ad.selfcare_user_group_id,
                                ad.user_name,
                                ad.selfcare_user_group_id,
                                ad.creation_datetime,
                                ad.expiration_date,
                                ad.deleted_on
                            ORDER BY
                                creation_datetime DESC
                                """
        with con_EDZDB_STDBY.cursor() as cursor:
            c = '%' + y + '%'
            cursor.execute(sql_ROLE_NAME, usr=c)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            users = dictfetchall(cursor)

    context = { 'Poses':Poses, 'users':users }
    return render(request,'edz/users.html', context)

@login_required
def reports_View(request):
    return render(request, 'edz/reports_View.html')

@login_required
def dwh_control(request):
    import cx_Oracle
    # cis_db=CISDB.objects.get(user=request.user)
    EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()

    sql_logs = """select STEP, TO_CHAR(from_tz(CAST(STEP_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as STEP_DATE_TIME_CET
                  from EDZ_STA.v_dwh_load_status"""

    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_logs)
        dwh_logs = dictfetchall(cursor)
        
    # from datetime import datetime, timedelta
    # for item in dwh_logs:
    #     if item['STEP'] == 'STA_START':
    #         STA_START = item['STEP_DATE_TIME']
    #     elif item['STEP'] == 'STA_END':
    #         STA_END = item['STEP_DATE_TIME']
    #     if item['STEP'] == 'MAA_START':
    #         MAA_START = item['STEP_DATE_TIME']
    #     elif item['STEP'] == 'MAA_END':
    #         MAA_END = item['STEP_DATE_TIME']
    # Duration_STA = STA_END - STA_START
    # Duration_MAA = MAA_END - MAA_START
 

    sql_detail = """select ID_DWH_LOAD_DETAIL, /*SOURCE_SYSTEM_NAME, */ LOAD_NUMBER, PARTITION_ID, LOAD_STAGE, STATUS,
                    TO_CHAR(from_tz(CAST(DATE_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as DATE_FROM_CET,
                    TO_CHAR(from_tz(CAST(DATE_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as DATE_TO_CET,
                    TO_CHAR(from_tz(CAST(LOAD_START AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as LOAD_START_CET,
                    TO_CHAR(from_tz(CAST(LOAD_END AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as LOAD_END_CET,
                    round((LOAD_END - LOAD_START) * 24 * 60, 1) AS diff_minutes,
                    TABLE_NAME, COMMAND
                    from EDZ_STA.dwh_load_detail
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
                    FROM EDZ_STA.dwh_load_error order by ID_DWH_LOAD_ERROR desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_error)
        dwh_error = dictfetchall(cursor)

    sql_merge_tables = """
                        select 
                        LOAD_NUMBER,	/*SOURCE_SYSTEM_NAME,*/	PARTITION_ID,	IS_MERGED_FLAG,	
                        TO_CHAR(from_tz(CAST(MERGE_FINISHED_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as 
                        MERGE_FINISHED_DATETIME,	IS_PREPARED_TO_MERGE,	
                        IS_EXPORT_RUNNING_FLAG,	LAST_RUN_ERROR_MESSAGE
                        from EDZ_STA.dwh_merge_table
                        order by LOAD_NUMBER desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_merge_tables)
        dwh_merge = dictfetchall(cursor)

    sql_tables = """SELECT ext.*, CAST(FROM_TZ(CAST(LAST_RUN AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LAST_RUN_CET  FROM EDZ_STA.DWH_EXPORT_TABLE ext
                    order by LAST_RUN_CET desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_tables)
        dwh_tables = dictfetchall(cursor)

    context={'dwh_logs': dwh_logs, 'dwh_detail':dwh_detail, 'dwh_error':dwh_error, 'dwh_tables':dwh_tables, 'dwh_merge':dwh_merge }
    return render(request, 'edz/dwh_control.html', context)

@login_required
def dwhdb(request):
    export = ''
    column_names_list = ''
    q = None

    if 'q' in request.GET:
        q=request.GET['q']

        EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
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
    return render(request, 'edz/edzdb.html', context)

#:::::::::: REPORTS ::::::::::::::::::::::::::::::
def sql_crv_edz(request):
    sql_storage = '/Scripts/EDZ/'
    query = 'EDZ_CRV.sql'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = BASE_DIR + sql_storage

    filename = query
    filepath = path + query
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response

def report_edz_crv():
    EDZ_DB=EDZDB.objects.get(user=1)
    con_EDZDB_STDBY = cx_Oracle.connect(EDZ_DB.EDZDB_username+"/"+EDZ_DB.EDZDB_password+"@"+EDZ_DB.EDZDB_hostname+":"+EDZ_DB.EDZDB_port+"/"+EDZ_DB.EDZDB_servicename)
    cursor = con_EDZDB_STDBY.cursor()

    # settings date
    today = datetime.datetime.now() + relativedelta(months=-1)
    my = today.strftime("%m%Y")

    # Save Script
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query = 'EDZ_CRV.sql'
    sql_storage = '/Scripts/EDZ/'
    name_report='/Reports/EDZ/EDZ_CRV_'+my+'.xlsx'
    path = BASE_DIR + sql_storage
    filename = path + query

    # odmazanie suborov
    directory = BASE_DIR +'/Reports/EDZ/'
    for file_name in os.listdir(directory):
        # construct full file path
        file = os.path.join(directory, file_name)
        if os.path.isfile(file):
            os.remove(file)

    # open script filename
    f = open(filename)
    full_sql = f.read()

    cursor.execute(full_sql)

    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    # Create a new excel
    df.to_excel(BASE_DIR+name_report, sheet_name='01a', index=False)
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    print("create report: 01a_"+my+".xlsx "+time)

    # zazipovanie
    # Define the source and destination file paths
    source_file = BASE_DIR+'\Reports\EDZ\EDZ_CRV_'+my+'.xlsx'
    destination_file = BASE_DIR+'\Reports\EDZ\EDZ_CRV_'+my+'.zip'

    # Create a zip file from the source file
    with zipfile.ZipFile(destination_file, 'w') as zipf:
        zipf.write(source_file, os.path.basename(source_file))

    with zipfile.ZipFile(destination_file, 'r') as zipf:
        zipf.extractall(BASE_DIR+'\Reports\EDZ')

    def load_orders(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        # email_addresses = [email for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky' for email in json_input['fields']['emails']]
            email_addresses = [email for json_input in json_inputs if json_input['model'] == 'EDZ_CRV' for email in json_input['fields'].get('emails', [])]
            return email_addresses
        
    def load_head(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'EDZ_CRV'][0] if json_inputs else None
        return head
    def load_body(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        body = [json_input['fields']['body'].replace('\\n', '\n') for json_input in json_inputs if json_input['model'] == 'EDZ_CRV'][0] if json_inputs else None
        return body
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/edz/static/json/jobs.json'
    # file_name = 'path/to/orders.json'
    email_addresses = load_orders(file_name)
    head = load_head(file_name)+" - " +my
    body = load_body(file_name)
    print(email_addresses)
    sender_email = "reports@example.com"
    receiver_email=email_addresses
    
    # Create an EmailMessage object and set headers
    message = EmailMessage(
        subject=head,
        body=body,
        from_email=sender_email,
        to=receiver_email,  # Pass the list of email addresses directly to the 'to' parameter
    )
    
    # Add attachment to email
    message.attach_file(destination_file)

    # Send email
    message.send()

    print('report poslany')

from edz.apps import EdzConfig
from apscheduler.schedulers.background import BackgroundScheduler
# from edz.scheduler import *
# from .scheduler import *
def report_edz_crv_view(request):
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'edz', 'static', 'json', 'jobs.json')

    with open(file_name, 'r') as file:
        json_inputs = json.load(file)

    # emails = [json_input['fields']['emails'] for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky']
    # print(emails)
    emails = [email for json_input in json_inputs if json_input['model'] == 'EDZ_CRV' for email in json_input['fields']['emails']]
    head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'EDZ_CRV'][0] if json_inputs else None
    body = [json_input['fields']['body'] for json_input in json_inputs if json_input['model'] == 'EDZ_CRV'][0] if json_inputs else None
    
    # print(body)
    rune = [json_input['fields']['run'] for json_input in json_inputs if json_input['model'] == 'EDZ_CRV'][0] if json_inputs else {}

    if request.method == 'POST':
        if 'emails' in request.POST:
            emails = request.POST['emails'].strip().split(',')
        if 'rune' in request.POST:
            rune = request.POST['rune']
        if 'head' in request.POST:
            head = request.POST['head']
        if 'body' in request.POST:
            body = request.POST['body']
            # body = body.replace('\\n', '\n')
        json_inputs = [json_input for json_input in json_inputs if json_input['model'] != 'EDZ_CRV']
        json_inputs.append({
            'model': 'EDZ_CRV',
            'fields': {
                'emails': emails,
                'run': rune,
                'head': head,
                'body':body
            }
        })
        with open(file_name, 'w') as file:
            json.dump(json_inputs, file, indent=4)
        
        #planovac aktualizacia
        # Trigger the job
        from .scheduler import reload_edz_crv_job
        reload_edz_crv_job()

        return render(request, 'edz/edz_crv.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body})
    return render(request, 'edz/edz_crv.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body})
def send_email(request):
    subject = "An email with attachment from Python"
    body = "Test - This is an email with attachment sent from Python"
    sender_email = "reports@example.com"
    receiver_email = "user@example.com"

    # Create an EmailMessage object and set headers
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=sender_email,
        to=[receiver_email],
    )

    message.send()

    print('report poslany')
    
#:::::::::: REPORTS Podania::::::::::::::::::::::::::::::
def sql_podania_edz(request):
    sql_storage = '/Scripts/EDZ/'
    query = 'EDZ_podania.sql'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = BASE_DIR + sql_storage

    filename = query
    filepath = path + query
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response

def report_edz_podania():
    logger.info("------------ START JOB EDZ_Podania")
    cursor = None
    con_EDZDB_STDBY = None

    try:
        print('here')
        EDZ_DB = EDZDB.objects.get(user=1)
        con_EDZDB_STDBY = cx_Oracle.connect(
            f"{EDZ_DB.EDZDB_username}/{EDZ_DB.EDZDB_password}@{EDZ_DB.EDZDB_hostname}:{EDZ_DB.EDZDB_port}/{EDZ_DB.EDZDB_servicename}"
        )
        cursor = con_EDZDB_STDBY.cursor()

        # settings date
        today = datetime.datetime.now() + relativedelta(months=-1)
        print(today)
        my = today.strftime("%m%Y")  # MMYYYY format

        # Save Script
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"Base directory: {BASE_DIR}")
        query = 'EDZ_podania.sql'
        sql_storage = 'Scripts/EDZ'
        name_report = f'Reports/EDZ/EDZ_Podania_{my}.xlsx'
        destination_file = os.path.join(BASE_DIR, name_report)
        path = os.path.join(BASE_DIR, sql_storage)
        filename = os.path.join(path, query)

        # Remove old files
        directory = os.path.join(BASE_DIR, 'Reports/EDZ')
        if not os.path.exists(directory):
            os.makedirs(directory)  # Create directory if it doesn't exist
        for file_name in os.listdir(directory):
            file = os.path.join(directory, file_name)
            if os.path.isfile(file):
                os.remove(file)

        # Open script filename
        # Open script filename
        with open(filename, 'r', encoding='utf-8') as f:
            full_sql = f.read()
            # full_sql = f.read()

        cursor.execute(full_sql)

        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(list(data), columns=columns)

        # Create a new Excel file
        df.to_excel(destination_file, sheet_name=my, index=False)

        # Check if the file was created
        if os.path.exists(destination_file):
            print(f"Report successfully created at: {destination_file}")
        else:
            print(f"Failed to create report at: {destination_file}")

        now = datetime.datetime.now()
        time = now.strftime("%H:%M:%S")
        print(f"create report: Edz_Podania_{my}.xlsx {time}")
        logger.info(f"create report: Edz_Podania_{my}.xlsx ")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con_EDZDB_STDBY' in locals():
            con_EDZDB_STDBY.close()

        # Load email addresses and message content
        def load_orders(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                json_inputs = json.load(file)
            email_addresses = [email for json_input in json_inputs if json_input['model'] == 'EDZ_Podania' for email in json_input['fields'].get('emails', [])]
            return email_addresses
        
        def load_head(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                json_inputs = json.load(file)
                head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None
                return head

        def load_body(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                json_inputs = json.load(file)
            body = [json_input['fields']['body'].replace('\\n', '\n') for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None
            return body
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_name = os.path.join(BASE_DIR, 'edz', 'static', 'json', 'jobs.json')

        # Load email addresses and message content
        email_addresses = load_orders(file_name)
        head = load_head(file_name) + " - " + my
        body = load_body(file_name)

        sender_email = "reports@example.com"
        receiver_email = email_addresses

        # Create an EmailMessage object and set headers
        message = EmailMessage(
            subject=head,
            body=body,
            from_email=sender_email,
            to=receiver_email,  # Pass the list of email addresses directly to the 'to' parameter
        )

        # Add attachment to email
        if os.path.exists(destination_file):
            message.attach_file(destination_file)
        else:
            print(f"File not found for attachment: {destination_file}")
            logger.error(f"File not found for attachment: {destination_file}")

        # Send email
        try:
            message.send()
            print('Report sent successfully')
            logger.info('------------ Report sent EDZ_Podania ---------------')
        except Exception as e:
            print(f"Failed to send email: {e}")
            logger.error(f"Failed to send email: {e}")
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        upload_file_to_sharepoint()


import datetime
from dateutil.relativedelta import relativedelta
import os
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

def upload_file_to_sharepoint():
    logger.info('------------ START upload EDZ_Podania Sharepoint')

    # Clear proxy settings for the Python process to bypass problematic proxies.
    # Adjust domains below if you need some hosts to go through your proxy.
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    # Alternatively, if you need to allow specific domains, you can set NO_PROXY:
    os.environ['NO_PROXY'] = 'login.microsoftonline.com,sharepoint.com'

    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_name = os.path.join(BASE_DIR, 'edz', 'static', 'json', 'jobs.json')

        def load_username(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                json_inputs = json.load(file)
                username = [json_input['fields']['username'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None
                return username

        def load_password(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                json_inputs = json.load(file)
                password = [json_input['fields']['password'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None
                return password

        username = load_username(file_name)
        password = load_password(file_name)
        site_url = "https://example.sharepoint.com/teams/example-team"
        relative_url = "/teams/example-team/Zkazncke%20podania/REPORT%20-%20počet%20podaní%20EDZ%20na%20KM"

        # Path to the file you want to upload
        today = datetime.datetime.now() + relativedelta(months=-1)
        my = today.strftime("%m%Y")
        file_path = os.path.join(BASE_DIR, 'Reports', 'EDZ', f'EDZ_Podania_{my}.xlsx')
        print(file_path)

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at {file_path} was not found.")
        
        print(f"Attempting to connect to SharePoint site: {site_url}")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at {file_path} was not found.")
        print(f"Attempting to connect to SharePoint site: {site_url}")

        # Authenticate with SharePoint
        ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
        print("Successfully authenticated with SharePoint.")

        # Get the target folder
        folder = ctx.web.get_folder_by_server_relative_url(relative_url)
        ctx.load(folder)
        ctx.execute_query()
        print(f"Folder '{relative_url}' loaded successfully.")

        # Upload the file
        with open(file_path, 'rb') as content_file:
            file_name = os.path.basename(file_path)
            upload_result = folder.upload_file(file_name, content_file.read()).execute_query()
        print(f"File '{upload_result.serverRelativeUrl}' uploaded successfully to SharePoint.")

    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    logger.info('------------ END JOB EDZ_Podania ----------')

def report_edz_podania_html(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'edz', 'static', 'json', 'jobs.json')

    with open(file_name, 'r') as file:
        json_inputs = json.load(file)

    emails = [email for json_input in json_inputs if json_input['model'] == 'EDZ_Podania' for email in json_input['fields']['emails']]
    head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None
    body = [json_input['fields']['body'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None
    username = [json_input['fields']['username'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None
    password = [json_input['fields']['password'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else None

    
    # print(body)
    rune = [json_input['fields']['run'] for json_input in json_inputs if json_input['model'] == 'EDZ_Podania'][0] if json_inputs else {}

    if request.method == 'POST':
        if 'emails' in request.POST:
            emails = request.POST['emails'].strip().split(',')
        if 'rune' in request.POST:
            rune = request.POST['rune']
        if 'head' in request.POST:
            head = request.POST['head']
        if 'body' in request.POST:
            body = request.POST['body']
        if 'username' in request.POST:
            username = request.POST['username']
        if 'password' in request.POST:
            password = request.POST['password']
            # body = body.replace('\\n', '\n')
        json_inputs = [json_input for json_input in json_inputs if json_input['model'] != 'EDZ_Podania']
        json_inputs.append({
            'model': 'EDZ_Podania',
            'fields': {
                'emails': emails,
                'run': rune,
                'head': head,
                'body':body,
                'username':username,
                'password':password,

            }
        })
        with open(file_name, 'w') as file:
            json.dump(json_inputs, file, indent=4)

        #planovac aktualizacia
        # Trigger the job
        from scheduler import reload_job_if_edz_podania
        reload_job_if_edz_podania('EDZ_Podania', 'edz/static/json/jobs.json')

        return render(request, 'edz/edz_crv.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body, 'username':username, 'password':password})
    
    return render(request, 'edz/edz_crv.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body, 'username':username, 'password':password})