# import time
from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
from .models import EETSDB, SAIDAMDDB, PROXYDB
# from django.contrib import messages
# from django.http import HttpResponseRedirect
# from django.urls import reverse
# from .forms import *
# from work.models import EMS_DWHDB
# from work.forms import EMSDWHDBUpdateForm
import os
# import logging
# logger = logging.getLogger(__name__)

# from django.contrib import messages
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
# #########################
# #### EMAIL ####
from django.core.mail import EmailMessage

# # Send email ----------------------------------------------------
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import cx_Oracle
from datetime import datetime

import logging

# Získajte logger
logger = logging.getLogger('my_app')  # Použite názov loggera, ktorý ste definovali

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')



def Rating_job():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Získajte aktuálny čas
    logger.info("---------- Start generovania jobu Rating_job (kazde 4 hodiny od 00:30). " )  # Zaznamenajte správu do info.log

    EETS_DB=EETSDB.objects.get(user=1)
    con_EETSDB_STDBY = cx_Oracle.connect(EETS_DB.EETSDB_username+"/"+EETS_DB.EETSDB_password+"@"+EETS_DB.EETSDB_hostname+":"+EETS_DB.EETSDB_port+"/"+EETS_DB.EETSDB_servicename)
    cursor = con_EETSDB_STDBY.cursor()
    print('connect EETSDB')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Control time: {now}")
    
    sql_ack_None = """
        select TO_CHAR(FROM_TZ(CAST(obu_timestamp AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Zurich', 'YYYY-MM-DD HH24')  ROK_MES_HOD,
        v.EETS_PROVIDER_ID,ep.PROVIDER_ABBREVIATION,
        /*round(sum(rtee.UNITS_USED),0) KM,*/
        sum(decode(rtee.toll_event_type_code,1,1,2,-1,3,1)) MT
        /*--round(sum(rtee.PRICE_AMOUNT),0) EUR*/
        from EETS_BE.EETS_RTE rtee
        left join EETS_ECM.VEHICLE v on v.VEHICLE_ID=rtee.VEHICLE_ID
        left join EETS_ECM.EETS_PROVIDER ep on ep.EETS_PROVIDER_ID=rtee.EETS_PROVIDER_ID
        where 
        FROM_TZ(CAST(OBU_TIMESTAMP AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Zurich' > FROM_TZ(CAST(Sysdate -4/24 AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Zurich'
        group by TO_CHAR(FROM_TZ(CAST(obu_timestamp AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Zurich', 'YYYY-MM-DD HH24'),v.EETS_PROVIDER_ID,ep.PROVIDER_ABBREVIATION
        order by TO_CHAR(FROM_TZ(CAST(obu_timestamp AS TIMESTAMP), 'UTC') AT TIME ZONE 'Europe/Zurich', 'YYYY-MM-DD HH24'),v.EETS_PROVIDER_ID,ep.PROVIDER_ABBREVIATION
            """
    cursor.execute(sql_ack_None)
    TC_Rating_4h = dictfetchall(cursor)

    result_list = []
    send_email = False

    max_mts = {}
    for provider in ['WAG', 'TELEPASS', 'ITIS', 'T4E']:
        max_mts[provider] = max((item['MT'] for item in TC_Rating_4h if item.get('PROVIDER_ABBREVIATION') == provider), default=0)
    # max_mts['ITIS'] =0
    print(str('ITIS MAX VALUES (4h) = ')+str(max_mts.get('ITIS', 0)))  # Use get() to avoid KeyError
    print(str('TELEPASS MAX VALUES (4h) = ')+str(max_mts.get('TELEPASS', 0)))  # Use get() to avoid KeyError
    print(str('T4E MAX VALUES (4h) = ')+str(max_mts.get('T4E', 0)))  # Use get() to avoid KeyError
    print(str('WAG MAX VALUES (4h) = ')+str(max_mts.get('WAG', 0)))  # Use get() to avoid KeyError
    logger.info(str('ITIS MAX VALUES (4h) = ')+str(max_mts.get('ITIS', 0)))
    logger.info(str('TELEPASS MAX VALUES (4h) = ')+str(max_mts.get('TELEPASS', 0)))
    logger.info(str('T4E MAX VALUES (4h) = ')+str(max_mts.get('T4E', 0))) 
    logger.info(str('WAG MAX VALUES (4h) = ')+str(max_mts.get('WAG', 0)))


    result_list = []

    for provider, value in max_mts.items():
        if value == 0:
            result_list.append(f"<font color='red'>{provider} = 0 MT ocenenych za posledne 4h. </font>")

    if result_list:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = "EMS EETS TC RATING"
        body = "<b>Kontrola ocenovanie MT vsetkych TSP</b><br>" + '<br><b>'.join(result_list) + "</b><br><br>" + 'Skontrolovane v case: ' + now + "<br><br>Prosim o kontrolu v BO: <br><a href='https://bo.internal.example.com/rating/rerate/events/'> Ocenené mýtne udalosti</a><br><a href='https://bo.internal.example.com/rating/rerate/tolldatarecordeets/'> Mýtne udalosti EETS čakajúce na ocenenie</a><br><a href='https://bo.internal.example.com/ecm/eetsimport/?whitelist=True'> WhiteList</a>- bez WL od TSP sa nebudu ocenovat <br><br>V minulosti riesene v:<br> <a href='https://example.atlassian.net/browse/EMSW-443'>EMSW-443</a> <br><a href='https://example.atlassian.net/browse/EMSW-451'>EMSW-451</a> <br>Zabbix priprava: <a href='https://example.atlassian.net/browse/EMSC-464'>EMSC-464</a><br><br>EMS-EETS TC DB script: <br><br> "+sql_ack_None +" <br><br>S pozdravom <br>App User"
        logger.info(result_list)
        sender_email = "reports@example.com"
        # receiver_emails = ["SKT_IT_APP@example.sk", "user@example.com"]  # Add more recipients here
        receiver_emails = ["user@example.com"]  # Add more recipients here
        # receiver_emails = ["user@example.com"]  # Add more recipients here


        # Create a multipart message and set headers
        message = MIMEMultipart('alternative')  # Use 'alternative' to allow HTML content
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_emails)  # Join the list of recipient addresses with commas
        message["Subject"] = subject

        # Create a text part and an HTML part
        text_part = MIMEText("This is a plain text message.", 'plain')
        html_part = MIMEText(body, 'html')  # Use 'html' subtype to render HTML content

        # Add both parts to the message
        message.attach(text_part)
        message.attach(html_part)

        # Convert message to string
        text = message.as_string()

        # Log in to server using secure context and send email
        with smtplib.SMTP('smtp.example.local', 25) as server:
            # server.login(sender_email, password) - prec
            server.sendmail(sender_email, receiver_emails, text)  # Pass the list of recipient addresses
    logger.info('--------- Dokonceny job Rating_job (EMS EETS TC Control RATING). ')  # Zaznamenajte správu do info.log

#### Edit html Lego report ##########################################################
def report_eets_rating_html(request):
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'eets', 'static', 'json', 'jobs.json')

    head_info='EMS-EETS TC job control rating '

    with open(file_name, 'r') as file:
        json_inputs = json.load(file)

    emails = [email for json_input in json_inputs if json_input['model'] == 'EETS_RATING' for email in json_input['fields']['emails']]
    head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'EETS_RATING'][0] if json_inputs else None
    body = [json_input['fields']['body'] for json_input in json_inputs if json_input['model'] == 'EETS_RATING'][0] if json_inputs else None
    # username = [json_input['fields']['username'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None
    # password = [json_input['fields']['password'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None

    
    # print(body)
    rune = [json_input['fields']['run'] for json_input in json_inputs if json_input['model'] == 'EETS_RATING'][0] if json_inputs else {}

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
        json_inputs = [json_input for json_input in json_inputs if json_input['model'] != 'EETS_RATING']
        json_inputs.append({
            'model': 'EETS_RATING',
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

        #planovac aktualizacia
        # Trigger the job
        from scheduler import reload_job_if_rating
        # Reload job pre EETS_Lego
        reload_job_if_rating('EETS_RATING', 'eets/static/json/jobs.json')

        return render(request, 'eets/eets_edit_job.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body, 'head_info':head_info})
    
    return render(request, 'eets/eets_edit_job.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body, 'head_info':head_info})

###### Schedule job ###################################################
def report_EETS_Lego():
    logger.info("------------ START JOB report_EETS_Lego -----------")
    con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@scan-dwh.etc.example:1521/dwh")

    # priprava a vymazanie tabulky pred generovanim
    TRUNCATE_sql = """TRUNCATE TABLE KDX_REMOVED_BILL_IDS
                """
    with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(TRUNCATE_sql)
                con_DWH_REP_CRM.commit()  # Commit the changes
                    # print("Procedura spuštěna")
                print("Vymazanie dat z tabulky KDX_REMOVED_BILL_IDS dokončené")
                logger.info("Vymazanie dat z tabulky KDX_REMOVED_BILL_IDS dokončené")
    con_DWH_REP_CRM.close()
    #kontrola dat a pripadne naplnenie Bill id ktore zu z dalsieho mesiaca    
    insert_sql = """
                        INSERT INTO kdx_removed_bill_ids (transaction_arrival_month, removed_bill_id)
                        SELECT to_date(TO_CHAR(ADD_MONTHS(TRUNC(Passage_month, 'MM'), -1), 'dd.mm.yyyy'), 'dd.mm.yyyy'), 
                            bill_id
                        FROM (
                        SELECT distinct
                            /*+ FULL(rte) PARALLEL(6) */
                            TRUNC(rte.OBU_TIMESTAMP, 'MM') AS Passage_month,
                            b.bill_id
                        FROM eets_maa.EETS_RTE_ALL rte
                            inner join eets_maa.BILL_ITEM bi on bi.bill_item_id = rte.bill_item_id
                            inner join eets_maa.BILL b on b.bill_id = bi.bill_id
                        where (b.ISSUE_DATE_TIME >= TRUNC(ADD_MONTHS(SYSDATE, -1), 'MM') 
                            AND b.ISSUE_DATE_TIME < TRUNC(ADD_MONTHS(SYSDATE, 1), 'MM') 
                            AND b.BILL_SESSION_ID IS NOT NULL AND b.BILL_ISSUER_CODE=20)   
                            and rte.obu_timestamp >= TRUNC(SYSDATE, 'MM')
                        )
                """
    con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@scan-dwh.etc.example:1521/dwh")
    with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(insert_sql)
                con_DWH_REP_CRM.commit()  # Commit the changes
                    # print("Procedura spuštěna")
                print("Naplnenie tabulky KDX_REMOVED_BILL_IDS dokončené")
                logger.info("Naplnenie tabulky KDX_REMOVED_BILL_IDS dokončené")

    con_DWH_REP_CRM.close()
    # Start kontrola dat - spustenie procedury
    import datetime

    ### Get the previous month
    current_date = datetime.date.today()

    ### Get the previous month
    previous_month = current_date.replace(day=1) - datetime.timedelta(days=1)
    MM = previous_month.strftime('%m')
    YYYY = '2024'  # Get the value of YYYY from the form
    procedure_sql = """
        DECLARE
            o_result_code NUMBER;
            o_error_message VARCHAR2(4000);
        BEGIN
            kdx_pkg_eets_lego_ppp_2022.lego_drop_temporary_agg_tables(
            o_result_code => o_result_code,
            o_error_message => o_error_message,
            i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
            );
            kdx_pkg_eets_lego_ppp_2022.lego_del_kpbpm_by_trans_ar_mon(
            o_result_code => o_result_code,
            o_error_message => o_error_message,
            i_date => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
            );
            kdx_pkg_eets_lego_ppp_2022.lego_del_kspoi_by_trans_ar_mon(
            o_result_code => o_result_code,
            o_error_message => o_error_message,
            i_date => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
            );
        END;
        """
    con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@scan-dwh.etc.example:1521/dwh")
    
    with con_DWH_REP_CRM.cursor() as cursor:
        cursor.execute(procedure_sql, MM=MM, YYYY=YYYY)
        con_DWH_REP_CRM.commit()  # Commit the changes

    # start plnenia dat - spustenie procedury
    import datetime
    # Get the current date
    current_date = datetime.date.today()

    ### Get the previous month
    previous_month = current_date.replace(day=1) - datetime.timedelta(days=1)
    MM = previous_month.strftime('%m')
    first_day = current_date.replace(day=1)
    mydate = first_day.strftime("%d-%m-%Y")
    procedure_sql = """
        DECLARE
            o_result_code NUMBER;
            o_error_message VARCHAR2(4000);
        BEGIN
            kdx_pkg_eets_lego_ppp_2022.lego_prepare_kpbpm_agg (
                o_result_code => o_result_code,
                o_error_message => o_error_message,
                i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY'),
                i_date_from_0203_mm_yyyy => TO_DATE('03-' || :MM || '-2024', 'DD-MM-YYYY'),
                i_parallel_degree => 6,
                i_discount_calculated_on_from => TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY'),
                i_discount_calculated_on_to => TO_DATE(:mydate, 'DD-MM-YYYY')
            );
            kdx_pkg_eets_lego_ppp_2022.lego_insert_kpbpm (
                o_result_code => o_result_code,
                o_error_message => o_error_message,
                i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY')
            );
            kdx_pkg_eets_lego_ppp_2022.lego_prepare_kspoi_agg (
                o_result_code => o_result_code,
                o_error_message => o_error_message,
                i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY'),
                i_date_from_0203_mm_yyyy => TO_DATE('03-' || :MM || '-2024', 'DD-MM-YYYY'),
                i_discount_calculated_on_from => TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY'),
                i_discount_calculated_on_to => TO_DATE(:mydate, 'DD-MM-YYYY')
            );
        END;
    """

    con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@scan-dwh.etc.example:1521/dwh")
    with con_DWH_REP_CRM.cursor() as cursor:
        cursor.execute(procedure_sql, MM=MM, mydate=mydate)
        con_DWH_REP_CRM.commit()  # Commit the changes
    # print("Procedura dokoncena")
        print("Procedura dokoncena i_date_from_01_mm_yyyy => 01-"+MM+"-2024 a i_discount_calculated_on_to => "+mydate)
        logger.info("Procedura dokoncena i_date_from_01_mm_yyyy => 01-"+MM+"-2024 a i_discount_calculated_on_to => "+mydate)
    con_DWH_REP_CRM.close()
    

    # Generovanie PDF
    pdfmetrics.registerFont(TTFont('DejaVuSans', './eets/static/fonts/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('Arial Unicode MS', './eets/static/fonts/arial-unicode-ms.ttf'))
    
    from datetime import datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("Dátum vygenerovania: %d. %m. %Y %H:%M:%S")
    previous_month = current_datetime - relativedelta(months=1)
    formatted_previous = previous_month.strftime("%m/%Y")
    formatted_previous_month = previous_month.strftime("%Y")

    pdf_sql = """
            select * from V_EETS_LEGO_REP_01
            where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY')
            order by PASSAGEDATE_MONTHLY asc
            """
    con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@scan-dwh.etc.example:1521/dwh")
    with con_DWH_REP_CRM.cursor() as cursor:
        cursor.execute(pdf_sql, MM=MM)
        pdf_data = dictfetchall(cursor)

    filtered_data_granvia = list(filter(lambda x: x['OWNER_NAME'] == 'Granvia', pdf_data))
    sum_spolu_granvia = sum(row['SPOLU'] for row in filtered_data_granvia)
    
    filtered_data_zbl = list(filter(lambda x: x['OWNER_NAME'] == 'Zero Bypass Limited', pdf_data))
    sum_spolu_zbl = sum(row['SPOLU'] for row in filtered_data_zbl)

    filtered_data_stat = list(filter(lambda x: x['OWNER_NAME'] == 'Štát', pdf_data))
    sum_spolu_stat = round(sum(row['SPOLU'] or 0 for row in filtered_data_stat), 2)

    ppp_sql = """
            select PASSAGEDATE_MONTHLY, SUM(SPOLU) as SPOLU from V_EETS_LEGO_REP_01
            where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY')
            and OWNER_NAME in ('Granvia','Zero Bypass Limited')
            group by PASSAGEDATE_MONTHLY
            order by PASSAGEDATE_MONTHLY asc
            """
    with con_DWH_REP_CRM.cursor() as cursor:
        cursor.execute(ppp_sql, MM=MM)
        ppp_data = dictfetchall(cursor)
    sum_spolu_ppp = round(sum(row['SPOLU'] for row in ppp_data), 2)

    spolu_sql = """
            select PASSAGEDATE_MONTHLY, SUM(SPOLU) as SPOLU from V_EETS_LEGO_REP_01
            where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2024', 'DD-MM-YYYY')
            group by PASSAGEDATE_MONTHLY
            order by PASSAGEDATE_MONTHLY asc
            """
    with con_DWH_REP_CRM.cursor() as cursor:
        cursor.execute(spolu_sql, MM=MM)
        spolu_data = dictfetchall(cursor)
    sum_spolu = round(sum(row['SPOLU'] for row in spolu_data), 2)

    """Generates a PDF file with the provided content."""
    # domazanie obsahu
    directory = './Reports/Lego/'  # specify the directory path

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

    output_filename = './Reports/Lego/EETS_LEGO_REP_'+MM+'2024.pdf'
    c = canvas.Canvas(output_filename, pagesize=A4)
    c.drawImage("./eets/static/img/logo_myto.png", 35, 780, width=80, height=50)
    c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech

    # Set up the text for the information
    c.drawString(414, 800, "Číslo zostavy: EETS_LEGO_REP_01")
    c.drawString(503, 785, "PDF formát")
    c.drawString(385, 770, formatted_datetime)

    # Set up the font for the title and text
    c.setFont("Helvetica-Bold", 14)
    c.drawString(165, 750 , "Prerozdelenie mýta medzi vlastníkov ciest")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, 720, "Mýtne transakcie spracované za obdobie:")

    c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech
    c.drawString(250, 720, MM +'/' +formatted_previous_month)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, 680, "Vlastník:")

    c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech
    c.drawString(80, 680, "Granvia")
    #--------------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, 580, "Vlastník:")

    c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech
    c.drawString(80, 580, "Zero Bypass Limited")
    #-------------------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, 480, "Celkom (PPP úseky) - Granvia + R7/D4")
    #-------------------------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, 390, "Vlastník:")

    c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech
    c.drawString(80, 390, "Štát")
    #-------------------------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, 270, "Celkom - PPP + Štát")

# Granvia
    table_data_GRANVIA = [
        ["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"],
    ]
    for row in filtered_data_granvia:
        table_data_GRANVIA.append([row['PASSAGEDATE_MONTHLY'], f"{row['SPOLU']:,.2f}".replace(',', ' '), f"{row['SPOLU']:,.2f}".replace(',', ' ')])
    table_data_GRANVIA.append(['Celková suma:', f"{sum_spolu_granvia:,.2f}".replace(',', ' '), f"{sum_spolu_granvia:,.2f}".replace(',', ' ')])

# ZBL
    table_data_ZBL = [
        ["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"],
    ]
    for row in filtered_data_zbl:
        table_data_ZBL.append([row['PASSAGEDATE_MONTHLY'], f"{row['SPOLU']:,.2f}".replace(',', ' '), f"{row['SPOLU']:,.2f}".replace(',', ' ')])
    table_data_ZBL.append(['Celková suma:', f"{sum_spolu_zbl:,.2f}".replace(',', ' '), f"{sum_spolu_zbl:,.2f}".replace(',', ' ')])

# PPP
    table_data_PPP = [
        ["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"],
    ]
    for row in ppp_data:
        table_data_PPP.append([row['PASSAGEDATE_MONTHLY'], f"{row['SPOLU']:,.2f}".replace(',', ' '), f"{row['SPOLU']:,.2f}".replace(',', ' ')])
    table_data_PPP.append(['Celková suma:', f"{sum_spolu_ppp:,.2f}".replace(',', ' '), f"{sum_spolu_ppp:,.2f}".replace(',', ' ')])

# Stat
    table_data_stat = [
        ["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"],
    ]
    for row in filtered_data_stat:
        table_data_stat.append([row['PASSAGEDATE_MONTHLY'], "{:_}".format(row['SPOLU']).replace('_', ' ') if row['SPOLU'] is not None else '', "{:_}".format(row['SPOLU']).replace('_', ' ') if row['SPOLU'] is not None else ''])
    table_data_stat.append(['Celková suma:', "{:_}".format(sum_spolu_stat).replace('_', ' ') if sum_spolu_stat is not None else '', "{:_}".format(sum_spolu_stat).replace('_', ' ') if sum_spolu_stat is not None else ''])
# Celkom spolu
    table_data_spolu = [
        ["Mesiac prejazdu mýtneho úseku", "EETS", "SPOLU"],
    ]
    for row in spolu_data:
        table_data_spolu.append([row['PASSAGEDATE_MONTHLY'], "{:_}".format(row['SPOLU']).replace('_', ' ') if row['SPOLU'] is not None else '', "{:_}".format(row['SPOLU']).replace('_', ' ') if row['SPOLU'] is not None else ''])
    table_data_spolu.append(['Celková suma:', f"{sum_spolu:_}".replace('_', ' '), f"{sum_spolu:_}".replace('_', ' ')])
    # Define the column widths
    col_widths = [2.5*inch,  1.5*inch + 2.5*inch/2.54, 1.5*inch]  # Add a spacer column

    # Create the table
    table = Table(table_data_ZBL, colWidths=col_widths)
    table_gr = Table(table_data_GRANVIA, colWidths=col_widths)
    table_ppp = Table(table_data_PPP, colWidths=col_widths)
    table_stat = Table(table_data_stat, colWidths=col_widths)
    table_spolu = Table(table_data_spolu, colWidths=col_widths)
    
    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Arial Unicode MS'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align the entire table to the left
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (2, -1), 'Helvetica-Bold'),  # Make the last row's cells bold
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right-align the second column
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),  # Right-align the third column
        ('LEADING', (0, 0), (-1, -1), 5),  # Reduce the space between rows to 4 points
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Add a grid to the table
    ])

    table.setStyle(table_style)
    table_gr.setStyle(table_style)
    table_ppp.setStyle(table_style)
    table_stat.setStyle(table_style)
    table_spolu.setStyle(table_style)

    # Get the page dimensions
    table.wrapOn(c, 120, 800)
    table_gr.wrapOn(c, 120, 800)
    table_ppp.wrapOn(c, 120, 800)
    table_stat.wrapOn(c, 120, 800)
    table_spolu.wrapOn(c, 120, 800)

    # Calculate the table width
    table_width = sum(col_widths)
    table_gr.drawOn(c, (A4[0] - table_width) / 4.4, 635)
    table.drawOn(c, (A4[0] - table_width) / 4.4, 530)
    table_ppp.drawOn(c, (A4[0] - table_width) / 4.4, 430)
    table_stat.drawOn(c, (A4[0] - table_width) / 4.4, 335)
    table_spolu.drawOn(c, (A4[0] - table_width) / 4.4, 215)

    # Set the line color to red
    c.setStrokeColorRGB(1, 0, 0)

    # Draw a vertical line from (100, 100) to (100, 200)
    c.line(560, 140, 560, 830)
    c.line(35, 140, 560, 140)

    c.setFont("Arial Unicode MS", 7)  # Use a font that supports Czech
    c.drawString(448, 150, "Sumy sú uvedené v EUR bez DPH.")

    c.setFont("Arial Unicode MS", 6)  # Use a font that supports Czech
    text = """
    example, a.s., Westend Plazza, Lamačská cesta 3/B, 841 04 Bratislava, Slovenská republika
    IČO/ID Nr.: 44 500 734, DIČ/Tax ID Nr.: 2022712153, IČ DPH/VAT Nr.: SK2022712153
    Spoločnosť je zapísaná v Obchodnom registri Okresného súdu Bratislava I. v Odd.: Sa, vložka č.: 4646/B
    Company is registered at Companies Register of the District Court Bratislava I. in Section: Sa, Insert No.: 4646/B"""

    lines = [line for line in text.split('\n') if line.strip() != '']
    y = 130
    for line in lines:
        c.drawString(16, y, line)
        y -= 10  # adjust the y-coordinate for each line

    # cislo strany
    c.saveState()
    c.setFont("Arial Unicode MS", 7)
    page_info = "Strana (Page) %d/1" % (c.getPageNumber())
    c.drawRightString(550, 20, page_info)
    c.restoreState()
    c.showPage()
    c.save()


# report_EETS_Lego()

    def load_orders(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        email_addresses = [email for json_input in json_inputs if json_input['model'] == 'EETS_Lego' for email in json_input['fields'].get('emails', [])]
        return email_addresses
    
    def load_head(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
            head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None
            return head

    def load_body(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        body = [json_input['fields']['body'].replace('\\n', '\n') for json_input in json_inputs if json_input['model'] == 'EETS_Lego'][0] if json_inputs else None
        return body
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'eets', 'static', 'json', 'jobs.json')

    email_addresses = load_orders(file_name)
    head = load_head(file_name)+' ' +MM+"/2024 " #+ my
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

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # output_filename = './Reports/Lego/EETS_LEGO_REP_'+MM+'2024.pdf'
    destination_file = './Reports/Lego/EETS_LEGO_REP_'+MM+'2024.pdf'
    message.attach_file(destination_file)

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
    con_DWH_REP_CRM.close()

    print('report poslany')
    logger.info('report poslany')

    logger.info("------------ END JOB report_EETS_Lego -----------")
