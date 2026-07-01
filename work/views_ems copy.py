from django.shortcuts import render, redirect
from django.http import HttpResponse   # added
from django.contrib.auth.decorators import login_required
from project.settings import cx_Oracle
from .models import BILLDB, EMS_DWHDB
import mimetypes

import paramiko
from paramiko import SSHClient, SSHConfig
from zipfile import ZipFile
import os, shutil

import datetime
from datetime import date, time
import pandas as pd
from xlsxwriter import Workbook
import zipfile
from django.http import FileResponse
from io import BytesIO

from django.contrib import messages
from dateutil.relativedelta import relativedelta

from django.core.mail import EmailMessage

#::  PDF
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from django.http import HttpResponseRedirect
from django.urls import reverse

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

# Define SFTP server's hostname, port, username, and password
hostname = 'logarch.etc.example'
port = 22
username = 'app_user'
# password = 'Nove_heslo69!'
password = 'Lip23nican04'

import json

from .forms import BILLDBUpdateForm, EMSDWHDBUpdateForm


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@login_required
def home_ems(request):
    bill_db=BILLDB.objects.get(user=request.user)
    form_bill = BILLDBUpdateForm(request.POST or None, instance=bill_db)
    
    if form_bill.is_valid():
        form_bill.save()
        messages.success(request,'Your Profile has been updated!')
        form_bill = BILLDBUpdateForm(instance=bill_db)
    else:
        form_bill = BILLDBUpdateForm(instance=bill_db)

    ems_dwh_db=EMS_DWHDB.objects.get(user=request.user)
    form_ems_dwh = EMSDWHDBUpdateForm(request.POST or None, instance=ems_dwh_db)
    if form_ems_dwh.is_valid():
        form_ems_dwh.save()
        messages.success(request,'Your Profile has been updated!')
        form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)
    else:
        form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)

    context = { 'form_bill':form_bill, 'form_ems_dwh':form_ems_dwh}

    return render(request, 'base_ems.html', context)
# def home_ems(request):
#     bill_db=BILLDB.objects.get(user=request.user)
#     form_bill = BILLDBUpdateForm(request.POST, instance=bill_db)
    

#     ems_dwh_db=EMS_DWHDB.objects.get(user=request.user)
#     form_ems_dwh = EMSDWHDBUpdateForm(request.POST, instance=ems_dwh_db)
#     if form_bill.is_valid():
#         form_bill.save()
#         messages.success(request,'Your Profile has been updated!')
#         form_bill = BILLDBUpdateForm(instance=bill_db)
#     elif form_ems_dwh.is_valid():
#         form_ems_dwh.save()
#         messages.success(request,'Your Profile has been updated!')
#         form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)
#     else:
#         form_bill = BILLDBUpdateForm(instance=bill_db)
#         form_ems_dwh = EMSDWHDBUpdateForm(instance=ems_dwh_db)   
     


#     context = { 'form_bill':form_bill, 'form_ems_dwh':form_ems_dwh}   

#     return render(request, 'base_ems.html', context)

def reports_View(request):

    return render(request, 'ems/reports_View.html')

@login_required
def validacia(request):

    context = {}
    return render(request, 'ems/validacia_EMS.html', context)

@login_required
def jobs_ems(request):

 

    billdb=BILLDB.objects.get(user=request.user)
    decrypted = billdb.BILLDB_password
    print('b')
    print(decrypted)
    
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    # cursor = con_CISDB_STDBY.cursor()

    job_s = ''
    # print('vysledok: '+job_s)\
    q = None

    sql_job = """SELECT * FROM(
                    SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME,
                    EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS
                    FROM BILLIEN_CO.JOB_INSTANCE ji
                    left join BILLIEN_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                    left join BILLIEN_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
                    where
                    exs.LANGUAGE_CODE='SK' and START_ACTION_DATETIME >= trunc(sysdate-3)
                                   --and ji.SCHEDULED_JOB_ID=143
                    and ji.EXECUTION_STATE_CODE!=4
                    --and UNSUCCESSFULLY_PROCESSED_ITEMS>0
                    or EXPECTED_NUMBER_OF_ITEMS !=SUCCESSFULLY_PROCESSED_ITEMS and exs.LANGUAGE_CODE='SK' and START_ACTION_DATETIME >= trunc(sysdate-3)
                    order by START_ACTION_DATETIME desc)
                    --where rownum <=8
                    """
    with con_BILLDB_STDBY.cursor() as cursor:
        cursor.execute(sql_job)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
        jobs_error = dictfetchall(cursor)

    print(q)

    if 'q' in request.GET:
        q=request.GET['q']

        sql_ROLE_NAME ="""SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME, EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS
                                FROM BILLIEN_CO.JOB_INSTANCE ji
                                left join BILLIEN_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                                left join BILLIEN_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
                                where
                                exs.LANGUAGE_CODE='SK'
                                and START_ACTION_DATETIME >= trunc(sysdate-7)
                                and JOB_NAME like :id
                                order by START_ACTION_DATETIME desc"""
        with con_BILLDB_STDBY.cursor() as cursor:
            c = '%' + q + '%'
            cursor.execute(sql_ROLE_NAME, id=c)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            job_s = dictfetchall(cursor)
            # print(job_s)
    # cursor.close()
    # connection.close()

    context = { 'jobe': jobs_error, 'job_s':job_s, 'q':q } #'job_s':job_s,
    return render(request,'ems/jobs_ems.html', context)

@login_required
def ems_logs(request):
    # remove these print statements later
    # if request.method == "GET":
    #     os.startfile(r'\\fileserver.internal.example.com\billien\CIS')

    # if request.method == 'POST':
    #     os.startfile(r'\\fileserver.internal.example.com\billien\CIS')

    return render(request, 'ems/ems_logs.html') #{'fname' : request.user.username }

def EMSAAPP01_realtime_error(request):
    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/ems_logs/EMSAAPP01/'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "EMSAAPP01"
        parent_dir = BASE_DIR + '/ems_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "EMSAAPP01"
        parent_dir = BASE_DIR + '/ems_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + '/ems_logs/EMSAAPP01/'
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if 'EMSAAPP01_real' in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + '/ems_logs/EMSAAPP01/'
    try:
        with open(folder + 'EMSAAPP01_real_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL ErrorLogs from EMSAAPP01  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + '/ems_logs/EMSAAPP01/EMSAAPP01_real_ErrorLogs.txt'
    search_folder = filepath = BASE_DIR + '/ems_logs/EMSAAPP01/EMSAAPP01_realtime/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nEMSAAPP01//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /EMSAAPP01_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'EMSAAPP01_real_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/ems_logs/EMSAAPP01/' + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAAPP01_realtime_app(request):
    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/ems_logs/EMSAAPP01/'

    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "EMSAAPP01"
        parent_dir = BASE_DIR + '/ems_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "EMSAAPP01"
        parent_dir = BASE_DIR + '/ems_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + '/ems_logs/EMSAAPP01/'
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if 'EMSAAPP01_real' in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + '/ems_logs/EMSAAPP01/'
    try:
        with open(folder + 'EMSAAPP01_real_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL AppLogs from EMSAAPP01  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + '/ems_logs/EMSAAPP01/EMSAAPP01_real_AppLogs.txt'
    search_folder = filepath = BASE_DIR + '/ems_logs/EMSAAPP01/EMSAAPP01_realtime/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nEMSAAPP01//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /EMSAAPP01_AppLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'EMSAAPP01_real_AppLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/ems_logs/EMSAAPP01/' + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAAPP02_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAAPP02/'
    search_file = 'EMSAAPP02_realtime'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL ErrorLogs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAAPP02_realtime_app(request):
    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAAPP02/'
    search_file = 'EMSAAPP02_realtime'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL APPLogs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSBAPP01_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSBAPP01/'
    search_file = 'EMSBAPP01_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSBAPP01_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSBAPP01/'
    search_file = 'EMSBAPP01_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSBAPP02_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSBAPP02/'
    search_file = 'EMSBAPP02_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSBAPP02_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSBAPP02/'
    search_file = 'EMSBAPP02_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSCAPP01_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSCAPP01/'
    search_file = 'EMSCAPP01_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSCAPP01_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSCAPP01/'
    search_file = 'EMSCAPP01_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSCAPP02_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSCAPP02/'
    search_file = 'EMSCAPP02_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSCAPP02_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSCAPP02/'
    search_file = 'EMSCAPP02_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSDAPP01_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSDAPP01/'
    search_file = 'EMSDAPP01_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n '+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSDAPP01_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSDAPP01/'
    search_file = 'EMSDAPP01_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSDAPP02_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSDAPP02/'
    search_file = 'EMSDAPP02_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSDAPP02_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSDAPP02/'
    search_file = 'EMSDAPP02_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSISAPP01_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSISAPP01/'
    search_file = 'EMSISAPP01_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSISAPP01_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSISAPP01/'
    search_file = 'EMSISAPP01_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSISAPP02_realtime_error(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSISAPP02/'
    search_file = 'EMSISAPP02_realtime'
    name = 'Error'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSISAPP02_realtime_app(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSISAPP02/'
    search_file = 'EMSISAPP02_realtime'
    name = 'App'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'
    print (create_files)
    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/'

    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB01_bo_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB01_bo/'
    search_file = 'EMSAWEB01_bo_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB02_bo_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB02_bo/'
    search_file = 'EMSAWEB02_bo_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB01_pos_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB01_pos/'
    search_file = 'EMSAWEB01_pos_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB02_pos_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB02_pos/'
    search_file = 'EMSAWEB02_pos_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB01_cr_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB01_cr/'
    search_file = 'EMSAWEB01_cr_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB02_cr_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB02_cr/'
    search_file = 'EMSAWEB02_cr_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB01_fci_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB01_fci/'
    search_file = 'EMSAWEB01_fci_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB02_fci_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB02_fci/'
    search_file = 'EMSAWEB02_fci_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    # if isExist:
    #     shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB01_sc_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB01_sc/'
    search_file = 'EMSAWEB01_sc_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

def EMSAWEB02_sc_realtime_web(request):

    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key (you can disable this if you want to manually check the host key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh.connect(hostname, port, username, password)

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir

    top_storage = '/ems_logs/'
    storage = 'EMSAWEB02_sc/'
    search_file = 'EMSAWEB02_sc_realtime'
    name = 'Web'

    dir = filepath = BASE_DIR + top_storage + storage
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = storage
        parent_dir = BASE_DIR + top_storage
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # Open an SFTP session
    sftp = ssh.open_sftp()
    print('pristup')
    print(sftp)

    # Define the remote directory's path
    remote_directory_path = '/srv/archive/log/upload-by-smbfs/billien-ems/temp/' #'/srv/archive/log/upload-by-smbfs/billien-edz/realtime/EDZISAPP02/'
    print('ulozisko'+remote_directory_path)

    # Define the local directory's path
    local_directory_path = BASE_DIR + top_storage + storage
    # local_directory_path = os.listdir(r'\fileserver.internal.example.com\c$\Users\app_user\Downloads')
    print('localne ulozisko'+local_directory_path)

    # Get a list of all files in the remote directory
    files = sftp.listdir(remote_directory_path)
    print('sftp files')
    print(files)

    # Iterate over each file in the remote directory
    for file in files:
        # If the file's name contains "error", copy it from the SFTP server to the local machine
        # if 'EMSISAPP0' in file:
        if search_file in file:
            print('files')
            print(f'Copying {file}')
            # print(file)

            # Define the remote file's path
            remote_file_path = remote_directory_path+file
            print('remote_file_path')
            print(remote_file_path)
            # Define the local file's path
            local_file_path = local_directory_path+file
            print('local_file_path')
            print(local_file_path)
            # Copy the file from the SFTP server to the local machine
            # ulozi zip subor
            sftp.get(remote_file_path, local_file_path)

            # Ulozim si nazov priecinkov ktore su odzipovane
            unzip_file = local_file_path[:-4]
            print(unzip_file)

            # rozbali zip subor bez poslednych troch pismen
            zf = ZipFile(local_file_path, 'r')
            zf.extractall(local_file_path[:-4])
            zf.close()

            # vymaze zip subor
            print('vymazanie suboru')
            print(local_file_path)
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    # Close the SFTP session
    sftp.close()

    # Close the SSH client object
    ssh.close()

    # create txt file
    folder = filepath = BASE_DIR + top_storage + storage
    create_files = search_file+'_'+name+'.txt'

    try:
        with open(folder + create_files, 'w') as f:
            f.write('---------------------------------------------  ALL '+name+'Logs from '+storage+' ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_emsaapp01_log = BASE_DIR + top_storage + storage +create_files
    search_folder = filepath = BASE_DIR + top_storage + storage + search_file +'/realtime/'
    print ('search_folder')
    print (search_folder)
    # append log in text
    for filename in os.listdir(search_folder):
        # if filename.endswith('.log'):       # konciaci na .log
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if name in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( search_folder + filename), 'r', encoding="utf-8") as reader, open(folder_emsaapp01_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\n'+storage+'/  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                # print('copied /EMSAAPP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = create_files
    # Define the full file path
    filepath = BASE_DIR + top_storage + storage + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    if isExist:
        shutil.rmtree(search_folder)
    # Return the response value
    return response

# ::::::::::::::::::: REPORTS ::::::::::::::::::::::::::::::::::

@login_required
def report_Accounts_daily_BILLDB(request):

    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()

    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")
    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'Accounts_daily_BILLDB_A.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='Accounts_'

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_Accounts_daily_BILLDB(request):
    sql_storage = '/Scripts/Denne/'
    query = 'Accounts_daily_BILLDB_A.sql'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = BASE_DIR + sql_storage

    # ----download file ------------------
    # Define Django project base directory
    # Define text file name
    filename = query
    # Define the full file path
    # filepath = BASE_DIR + top_storage + storage + filename
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

def report_DB_CRISIS(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")
    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'DP_CRISIS_REPORT.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='DB_CRISIS_REPORT_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_DB_CRISIS(request):
    sql_storage = '/Scripts/Denne/'
    query = 'DP_CRISIS_REPORT.sql'
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

def report_Invoices(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'TOIS_Invoices_v14_param.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='Invoices_'
    
    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_Invoices(request):
    sql_storage = '/Scripts/Denne/'
    query = 'TOIS_Invoices_v14_param.sql'
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

def report_Accounts_all_active_BILLDB_zip(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")
    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'Accounts_ALL_Active_BILLDB.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='Accounts_ALL_Active_'
    # create folder
    path = BASE_DIR + reports +'/'
    folder= path = BASE_DIR + reports +'/'
    print(folder)
    isExist = os.path.exists(path)
    if not isExist: 
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")
    else:
        print('path exist')
    sql = BASE_DIR + sql_storage + query
    print(sql)

    # open script filename

    f = open(sql)

    full_sql = f.read()

    cur_billdb.execute(full_sql)

    columns = [desc[0] for desc in cur_billdb.description]

    data = cur_billdb.fetchall()

    df = pd.DataFrame(list(data), columns=columns)

    file = BytesIO()

    writer = pd.ExcelWriter(file, engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.book.close() # <--- change is here

    file.seek(0)

    # Create a zip file to store the Excel file

    zip_file = BytesIO()

    with zipfile.ZipFile(zip_file, 'w') as zipf:

        zipf.writestr('Accounts_ALL_Active_'+yesterday1+'.xlsx', file.read())

    zip_file.seek(0)

    # Create a FileResponse with the zip file content

    response = FileResponse(zip_file, as_attachment=True, filename='Accounts_ALL_Active_'+yesterday1+'.zip')

    response['Content-Type'] = 'application/zip'

    return response

def report_Accounts_all_active_BILLDB(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'Accounts_ALL_Active_BILLDB.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='Accounts_ALL_Active_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_Accounts_all_active_BILLDB(request):
    sql_storage = '/Scripts/Denne/'
    query = 'Accounts_ALL_Active_BILLDB.sql'
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

def report_OBUS_ALL_BILLDB(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'OBUS_ALL_BILLDB.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='OBUS_ALL_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def report_OBUS_ALL_BILLDB_zip(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'OBUS_ALL_BILLDB.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='OBUS_ALL_'

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")
    # create folder
    path = BASE_DIR + reports +'/'
    folder= path = BASE_DIR + reports +'/'
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The new directory is created!")

    # zip
    # zip
    with zipfile.ZipFile(path+'OBUS_ALL_'+yesterday1+'.zip', "w") as zf:

        with zf.open('OBUS_ALL_'+yesterday1+'.xlsx', "w") as buffer:

            with pd.ExcelWriter(buffer) as writer:

                df.to_excel(writer, index=False)
    # print(folder+name_rep+yesterday1+'.zip')            
    response = HttpResponse(open(folder+name_rep+yesterday1+'.zip', 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment;'+name_rep+yesterday1+'.zip'
    shutil.rmtree(folder)
    return response

def sql_OBUS_ALL_BILLDB(request):
    sql_storage = '/Scripts/Denne/'
    query = 'OBUS_ALL_BILLDB.sql'
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

def report_POS_CRISIS_REPORT_BILLDB(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'POS_CRISIS_REPORT_AUTO_v4.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='POS_CRISIS_REPORT_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_POS_CRISIS_REPORT_BILLDB(request):
    sql_storage = '/Scripts/Denne/'
    query = 'POS_CRISIS_REPORT_AUTO_v4.sql'
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

def report_Vyrubene_myto_kategorie(request):
    EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'Vyrubene_myto_kategorie.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='Vyrubene_myto_kategorie_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cursor.execute(full_sql)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_Vyrubene_myto_kategorie(request):
    sql_storage = '/Scripts/Denne/'
    query = 'Vyrubene_myto_kategorie.sql'
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

def report_Vyrubene_myto_krajiny(request):
    EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Denne/'
    query = 'Vyrubene_myto_krajiny.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='Vyrubene_myto_krajiny_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cursor.execute(full_sql)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_Vyrubene_myto_krajiny(request):
    sql_storage = '/Scripts/Denne/'
    query = 'Vyrubene_myto_krajiny.sql'
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

# tyzdenne
def report_REP_INACTIVITY_4M(request):
    EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Tyzdenne/'
    query = 'REP_INACTIVITY_4M.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='REP_INACTIVITY_4M_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cursor.execute(full_sql)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_REP_INACTIVITY_4M(request):
    sql_storage = '/Scripts/Tyzdenne/'
    query = 'REP_INACTIVITY_4M.sql'
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

def report_REP_INACTIVITY_6M_PRP(request):
    EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.date.today()
    dt = today.strftime("%Y%m%d")

    sql_storage = '/Scripts/Tyzdenne/'
    query = 'REP_INACTIVITY_6M_PRP.sql'
    reports = '/Reports/'+dt+'/'
    name_rep ='REP_INACTIVITY_6M_PRP_'

    yesterday = today - datetime.timedelta(days=1)
    yesterday1 = yesterday.strftime("%Y%m%d")

    sql = BASE_DIR + sql_storage + query
    print(sql)
    # open script filename
    f = open(sql)
    full_sql = f.read()
    cursor.execute(full_sql)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename='+name_rep+yesterday1+'.xlsx"'
    writer = pd.ExcelWriter(response, engine = 'xlsxwriter')
    #d1 and d2 are pandas dataframe 
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    return response

def sql_REP_INACTIVITY_6M_PRP(request):
    sql_storage = '/Scripts/Tyzdenne/'
    query = 'REP_INACTIVITY_6M_PRP.sql'
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

from openpyxl import load_workbook
def report_Mark_stat():
    logger.info("------------ START job marketing statistiky " )  # Zaznamenajte správu do info.log
    EMS_DWH=EMS_DWHDB.objects.get(user=1)
    print(EMS_DWH)
    con_BILLDB_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    print(con_BILLDB_STDBY)
    cursor = con_BILLDB_STDBY.cursor()
    
    # # 1 Drop Table if exists T_TMP_MKT_ROAD_USAGE_1
    cursor.execute('''declare n number(10);
                    begin
                    select count(*) into n from tab where tname='T_TMP_MKT_ROAD_USAGE_1';

                    if (n > 0) then 
                        execute immediate 
                        'DROP TABLE T_TMP_MKT_ROAD_USAGE_1';
                    end if;
                    end;''')
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    print("Table Deleted: T_TMP_MKT_ROAD_USAGE_1", time, " START")
    logger.info("Table Deleted: T_TMP_MKT_ROAD_USAGE_1")
    
    # 1 Create table T_TMP_MKT_ROAD_USAGE_1
    cursor.execute('''CREATE TABLE T_TMP_MKT_ROAD_USAGE_1 AS
                        SELECT
                        /*+ NO_INDEX(pass)*/
                        pass.VEHICLE_ID,
                        to_char(pass.OBU_LOCAL_TIME,'mm') AS MONTH,
                        s.ROAD_TYPE_CODE,
                        pass.OBU_NUMBER_OF_AXLES,
                        NVL(pass.DISCOUNT_RATE, 0) AS DISCOUNT_RATE,
                        SUM(DECODE(TOLL_EVENT_TYPE_CODE, 1, 1, 2, -1, 3, 1, 0)) AS Transaction_count,
                        SUM(pass.PRICE_AMOUNT) AS Transaction_amount,
                        SUM (UNITS_USED) AS Tolled_km,
                        SUM(NVL(DISCOUNT_AMOUNT, 0)) AS Discount_amount
                        FROM BILLIEN_MAA.RATED_TOLL_EVENT pass
                        JOIN BILLIEN_MAA.ROAD_SEGMENTS s ON pass.TOLL_SEGMENT_ID=s.TOLL_SEGMENT_ID
                        WHERE pass.OBU_TIMESTAMP >= CAST(FROM_TZ(CAST(ADD_MONTHS(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM'), -1/*pri ročnom -12*/) AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                        AND pass.OBU_TIMESTAMP < CAST(FROM_TZ(CAST(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM') AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                        AND pass.EXEMPT_FLAG=0
                        AND pass.TEST_CUSTOMER_FLAG=0
                        GROUP BY pass.VEHICLE_ID, to_char(pass.OBU_LOCAL_TIME,'mm'), s.ROAD_TYPE_CODE, pass.OBU_NUMBER_OF_AXLES, NVL(pass.DISCOUNT_RATE, 0)''')
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    print("Table Created: T_TMP_MKT_ROAD_USAGE_1", time)
    logger.info("Table Created: T_TMP_MKT_ROAD_USAGE_1")
    
    # 2 Drop Table if exists T_TMP_MKT_ROAD_USAGE_2
    cursor.execute('''declare n number(10);
                        begin
                        select count(*) into n from tab where tname='T_TMP_MKT_ROAD_USAGE_2';

                        if (n > 0) then 
                            execute immediate 
                            'DROP TABLE T_TMP_MKT_ROAD_USAGE_2';
                        end if;
                        end;''')
    print("Table Deleted: T_TMP_MKT_ROAD_USAGE_2", time)
    logger.info("Table Deleted: T_TMP_MKT_ROAD_USAGE_2")


    # 2 Create table T_TMP_MKT_ROAD_USAGE_2
    cursor.execute('''CREATE TABLE T_TMP_MKT_ROAD_USAGE_2 AS
                        SELECT
                        /*+ NO_INDEX(pass)*/
                        pass.VEHICLE_ID,
                        to_char(pass.OBU_LOCAL_TIME,'yyyy.mm.dd') AS PassageDate,
                        SUM(DECODE(TOLL_EVENT_TYPE_CODE, 1, 1, 2, -1, 3, 1, 0)) AS Transaction_count,
                        SUM(pass.PRICE_AMOUNT) AS Transaction_amount,
                        SUM (UNITS_USED) AS Tolled_km
                        FROM BILLIEN_MAA.RATED_TOLL_EVENT pass
                        JOIN BILLIEN_MAA.ROAD_SEGMENTS s ON pass.TOLL_SEGMENT_ID=s.TOLL_SEGMENT_ID
                        WHERE pass.OBU_TIMESTAMP >= CAST(FROM_TZ(CAST(ADD_MONTHS(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM'), -1/*pri ročnom -12*/) AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                        AND pass.OBU_TIMESTAMP < CAST(FROM_TZ(CAST(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM') AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                        AND pass.EXEMPT_FLAG=0
                        AND pass.TEST_CUSTOMER_FLAG=0
                        GROUP BY pass.VEHICLE_ID,to_char(pass.OBU_LOCAL_TIME,'yyyy.mm.dd')''')
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    print("Table Created: T_TMP_MKT_ROAD_USAGE_2", time)
    logger.info("Table Created: T_TMP_MKT_ROAD_USAGE_2")

    
    # 3 Drop Table if exists T_TMP_MKT_ROAD_USAGE_3
    cursor.execute('''declare n number(10);
                        begin
                        select count(*) into n from tab where tname='T_TMP_MKT_ROAD_USAGE_3';

                        if (n > 0) then 
                            execute immediate 
                            'DROP TABLE T_TMP_MKT_ROAD_USAGE_3';
                        end if;
                        end;''')
    print("Table Deleted: T_TMP_MKT_ROAD_USAGE_3", time)
    logger.info("Table Deleted: T_TMP_MKT_ROAD_USAGE_3")

    # 3 Create table T_TMP_MKT_ROAD_USAGE_3
    cursor.execute('''CREATE TABLE T_TMP_MKT_ROAD_USAGE_3 AS
                        SELECT
                        /*+ NO_INDEX(pass)*/
                        pass.VEHICLE_ID,
                        TRUNC(pass.OBU_LOCAL_TIME) AS Passage_date,
                        pass.TOLL_SEGMENT_ID AS Segment_ID,
                        SUM(DECODE(TOLL_EVENT_TYPE_CODE, 1, 1, 2, -1, 3, 1, 0)) AS Transaction_count,
                        SUM(pass.PRICE_AMOUNT) AS Transaction_amount
                        FROM BILLIEN_MAA.RATED_TOLL_EVENT pass
                        WHERE pass.OBU_TIMESTAMP >= CAST(FROM_TZ(CAST(ADD_MONTHS(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM'), -1/*pri ročnom -12*/) AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                        AND pass.OBU_TIMESTAMP < CAST(FROM_TZ(CAST(TRUNC(CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE), 'MM') AS TIMESTAMP), 'CET') AT TIME ZONE 'GMT' AS DATE)
                        AND pass.EXEMPT_FLAG=0
                        AND pass.TEST_CUSTOMER_FLAG=0
                        GROUP BY pass.VEHICLE_ID, TRUNC(pass.OBU_LOCAL_TIME), pass.TOLL_SEGMENT_ID''')
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    print("Table Created: T_TMP_MKT_ROAD_USAGE_3", time," END created tables")
    logger.info("Table Created: T_TMP_MKT_ROAD_USAGE_3 and END created tables")
    # # ---------- end created table --------------------------------------------------------
    # ---------- start created reports --------------------------------------------------------

    # settings date
    today = datetime.datetime.now() + relativedelta(months=-1)
    my = today.strftime("%m%Y")

    # Save Script
    # filename=r"C:\NEW\Scripts\Marketing_stat\1_BILLDB_a.sql"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query = '1_BILLDB_a.sql'
    sql_storage = '/Scripts/Marketing_stat/'
    name_report='/Reports/Marketing_stat/Marketingove_statistiky_'+my+'.xlsx'
    path = BASE_DIR + sql_storage
    filename = path + query

    # odmazanie suborov
    directory = BASE_DIR +'/Reports/Marketing_stat/'
    for file_name in os.listdir(directory):
        # construct full file path
        file = os.path.join(directory, file_name)
        if os.path.isfile(file):
            os.remove(file)
    
    # open script filename
    f = open(filename)
    full_sql = f.read()
    
    billdb=BILLDB.objects.get(user=1)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cur_billdb = con_BILLDB_STDBY.cursor()
    cur_billdb.execute(full_sql)

    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
       

    # Create a new excel
  
    df.to_excel(BASE_DIR+name_report, sheet_name='01a', index=False)
    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    print("create report: 01a_"+my+".xlsx "+time)
    logger.info("create report: 01a_"+my+".xlsx ")

    
    # GENERATE REPORT 01b
    query = '1_BILLDB_b.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_billdb.execute(full_sql)
    columns = [desc[0] for desc in cur_billdb.description]
    data = cur_billdb.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='01b', index=False)
        
    # GENERATE REPORT 02a
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '2_DWH_a.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='02a', index=False)

    # GENERATE REPORT 02b
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '2_DWH_b.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='02b', index=False)
        
    # GENERATE REPORT 02c
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '2_DWH_c.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='02c', index=False)
        
    # GENERATE REPORT 10a
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '10_DWH_a.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='10a', index=False)
        
    # GENERATE REPORT 10b
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '10_DWH_b.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='10b', index=False)
        
    # GENERATE REPORT 10c
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '10_DWH_c.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='10c', index=False)
        
    # GENERATE REPORT 10d
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '10_DWH_d.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='10d', index=False)
        
    # GENERATE REPORT 10d
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()
    query = '11_DWH_a.sql'
    filename = path + query
    f = open(filename)
    full_sql = f.read()
    cur_EMSDWH.execute(full_sql)
    columns = [desc[0] for desc in cur_EMSDWH.description]
    data = cur_EMSDWH.fetchall()
    df = pd.DataFrame(list(data), columns=columns)
    
    with pd.ExcelWriter(BASE_DIR+name_report, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='11a', index=False)
    logger.info("create last tab in excele 11a")
    
    # zazipovanie
    # Define the source and destination file paths
    source_file = BASE_DIR+'\Reports\Marketing_stat\Marketingove_statistiky_'+my+'.xlsx'
    destination_file = BASE_DIR+'\Reports\Marketing_stat\Marketingove_statistiky_'+my+'.zip'

    # Create a zip file from the source file
    with zipfile.ZipFile(destination_file, 'w') as zipf:
        zipf.write(source_file, os.path.basename(source_file))

    # If you want to unzip the file after zipping it, you can use the following code:
    # Unzip the file
    with zipfile.ZipFile(destination_file, 'r') as zipf:
        zipf.extractall(BASE_DIR+'\Reports\Marketing_stat')
        
    def load_orders(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        # email_addresses = [email for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky' for email in json_input['fields']['emails']]
        email_addresses = [email for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky' for email in json_input['fields'].get('emails', [])]
        return email_addresses
    def load_head(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky'][0] if json_inputs else None
        return head
    def load_body(file_name):
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
        body = [json_input['fields']['body'].replace('\\n', '\n') for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky'][0] if json_inputs else None
        return body
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/work/static/json/jobs.json'
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
    logger.info("------------- END Marketing Statistiky report poslany")

# ::::::::::::::::::: REPORTS END ::::::::::::::::::::::::::::::::::::::::::::
@login_required
def EMS_bd_ack(request):
    import cx_Oracle
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()

    sql_ack_None = """
                SELECT *
                FROM
                (SELECT bd.ede_log_id   AS bd_ede_log_id,
                    bd.integration_log_id AS bd_integration_log_id,
                    bd.ede_log_status_code
                    ||'-'
                    || bds.ede_log_status_name AS bd_ede_log_status,
                    bd.eets_provider_id
                    ||'-'
                    || p.PROVIDER_NUMBER
                    ||'-'
                    || p.provider_abbreviation    AS EETS_PROVIDER,
                    TO_CHAR( bd.apdu_identifier ) AS apdu_identifier,
                    --bd.created_on                 AS bd_created_on,
                    CAST(FROM_TZ(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_created_on,
                    --bd.exported_on                AS bd_exported_on,
                    CAST(FROM_TZ(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_exported_on,
                    --ack.created_on                AS ACK_CREATED_ON,
                    CAST(FROM_TZ(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_CREATED_ON,
                    24* (to_date( ack.created_on) - to_date(bd.exported_on )) diff_hours
                    
                FROM BILLIEN_ede.ede_log bd
                JOIN BILLIEN_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN BILLIEN_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN BILLIEN_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                AND bd.created_on >= trunc(sysdate-7, 'DD') 
                )
                --WHERE NVL(ack_created_on, bd_created_on+1) - bd_created_on > 2/24
                WHERE ACK_CREATED_ON is NULL
               
                ORDER BY bd_created_on desc
              """
    cursor.execute(sql_ack_None)
    ack_None = dictfetchall(cursor)
    x = None
    y = None
    
    if 'x' in request.GET and request.GET['y'] =='':        
        x = request.GET['x']
        y = request.GET['y']
        sql_x="""
            SELECT *
                FROM
                (SELECT bd.ede_log_id   AS bd_ede_log_id,
                    bd.integration_log_id AS bd_integration_log_id,
                    bd.ede_log_status_code
                    ||'-'
                    || bds.ede_log_status_name AS bd_ede_log_status,
                    bd.eets_provider_id
                    ||'-'
                    || p.PROVIDER_NUMBER
                    ||'-'
                    || p.provider_abbreviation    AS EETS_PROVIDER,
                    TO_CHAR( bd.apdu_identifier ) AS apdu_identifier,
                    --bd.created_on                 AS bd_created_on,
                    CAST(FROM_TZ(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_created_on,
                    --bd.exported_on                AS bd_exported_on,
                    CAST(FROM_TZ(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_exported_on,
                    --ack.created_on                AS ACK_CREATED_ON,
                    CAST(FROM_TZ(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_CREATED_ON,
                    --24* (to_date( ack.created_on) - to_date(bd.exported_on )) diff_hours
                    ROUND(24* (to_date( ack.created_on) - to_date(bd.created_on)),3) diff_hours,
                   ROUND((to_date(ack.created_on) - to_date(bd.created_on))*24*60,1) DIFF_MINUTES,
                   ROUND((to_date(ack.created_on) - to_date(bd.exported_on))*24*60*60,3) DIFF_SECONDS

                FROM BILLIEN_ede.ede_log bd
                JOIN BILLIEN_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN BILLIEN_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN BILLIEN_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                --AND bd.created_on              > sysdate - 3
                )
                WHERE BD_CREATED_ON > to_date(:datex, 'DD-MM-YYYY HH24:MI:SS')
                ORDER BY bd_created_on desc
        """
 
        with con_BILLDB_STDBY.cursor() as cursor:
            cursor.execute(sql_x, datex=x)
            ack = dictfetchall(cursor)
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_y="""
            SELECT *
                FROM
                (SELECT bd.ede_log_id   AS bd_ede_log_id,
                    bd.integration_log_id AS bd_integration_log_id,
                    bd.ede_log_status_code
                    ||'-'
                    || bds.ede_log_status_name AS bd_ede_log_status,
                    bd.eets_provider_id
                    ||'-'
                    || p.PROVIDER_NUMBER
                    ||'-'
                    || p.provider_abbreviation    AS EETS_PROVIDER,
                    TO_CHAR( bd.apdu_identifier ) AS apdu_identifier,
                    --bd.created_on                 AS bd_created_on,
                    CAST(FROM_TZ(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_created_on,
                    --bd.exported_on                AS bd_exported_on,
                    CAST(FROM_TZ(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_exported_on,
                    --ack.created_on                AS ACK_CREATED_ON,
                    CAST(FROM_TZ(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_CREATED_ON,
                    --24* (to_date( ack.created_on) - to_date(bd.exported_on )) diff_hours
                    ROUND(24* (to_date( ack.created_on) - to_date(bd.created_on)),3) diff_hours,
                   ROUND((to_date(ack.created_on) - to_date(bd.created_on))*24*60,1) DIFF_MINUTES,
                   ROUND((to_date(ack.created_on) - to_date(bd.created_on))*24*60*60,3) DIFF_SECONDS

                FROM billien_ede.ede_log bd
                JOIN billien_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN billien_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN billien_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                --AND bd.created_on              > sysdate - 3
                )
                WHERE BD_CREATED_ON < to_date(:datey, 'DD-MM-YYYY HH24:MI:SS')
                ORDER BY bd_created_on desc
        """
        with con_BILLDB_STDBY.cursor() as cursor:
            cursor.execute(sql_y, datey=y)
            ack = dictfetchall(cursor)
    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
            SELECT *
                FROM
                (SELECT bd.ede_log_id   AS bd_ede_log_id,
                    bd.integration_log_id AS bd_integration_log_id,
                    bd.ede_log_status_code
                    ||'-'
                    || bds.ede_log_status_name AS bd_ede_log_status,
                    bd.eets_provider_id
                    ||'-'
                    || p.PROVIDER_NUMBER
                    ||'-'
                    || p.provider_abbreviation    AS EETS_PROVIDER,
                    TO_CHAR( bd.apdu_identifier ) AS apdu_identifier,
                    --bd.created_on                 AS bd_created_on,
                    CAST(FROM_TZ(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_created_on,
                    --bd.exported_on                AS bd_exported_on,
                    CAST(FROM_TZ(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_exported_on,
                    --ack.created_on                AS ACK_CREATED_ON,
                    CAST(FROM_TZ(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_CREATED_ON,
                    --24* (to_date( ack.created_on) - to_date(bd.exported_on )) diff_hours
                    ROUND(24* (to_date( ack.created_on) - to_date(bd.created_on)),3) diff_hours,
                   ROUND((to_date(ack.created_on) - to_date(bd.created_on))*24*60,1) DIFF_MINUTES,
                   ROUND((to_date(ack.created_on) - to_date(bd.created_on))*24*60*60,3) DIFF_SECONDS

                FROM billien_ede.ede_log bd
                JOIN billien_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN billien_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN billien_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                --AND bd.created_on              > sysdate - 3
                )
                WHERE BD_CREATED_ON > to_date(:datex, 'DD-MM-YYYY HH24:MI:SS')
                        AND BD_CREATED_ON < to_date(:datey, 'DD-MM-YYYY HH24:MI:SS')
                ORDER BY bd_created_on desc
        """
        with con_BILLDB_STDBY.cursor() as cursor:
            cursor.execute(sql_xy, datex=x, datey=y)
            ack = dictfetchall(cursor)
    else:
        sql_ack = """
                SELECT *
                FROM
                (SELECT bd.ede_log_id   AS bd_ede_log_id,
                    bd.integration_log_id AS bd_integration_log_id,
                    bd.ede_log_status_code
                    ||'-'
                    || bds.ede_log_status_name AS bd_ede_log_status,
                    bd.eets_provider_id
                    ||'-'
                    || p.PROVIDER_NUMBER
                    ||'-'
                    || p.provider_abbreviation    AS EETS_PROVIDER,
                    TO_CHAR( bd.apdu_identifier ) AS apdu_identifier,
                    --bd.created_on                 AS bd_created_on,
                    CAST(FROM_TZ(CAST(bd.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_created_on,
                    --bd.exported_on                AS bd_exported_on,
                    CAST(FROM_TZ(CAST(bd.exported_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as bd_exported_on,
                    --ack.created_on                AS ACK_CREATED_ON,
                    CAST(FROM_TZ(CAST(ack.created_on AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_CREATED_ON,
                    --24* (to_date( ack.created_on) - to_date(bd.exported_on )) diff_hours
                    --ROUND(24* (to_date( ack.created_on) - to_date(bd.created_on)),3) diff_hours,
                   --ROUND((to_date(ack.created_on) - to_date(bd.created_on))*24*60,1) MINUTES,
                    ROUND((NVL(ack.created_on,bd.created_on)  -bd.created_on)*24*60, 1 ) || ' min' as DIFF_MINUTES
                   --ROUND((to_date(ack.created_on) - to_date(bd.created_on))*24*60*60,3) DIFF_SECONDS

                FROM billien_ede.ede_log bd
                JOIN billien_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN billien_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN billien_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                AND bd.created_on              > sysdate - 3
                )
                --WHERE NVL(ack_created_on, bd_created_on+1) - bd_created_on > 2/24
                ORDER BY bd_created_on desc
              """

        with con_BILLDB_STDBY.cursor() as cursor:
            cursor.execute(sql_ack)
            ack = dictfetchall(cursor)
 
    context = {'ack':ack, 'ack_None':ack_None}
    return render(request, 'ems/ems_bd_ack.html', context)

@login_required
def EMS_bad_trans(request):
    # con_CISDB_STDBY = cx_Oracle.connect("DB_USER/DB_PASSWORD@db-host-b.internal.example.com:1521/cissrv_rdo")
    import cx_Oracle
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()

    sql_REJECTED_TRANSACTION = """Select *
                                from BILLIEN_FA.REJECTED_TRANSACTION
                                where DELETED_ON is NULL
                                ORDER BY TRANSACTION_DATA_ID
                                """
    with con_BILLDB_STDBY.cursor() as cursor:
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
    cursor = con_BILLDB_STDBY.cursor()

    # cursor = connections['cis_db'].cursor()

    cursor.callproc("dbms_output.enable")
    
    sqlCode = """
                declare
                ----------------------------------------------------------------------------------------------
                v_transaction_data_id       billien_fa.table_of_number_18_t := billien_fa.table_of_number_18_t(:cd);
                tid_to_display_count        number := 5;
                consider_deleted_definition number := 0;
                ----------------------------------------------------------------------------------------------
                type t is table of varchar2(4000);
                criteria_ok                t := t();
                criteria_bad               t := t();
                transaction_item_def_id    billien_fa.table_of_number_18_t := billien_fa.table_of_number_18_t();
                transaction_item_def_short billien_fa.table_of_varchar2_50_t := billien_fa.table_of_varchar2_50_t();
                oktab                      billien_fa.table_of_number_18_t := billien_fa.table_of_number_18_t();
                badtab                     billien_fa.table_of_number_18_t := billien_fa.table_of_number_18_t();
                val                        number;
                ok                         number;
                bad                        number;
                begin
                dbms_output.put_line('Top ' || tid_to_display_count ||
                                    ' best-fit criteria');
                dbms_output.new_line;
                -- transaction data loop
                for i in (select td.transaction_data_id, ft.accounting_datetime
                            from billien_fa.transaction_data td
                            left join billien_fa.financial_transaction ft
                                on ft.transaction_data_id = td.transaction_data_id
                            where td.transaction_data_id in
                                (select column_value from table(v_transaction_data_id))) loop
                    dbms_output.put_line(lpad('*', 100, '*'));
                    dbms_output.put_line(rpad(' ', 18, ' ') ||
                                        'check transaction_data_id ' ||
                                        i.transaction_data_id ||
                                        ', accounting datetime: ' ||
                                        to_char(billien_co.to_local_datetime(i.accounting_datetime)
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
                                from billien_fa.transaction_item_def td
                                join billien_fa.transaction_def d
                            using (transaction_def_id)
                            where exists
                            (select 1.0
                                        from billien_fa.selection_criteria sc
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
                                from billien_fa.selection_criteria sc
                                join billien_fa.data_column
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
                                            ' from billien_fa.transaction_data where transaction_data_id = ' ||
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
                                            ' from billien_fa.transaction_data where transaction_data_id = ' ||
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
                                        join billien_fa.transaction_item_def tid
                                        using (transaction_item_def_id, transaction_item_def_short)
                                        join billien_fa.transaction_def td
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
                                        to_char(billien_co.to_local_datetime(i.validity_start)
                                                ,'dd.mm.yyyy') || ' - ' ||
                                        nvl(to_char(billien_co.to_local_datetime(i.validity_end)
                                                    ,'dd.mm.yyyy')
                                            ,'...') || case when
                                        i.deleted_on is not null then
                                        ' deleted on: ' ||
                                        to_char(billien_co.to_local_datetime(i.deleted_on)
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

    
    return render(request,'ems/transakce_ems.html', context)

import datetime
def my_job():
    print(f"{datetime.datetime.now()} - I love python\n")
    
import os
import json
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import DataForm

# Získajte logger
import logging
logger = logging.getLogger('my_app')  # Použite názov loggera, ktorý ste definovali

# Define the filename of the JSON file to load


import json

def marketing_stats_view(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'work', 'static', 'json', 'jobs.json')

    with open(file_name, 'r') as file:
        json_inputs = json.load(file)

    # emails = [json_input['fields']['emails'] for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky']
    # print(emails)
    emails = [email for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky' for email in json_input['fields']['emails']]
    head = [json_input['fields']['head'] for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky'][0] if json_inputs else None
    body = [json_input['fields']['body'] for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky'][0] if json_inputs else None
    
    # print(body)
    rune = [json_input['fields']['run'] for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky'][0] if json_inputs else {}

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
        json_inputs = [json_input for json_input in json_inputs if json_input['model'] != 'marketingove_statistiky']
        json_inputs.append({
            'model': 'marketingove_statistiky',
            'fields': {
                'emails': emails,
                'run': rune,
                'head': head,
                'body':body
            }
        })
        with open(file_name, 'w') as file:
            json.dump(json_inputs, file, indent=4)

        from scheduler import reload_job_if_markstat
        # Reload job pre EETS_Lego
        reload_job_if_markstat('marketingove_statistiky', 'work/static/json/jobs.json')

        return render(request, 'ems/marketing_stats.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body})
    return render(request, 'ems/marketing_stats.html', {'emails': emails, 'rune': rune, 'head':head, 'body':body})

#:::::::::::::: Reports PDF ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def generate_pdf(request):
    from reportlab.lib.pagesizes import letter

    from reportlab.lib import colors

    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    from reportlab.lib.units import mm
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(BASE_DIR, 'work', 'static', 'img', 'myto.png')

    # Create a new PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="mypdf.pdf"'

    # Create a canvas object
    c = canvas.Canvas(response, pagesize=letter)

    # Calculate the center position of the page
    page_width, page_height = letter
    image_width, image_height = 25*mm, 17*mm
    x = 50
    y = 720
    # Draw the PNG image at the center of the page
    c.drawImage(image_path, x, y, width=image_width, height=image_height)

    # Draw the centered text
    font_size = 14
    text = "Prerozdelenie mýta medzi vlastníkov ciest"
    x_text = page_width / 2
    y_text = page_height - 30 * mm
    c.setFont('Helvetica-Bold', font_size)
    c.drawCentredString(x_text, y_text, text)

    # Draw the date in the upper right corner
    from datetime import datetime
    date_text = f"Dátum vygenerovania: {datetime.now().strftime('%d. %m. %Y    %H:%M:%S')}"
    x_date = page_width - 10*mm
    y_date = page_height - 20*mm
    c.setFont('Helvetica', 8)
    c.drawRightString(x_date, y_date, date_text)

    font_size = 10
    text = "Mýtne transakcie spracované za obdobie:"
    c.setFont('Helvetica-Bold', font_size)
    c.drawCentredString(150, page_height - 50 * mm, text)
    
    # GENERATE 
    EMS_DWH=EMS_DWHDB.objects.get(user=1)
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()

    query ="""SELECT * FROM   "REP_CRM"."V_LEGO_REP_01" "V_LEGO_REP_01"
                WHERE "V_LEGO_REP_01"."TRANSACTION_ARRIVAL_MONTH" >= add_months(trunc(sysdate, 'MM'), -1)
                AND "V_LEGO_REP_01"."TRANSACTION_ARRIVAL_MONTH" < trunc(sysdate, 'MM')
                ORDER BY OWNER_NAME, PASSAGEDATE_MONTHLY"""
    with con_EMSDWH_STDBY.cursor() as cursor:
            cursor.execute(query)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            data = dictfetchall(cursor)
    print(data)

    filtered_data = [row for row in data if row['OWNER_NAME'] == 'Granvia']
    print(filtered_data)
  

    # print(granvia_data['OWNER_NAME'])
    # Save and return the PDF document
    c.save()
    # print(data)


    return response
import io
from reportlab.lib.units import inch
def generate_report(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    EMS_DWH=EMS_DWHDB.objects.get(user=1)
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()

    query ="""SELECT * FROM   "REP_CRM"."V_LEGO_REP_01" "V_LEGO_REP_01"
                WHERE "V_LEGO_REP_01"."TRANSACTION_ARRIVAL_MONTH" >= add_months(trunc(sysdate, 'MM'), -1)
                AND "V_LEGO_REP_01"."TRANSACTION_ARRIVAL_MONTH" < trunc(sysdate, 'MM')
                ORDER BY OWNER_NAME, PASSAGEDATE_MONTHLY"""
    with con_EMSDWH_STDBY.cursor() as cursor:
            cursor.execute(query)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            data = dictfetchall(cursor)

    filtered_data = [row for row in data if row['OWNER_NAME'] == 'Granvia']


    # Create a list of strings, where each string represents a row in the filtered data

    filtered_data_strings = [f"{row['OWNER_NAME']} {row['PASSAGEDATE_MONTHLY']} {row['PASSAGEDATE_MONTHLY']}" for row in filtered_data]


    for line in filtered_data_strings:

        textob.textLine(line)


    c.drawText(textob)

    c.showPage()

    c.save()

    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='test.pdf')

from django.template.loader import get_template
from xhtml2pdf import pisa
def render_pdf_view(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(BASE_DIR, 'work', 'templates', 'ems', 'lego_pdf.html')
    print(template_path)

    EMS_DWH=EMS_DWHDB.objects.get(user=1)
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()
    cursor = con_EMSDWH_STDBY.cursor()

    query ="""SELECT * FROM   "REP_CRM"."V_LEGO_REP_01" "V_LEGO_REP_01"
                WHERE "V_LEGO_REP_01"."TRANSACTION_ARRIVAL_MONTH" >= add_months(trunc(sysdate, 'MM'), -1)
                AND "V_LEGO_REP_01"."TRANSACTION_ARRIVAL_MONTH" < trunc(sysdate, 'MM')
                ORDER BY OWNER_NAME, PASSAGEDATE_MONTHLY"""
    with con_EMSDWH_STDBY.cursor() as cursor:
            cursor.execute(query)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            data = dictfetchall(cursor)

    # filtered_data = [row for row in data if row['OWNER_NAME'] == 'Granvia']
    # context = {'myvar': 'sadfsdfasdfadsfdsfds'}
    filtered_data = [row for row in data if row['OWNER_NAME'] == 'Granvia']
    context = {'myvar': filtered_data}
    print(context)


    response =HttpResponse(content_type='aplication/pdf')

    # if download
    # response['Content-Disposition'] = attachment; 'filename="report.pdf"'

    response['Content-Disposition'] = 'filename="report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status=pisa.CreatePDF(
        html, dest=response
    )
    if pisa_status.err:
        return HttpResponse('sadfsdafdsafdfsa <pre>'+ html + '</pre>')
    return response


@login_required
def pos_user(request):
    billdb=BILLDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(billdb.BILLDB_username+"/"+billdb.BILLDB_password+"@"+billdb.BILLDB_hostname+":"+billdb.BILLDB_port+"/"+billdb.BILLDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()

    sql_ = """SELECT POS_ID, POS_NUMBER, POS_NAME, pos.POS_TYPE_CODE, POS_TYPE_NAME, pos.RETAIL_PARTNER_ID, rp.RETAIL_PARTNER_NAME
                                    from billien_co.pos pos
                                    left join billien_co.POS_TYPE_L typ on pos.POS_TYPE_CODE=typ.POS_TYPE_CODE
                                    left join billien_co.retail_partner rp on pos.retail_partner_id = rp.retail_partner_id
                                    where pos.priority != '-1'
                                    and typ.LANGUAGE_CODE='SK'
                                    order by POS_NUMBER
                                """
    with con_BILLDB_STDBY.cursor() as cursor:
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
                                billien_ac.user_detail    ad
                                LEFT JOIN billien_ac.user_in_role   usr ON ad.user_id = usr.user_id
                                LEFT JOIN billien_ac.role           rl ON usr.role_id = rl.role_id
                                LEFT JOIN billien_ac.user_in_pos    pos ON ad.user_id = pos.user_id
                                left join BILLIEN_AC.user_status_l stat on ad.USER_STATUS_CODE=stat.USER_STATUS_CODE
                            WHERE
                                POS_ID=:id
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
        with con_BILLDB_STDBY.cursor() as cursor:
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
                                billien_ac.user_detail    ad
                                LEFT JOIN billien_ac.user_in_role   usr ON ad.user_id = usr.user_id
                                LEFT JOIN billien_ac.role           rl ON usr.role_id = rl.role_id
                                LEFT JOIN billien_ac.user_in_pos    pos ON ad.user_id = pos.user_id
                                left join BILLIEN_AC.user_status_l stat on ad.USER_STATUS_CODE=stat.USER_STATUS_CODE
                            WHERE
                                user_name LIKE :usr
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
        with con_BILLDB_STDBY.cursor() as cursor:
            c = '%' + y + '%'
            cursor.execute(sql_ROLE_NAME, usr=c)
            #rows = cursor.fetchall()
            #rows = namedtuplefetchall(cursor)
            users = dictfetchall(cursor)

    context = { 'Poses':Poses, 'users':users }
    return render(request,'ems/poses_users.html', context)

@login_required
def dwh_control(request):
    import cx_Oracle
    # cis_db=CISDB.objects.get(user=request.user)
    EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
    con_EMSDWH_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cur_EMSDWH = con_EMSDWH_STDBY.cursor()

    sql_logs = """select STEP, TO_CHAR(from_tz(CAST(STEP_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as STEP_DATE_TIME_CET
                  from BILLIEN_STA.v_dwh_load_status"""

    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_logs)
        dwh_logs = dictfetchall(cursor)
        
    sql_detail = """select ID_DWH_LOAD_DETAIL, /*SOURCE_SYSTEM_NAME,*/ LOAD_NUMBER, PARTITION_ID, LOAD_STAGE, STATUS,
                    TO_CHAR(from_tz(CAST(DATE_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as DATE_FROM_CET,
                    TO_CHAR(from_tz(CAST(DATE_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as DATE_TO_CET,
                    TO_CHAR(from_tz(CAST(LOAD_START AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as LOAD_START_CET,
                    TO_CHAR(from_tz(CAST(LOAD_END AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as LOAD_END_CET,
                    round((LOAD_END - LOAD_START) * 24 * 60, 1) AS diff_minutes,
                    TABLE_NAME, COMMAND
                    from BILLIEN_STA.dwh_load_detail
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
                    FROM BILLIEN_STA.dwh_load_error order by ID_DWH_LOAD_ERROR desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_error)
        dwh_error = dictfetchall(cursor)

    sql_merge_tables = """
                        select 
                        LOAD_NUMBER, /*SOURCE_SYSTEM_NAME,*/	PARTITION_ID,	IS_MERGED_FLAG,	
                        TO_CHAR(from_tz(CAST(MERGE_FINISHED_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET', 'DD.MM.YYYY HH24:MI:SS') as 
                        MERGE_FINISHED_DATETIME,	IS_PREPARED_TO_MERGE,	
                        IS_EXPORT_RUNNING_FLAG,	LAST_RUN_ERROR_MESSAGE
                        from BILLIEN_STA.dwh_merge_table
                        order by LOAD_NUMBER desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_merge_tables)
        dwh_merge = dictfetchall(cursor)

    sql_tables = """SELECT ext.*, CAST(FROM_TZ(CAST(LAST_RUN AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LAST_RUN_CET  
                    FROM BILLIEN_STA.DWH_EXPORT_TABLE ext order by LAST_RUN desc
                  """
    with con_EMSDWH_STDBY.cursor() as cursor:
        cursor.execute(sql_tables)
        dwh_tables = dictfetchall(cursor)

    context={'dwh_logs': dwh_logs, 'dwh_detail':dwh_detail, 'dwh_error':dwh_error, 'dwh_tables':dwh_tables, 'dwh_merge':dwh_merge }
    return render(request,'ems/dwh_control.html', context)
########## LEGO REPORT view and manual PDF generation ##########
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

@login_required
def lego_rep_CRM(request):
    export = ''
    column_names_list = ''
    q = None

    con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@db-host.internal.example.com:1521/dwh")
    
    sql_logs = """select * from V_LEGO_REP_01
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
            MM = request.POST.get('MM')  # Get the value of MM from the form
            pdfmetrics.registerFont(TTFont('DejaVuSans', './eets/static/fonts/DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('Arial Unicode MS', './eets/static/fonts/arial-unicode-ms.ttf'))
            
            from datetime import datetime
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("Dátum vygenerovania: %d. %m. %Y %H:%M:%S")
            previous_month = current_datetime - relativedelta(months=1)
            formatted_previous = previous_month.strftime("%m/%Y")
            formatted_previous_month = previous_month.strftime("%Y")

            con_DWH_REP_CRM= cx_Oracle.connect("DB_USER/DB_PASSWORD@db-host.internal.example.com:1521/dwh")

            pdf_sql = """
                    select * from V_LEGO_REP_01
                    where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY')
                    order by PASSAGEDATE_MONTHLY asc
                    """
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
                    select PASSAGEDATE_MONTHLY, SUM(SPOLU) as SPOLU from V_LEGO_REP_01
                    where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY')
                    and OWNER_NAME in ('Granvia','Zero Bypass Limited')
                    group by PASSAGEDATE_MONTHLY
                    order by PASSAGEDATE_MONTHLY asc
                    """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(ppp_sql, MM=MM)
                ppp_data = dictfetchall(cursor)
            sum_spolu_ppp = round(sum(row['SPOLU'] for row in ppp_data), 2)

            spolu_sql = """
                    select PASSAGEDATE_MONTHLY, SUM(SPOLU) as SPOLU from V_LEGO_REP_01
                    where TRANSACTION_ARRIVAL_MONTH = TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY')
                    group by PASSAGEDATE_MONTHLY
                    order by PASSAGEDATE_MONTHLY asc
                    """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(spolu_sql, MM=MM)
                spolu_data = dictfetchall(cursor)
            sum_spolu = round(sum(row['SPOLU'] for row in spolu_data), 2)

            """Generates a PDF file with the provided content."""
            # odmazanie obsahu
            directory = './Reports/Lego/'  # specify the directory path

            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")

            output_filename = './Reports/Lego/EETS_LEGO_REP_'+MM+'2025.pdf'
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
            c.drawString(35, 690, "Vlastník:")

            c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech
            c.drawString(80, 690, "Granvia")
            #--------------------
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, 585, "Vlastník:")

            c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech
            c.drawString(80, 585, "Zero Bypass Limited")
            #-------------------------
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, 485, "Celkom (PPP úseky) - Granvia + R7/D4")
            #-------------------------------
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, 410, "Vlastník:")

            c.setFont("Arial Unicode MS", 8)  # Use a font that supports Czech
            c.drawString(80, 410, "Štát")
            #-------------------------------
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, 295, "Celkom - PPP + Štát")

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
            # table_gr.setStyle(table_style)
            # table_ppp.setStyle(table_style)
            # table_stat.setStyle(table_style)
            # table_spolu.setStyle(table_style)

            # Get the page dimensions
            table.wrapOn(c, 120, 800)
            # table_gr.wrapOn(c, 120, 800)
            # table_ppp.wrapOn(c, 120, 800)
            # table_stat.wrapOn(c, 120, 800)
            # table_spolu.wrapOn(c, 120, 800)

            # Calculate the table width
            table_width = sum(col_widths)
            # table_gr.drawOn(c, (A4[0] - table_width) / 4.4, 635)
            table.drawOn(c, (A4[0] - table_width) / 4.4, 530)
            # table_ppp.drawOn(c, (A4[0] - table_width) / 4.4, 430)
            # table_stat.drawOn(c, (A4[0] - table_width) / 4.4, 335)
            # table_spolu.drawOn(c, (A4[0] - table_width) / 4.4, 215)

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

            # Open the PDF file
            with open(output_filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="EETS_LEGO_REP_'+MM+'2025.pdf"'
            return response           

        if 'delete_procedure' in request.POST:
            MM = request.POST.get('MM')  # Get the value of MM from the form
            YYYY = request.POST.get('YYYY')  # Get the value of YYYY from the form
            procedure_sql = """
                DECLARE
                    o_result_code NUMBER;
                    o_error_message VARCHAR2(4000);
                BEGIN
                    kdx_pkg_lego_ppp_2020.lego_drop_temporary_agg_tables(
                    o_result_code => o_result_code,
                    o_error_message => o_error_message,
                    i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
                    );
                    kdx_pkg_lego_ppp_2020.lego_del_kpbpm_by_trans_ar_mon(
                    o_result_code => o_result_code,
                    o_error_message => o_error_message,
                    i_date => TO_DATE('01-' || :MM || '-' || :YYYY, 'DD-MM-YYYY')
                    );
                    kdx_pkg_lego_ppp_2020.lego_del_kspoi_by_trans_ar_mon(
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
            return HttpResponseRedirect(reverse('work:lego_rep_CRM'))

        if 'delete_REMOVED_BILL_ID' in request.POST:
            TRUNCATE_sql = """TRUNCATE TABLE KDX_REMOVED_BILL_IDS
                """
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(TRUNCATE_sql)
                con_DWH_REP_CRM.commit()  # Commit the changes
                    # print("Procedura spuštěna")
            messages.info(request, f"Vymazanie dat z tabulky KDX_REMOVED_BILL_IDS dokončené")
            return HttpResponseRedirect(reverse('work:lego_rep_CRM'))
        
        if 'insert_REMOVED_BILL_ID' in request.POST:
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
            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(insert_sql)
                con_DWH_REP_CRM.commit()  # Commit the changes
                    # print("Procedura spuštěna")
            messages.info(request, f"Naplnenie tabulky KDX_REMOVED_BILL_IDS dokončené")
            return HttpResponseRedirect(reverse('work:lego_rep_CRM'))

        if 'run_procedure' in request.POST:
            MM = request.POST.get('MM')  # Get the value of MM from the form
            mydate = request.POST.get('mydate')  # Get the value of mydate from the form
            procedure_sql = """
                DECLARE
                    o_result_code NUMBER;
                    o_error_message VARCHAR2(4000);
                BEGIN
                    kdx_pkg_lego_ppp_2020.lego_prepare_kpbpm_agg (
                      o_result_code => o_result_code,
                      o_error_message => o_error_message,
                      i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY'),
                      i_date_from_0203_mm_yyyy => TO_DATE('03-' || :MM || '-2025', 'DD-MM-YYYY'),
                      i_parallel_degree => 6,
                      i_discount_calculated_on_from => TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY'),
                      i_discount_calculated_on_to => TO_DATE(:mydate, 'DD-MM-YYYY')
                    );
                    kdx_pkg_lego_ppp_2020.lego_insert_kpbpm (
                      o_result_code => o_result_code,
                      o_error_message => o_error_message,
                      i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY')
                    );
                    kdx_pkg_lego_ppp_2020.lego_prepare_kspoi_agg (
                      o_result_code => o_result_code,
                      o_error_message => o_error_message,
                      i_date_from_01_mm_yyyy => TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY'),
                      i_date_from_0203_mm_yyyy => TO_DATE('03-' || :MM || '-2025', 'DD-MM-YYYY'),
                      i_discount_calculated_on_from => TO_DATE('01-' || :MM || '-2025', 'DD-MM-YYYY'),
                      i_discount_calculated_on_to => TO_DATE(:mydate, 'DD-MM-YYYY')
                    );
                END;
            """

            with con_DWH_REP_CRM.cursor() as cursor:
                cursor.execute(procedure_sql, MM=MM, mydate=mydate)
                con_DWH_REP_CRM.commit()  # Commit the changes
            # print("Procedura dokoncena")
            messages.info(request, f"Procedura dokoncena i_date_from_01_mm_yyyy => 01-{MM}-2025 a i_discount_calculated_on_to => {mydate}")
            return HttpResponseRedirect(reverse('work:lego_rep_CRM'))

    con_DWH_REP_CRM.close()  # Close the connection

    context = {'dwh_lego_view':dwh_lego_view, 'dwh_lego_removed_bill':dwh_lego_removed_bill }
    return render(request, 'lego_view.html', context)

########## PAY WELL ##########
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404

UPLOAD_DIR = os.path.join(settings.PAYWELL_ROOT, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def paywell(request):
    message = ''
    pswd = '936BhU14'  # Heslo na odzipovanie
    transactions_summary = {
        'T_FP_CARD_TRANSACTIONS': [],
        'T_FP_FCI_CARD_TRANSACTIONS': []
    }

    # === PRIPOJENIE K ORACLE A NAČÍTANIE PREHĽADU ===
    try:
        EMS_DWH = EMS_DWHDB.objects.get(user=1)
        con = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username + "/" + EMS_DWH.EMS_DWHDB_password + "@" + EMS_DWH.EMS_DWHDB_hostname + ":" + EMS_DWH.EMS_DWHDB_port +"/" + EMS_DWH.EMS_DWHDB_servicename)
        cur = con.cursor()

        query_1 = """
            SELECT to_char(date_time, 'dd.mm.yyyy') AS DateOfTransaction, count(ID) as pocet
            FROM REP_CRM.T_FP_CARD_TRANSACTIONS 
            WHERE date_time >= trunc(SYSDATE -5) AND date_time < trunc(SYSDATE)
            GROUP BY to_char(date_time, 'dd.mm.yyyy') 
            ORDER BY 1
        """

        query_2 = """
            SELECT to_char(date_time, 'dd.mm.yyyy') AS DateOfTransaction, count(ID) as pocet
            FROM REP_CRM.T_FP_FCI_CARD_TRANSACTIONS 
            WHERE date_time >= trunc(SYSDATE -5) AND date_time < trunc(SYSDATE)
            GROUP BY to_char(date_time, 'dd.mm.yyyy') 
            ORDER BY 1
        """

        cur.execute(query_1)
        transactions_summary['T_FP_CARD_TRANSACTIONS'] = cur.fetchall()

        cur.execute(query_2)
        transactions_summary['T_FP_FCI_CARD_TRANSACTIONS'] = cur.fetchall()

        cur.close()
        con.close()
    except Exception as e:
        message += f'⚠️ Chyba pri načítaní prehľadu transakcií: {e}<br>'
    
    # Spojenie a súčet podľa dátumu
    from collections import defaultdict

    sum_per_date = defaultdict(int)

    for date, count in transactions_summary['T_FP_CARD_TRANSACTIONS']:
        sum_per_date[date] += count

    for date, count in transactions_summary['T_FP_FCI_CARD_TRANSACTIONS']:
        sum_per_date[date] += count

    # zoradenie podla datumu
    summary_sum = sorted(sum_per_date.items())

    transactions_summary['SUM'] = summary_sum


    # === 1. Nahrávanie ZIP súboru cez formulár ===
    if request.method == 'POST' and request.FILES.get('zipfile'):
        logger.info("------------ START upload suboru " )  # Zaznamenajte správu do info.log
        zipfile_uploaded = request.FILES['zipfile']
        if zipfile_uploaded.name.endswith('.zip'):
            fs = FileSystemStorage(location=UPLOAD_DIR)
            filename = fs.save(zipfile_uploaded.name, zipfile_uploaded)
            message = f'✅ Súbor "{filename}" bol úspešne nahraný.'
        else:
            message = '❌ Prosím, nahrajte platný ZIP súbor.'

    # === 2. Vymazanie súboru cez formulár ===
    if request.method == 'POST' and request.POST.get('delete_file'):
        logger.info("------------ START vymazanie suboru " )
        file_to_delete = request.POST['delete_file']
        file_path = os.path.join(UPLOAD_DIR, file_to_delete)
        if os.path.isfile(file_path):
            os.remove(file_path)
            message = f'🗑️ Súbor "{file_to_delete}" bol vymazaný.'
        else:
            message = f'❌ Súbor "{file_to_delete}" neexistuje.'
    
    # === 3. Vymazanie VŠETKÝCH súborov ===
    if request.method == 'POST' and request.POST.get('delete_all'):
        logger.info("------------ START vymazanie VSETKYCH suborov")
        deleted = 0
        for file in os.listdir(UPLOAD_DIR):
            try:
                os.remove(os.path.join(UPLOAD_DIR, file))
                deleted += 1
            except Exception as e:
                logger.warning(f"Nepodarilo sa zmazať {file}: {e}")
        message = f'🧹 Vymazaných {deleted} súborov.'

    # === 3. Odzipovanie všetkých ZIP súborov a spracovanie XML do jedného SQL ===
    if request.method == 'POST' and 'unzip_files' in request.POST:
        logger.info("------------ START odzipovanie " )
        insert_lines = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sql_file_name = f"insert_example_all_{timestamp}.sql"
        sql_file_path = os.path.join(UPLOAD_DIR, sql_file_name)

        # A. Odzipuj všetky ZIP súbory v priečinku
        for filename in os.listdir(UPLOAD_DIR):
            if filename.lower().endswith('.zip'):
                zip_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    with zipfile.ZipFile(zip_path) as zip_file:
                        zip_file.setpassword(pswd.encode('utf-8'))
                        zip_file.extractall(UPLOAD_DIR)
                        message += f'✅ ZIP "{filename}" bol úspešne odzipovaný.<br>'
                except RuntimeError as e:
                    message += f'❌ Chyba pri odzipovaní "{filename}": {e}<br>'
                except Exception as e:
                    message += f'❌ Neočakávaná chyba so súborom "{filename}": {e}<br>'

        # B. Prejdi všetky .xml a vyber INSERTy
        for xml_file in os.listdir(UPLOAD_DIR):
            logger.info("------------ START priprava insertov " )
            if xml_file.lower().endswith('.xml'):
                xml_path = os.path.join(UPLOAD_DIR, xml_file)
                try:
                    tree = ET.parse(xml_path)
                    text = ET.tostring(tree.getroot(), encoding='utf-8', method='text').decode('utf-8')
                    insert_lines += [
                        line.strip() for line in text.splitlines() if line.strip().upper().startswith("INSERT INTO")
                    ]
                except Exception as e:
                    message += f'⚠️ Chyba pri XML "{xml_file}": {e}<br>'

        # C. Vytvor SQL súbor s INSERTmi
        if insert_lines:
            logger.info("------------ START vytvorenie sql " )
            try:
                with open(sql_file_path, 'w', encoding='utf-8') as sql_out:
                    sql_out.write('\n'.join(insert_lines))
                    sql_out.write('\nCOMMIT;\n')
                message += f'📄 INSERTy boli uložené do "{sql_file_name}".<br>'
            except Exception as e:
                message += f'❌ Chyba pri zápise SQL: {e}<br>'
        else:
            message += '⚠️ Neboli nájdené INSERT príkazy v žiadnom XML súbore.<br>'

    # === 6. Import SQL do Oracle DB ===
    if request.method == 'POST' and request.POST.get('import_sql_to_db'):
        print("------------ START import sql do DB")
        logger.info("------------ START import sql do DB")
        # try:
        #     sql_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.sql')]
        #     if sql_files:
        #         sql_files.sort()
        #         file_path = os.path.join(UPLOAD_DIR, sql_files[-1])

        #         with open(file_path, 'r', encoding='utf-8') as f:
        #             full_sql = f.read()

        #         statements = [s.strip() for s in full_sql.split(';') if s.strip()]
        #         EMS_DWH = EMS_DWHDB.objects.get(user=1)
        #         con = cx_Oracle.connect(
        #             f"{EMS_DWH.EMS_DWHDB_username}/{EMS_DWH.EMS_DWHDB_password}@{EMS_DWH.EMS_DWHDB_hostname}:{EMS_DWH.EMS_DWHDB_port}/{EMS_DWH.EMS_DWHDB_servicename}"
        #         )
        #         cur = con.cursor()

        #         message += f'✅  Pripojenie do DWH.<br>'
        #         message += f'❓ Spusteny import SQL súboru "{os.path.basename(file_path)}" do DWH.<br>'
        #         message += f'❓ Počet príkazov: {len(statements)}<br>'
        #         message += f'❓ Spúšťam príkazy:<br>'
                
        #         for stmt in statements:
        #             try:
        #                 cur.execute(stmt)
        #             except Exception as e:
        #                 message += f'❌ Chyba: {e}<br>'
        #         con.commit()
        #         cur.close()
        #         con.close()
        #         message += f'✅ SQL súbor \"{os.path.basename(file_path)}\" bol importovaný do DB.<br>'
        #     else:
        #         message += "❌ Nebol nájdený žiadny .sql súbor na import.<br>"
        # except Exception as e:
        #     message += f"❌ Chyba importu do DB: {e}<br>"

    # === Zmazanie z DB ===
    if request.method == 'POST' and request.POST.get('delete_transactions_by_date'):
        print("------------ START zmazanie transakcii")
        logger.info("------------ START zmazanie transakcii")
        try:
            # Formát: 15.05.2025
            delete_date = request.POST.get('delete_date')
            datetime.strptime(delete_date, '%d.%m.%Y')  # validácia

            EMS_DWH = EMS_DWHDB.objects.get(user=1)
            con = cx_Oracle.connect(
                f"{EMS_DWH.EMS_DWHDB_username}/{EMS_DWH.EMS_DWHDB_password}@{EMS_DWH.EMS_DWHDB_hostname}:{EMS_DWH.EMS_DWHDB_port}/{EMS_DWH.EMS_DWHDB_servicename}"
            )
            cur = con.cursor()

            delete_sql_1 = f"""
                DELETE FROM REP_CRM.T_FP_CARD_TRANSACTIONS
                WHERE TRUNC(transaction_date) = TO_DATE('{delete_date}', 'DD.MM.YYYY')
            """
            delete_sql_2 = f"""
                DELETE FROM REP_CRM.T_FP_FCI_CARD_TRANSACTIONS
                WHERE TRUNC(transaction_date) = TO_DATE('{delete_date}', 'DD.MM.YYYY')
            """

            cur.execute(delete_sql_1)
            cur.execute(delete_sql_2)
            con.commit()
            cur.close()
            con.close()

            message += f'🗑️ Transakcie k dátumu {delete_date} boli vymazané.<br>'
        except ValueError:
            message += f'❌ Nesprávny formát dátumu. Použi DD.MM.YYYY<br>'
        except Exception as e:
            message += f'❌ Chyba pri mazaní transakcií: {e}<br>'


    # === 4. Načítanie súborov ===
    try:
        files = os.listdir(UPLOAD_DIR)
    except FileNotFoundError:
        files = []

    return render(request, 'ems/paywell.html', {
        'files': os.listdir(UPLOAD_DIR),
        'message': message,
        'transactions_summary': transactions_summary,
    })


def download_sql(request, filename):
    logger.info("------------ START stiahnutie suboru " )
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    raise Http404("Súbor neexistuje.")
