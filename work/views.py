from django.shortcuts import render, redirect
from django.http import HttpResponse   # added
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import os
import shutil
# from colorama import Fore
import mimetypes
from project.settings import DATABASES
from .models import *
import os
# from project.settings import con_CISDB_STDBY, cx_Oracle
from project.settings import cx_Oracle
import glob
import webbrowser
import datetime
from django.contrib.auth.decorators import login_required
from .forms import CISDBUpdateForm, DWHDBUpdateForm, CISDB_TEST_UpdateForm, BILLDBUpdateForm, EMSDWHDBUpdateForm
from django.contrib.auth.hashers import make_password

# cislo riadku
from django.db.models.expressions import RawSQL
from . import views_ems

from django.core.signing  import Signer

from django.conf import settings
from encrypt_decrypt_fields import Crypto

# EDZ project
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from edz import forms
from edz.models import EDZDB
from eets import forms
from eets.models import EETSDB

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

now = datetime.datetime.now()
time = now.strftime("%H:%M:%S")


        
@login_required
def home(request):
    # remove these print statements later
    # print('\n\nRequest object:', request)
    # print('Request object type:', type(request), '\n\n')

    return render(request, 'base.html')
    
def signup(request):

    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        # pin = request.POST['PIN']


        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('work:signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already exist!")
            return redirect('work:signup')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didt'n match!")
            return redirect('work:signup')
        
        # if pin != '2023':
        #     messages.error(request, "The PIN code does not match")
        #     return redirect('work:signup')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_staff = True

        myuser.save()
        cis = CISDB(user=myuser)
        cis.save()

        cis_test = CISDB_TEST(user=myuser)
        cis_test.save()

        dwh = DWHDB(user=myuser)
        dwh.save()

        ems_dwh = EMS_DWHDB(user=myuser)
        ems_dwh.save()
        
        
        edz = EDZDB(user=myuser)
        edz.save()
        messages.success(request, "Your Account has been successfully created. ")

        eets = EETSDB(user=myuser)
        eets.save()
        messages.success(request, "Your Account has been successfully created. ")


        bill = BILLDB(user=myuser)
        bill.save()
        messages.success(request, "Your Account has been successfully created. ")

        # Welcome email 
        if myuser is not None:
            login(request, myuser)
            # myuser.first_name = fname
            return render(request, 'preface.html')

        return redirect('/preface')

    return render(request, "authentication/signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            # myuser.first_name = fname
            fname = user.first_name
            return render(request, 'preface.html', {'fname':fname})
        
        else:
            messages.error(request, "Bad Credentials! ")
            return render(request, 'authentication/signin.html')


    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return render(request, 'authentication/signin.html')

@login_required
def preface(request):
    # remove these print statements later
    # print('\n\nRequest object:', request)
    # print('Request object type:', type(request), '\n\n')

    return render(request, 'preface.html')

@login_required
def hpsm(request):
    import pyodbc
    connection_string = (
            r'DRIVER={SQL Server};'
            r'SERVER=HPSMDB;'
            r'DATABASE=HPSMPROD;'
            r'UID=XOSA_APP;'
            r'PWD=UdiCVkraFwgv3i4IqXq7;'
        )

    connection = pyodbc.connect(connection_string)

        # Create a cursor object
    cursor = connection.cursor()

    sql = """SELECT *, DATEADD(hour, 2, OPEN_TIME) as My_time
                FROM dbo.PROBSUMMARYM1 p 
                where ASSIGNEE_NAME is NULL
                and ASSIGNMENT='Prevadzka App' or ASSIGNMENT='Prevadzka TCS/MD' and ASSIGNEE_NAME is NULL
                /*and STATUS='OPEN'*/
                ORDER by OPEN_TIME desc
            """

    # Execute the SQL query to list all the tables
    cursor.execute(sql)

    # Fetch and print the table names
    APP_INC = cursor.fetchall()

    if 'q' in request.GET:
        q=request.GET['q']

        sql_search ="""SELECT *,  DATEADD(hour, 2, OPEN_TIME) as My_time
                        FROM dbo.PROBSUMMARYM1 p 
                        where 
                        UPDATE_ACTION LIKE ?
                        or  BRIEF_DESCRIPTION LIKE ?
                        or ACTION LIKE ?
                        or RESOLUTION LIKE ?
                        ORDER by OPEN_TIME desc
                        """
        with connection.cursor() as cursor:
            text=str(q)
            print(text)
            cursor.execute(sql_search, '%' + str(q) + '%', '%' + str(q) + '%', '%' + str(q) + '%', '%' + str(q) + '%')
            APP_INC = dictfetchall(cursor)
            # for row in APP_INC:
            #     print(row.NUMBER)

    context = {'APP_INC':APP_INC}

    return render(request, 'authentication/hpsm_inc.html', context )

@login_required
def hpsm_c(request):
    import pyodbc
    connection_string = (
            r'DRIVER={SQL Server};'
            r'SERVER=HPSMDB;'
            r'DATABASE=HPSMPROD;'
            r'UID=XOSA_APP;'
            r'PWD=UdiCVkraFwgv3i4IqXq7;'
        )

    connection = pyodbc.connect(connection_string)

        # Create a cursor object
    cursor = connection.cursor()

    sql = """SELECT *, DATEADD(hour, 2, ORIG_DATE_ENTERED) as My_time
            FROM dbo.CM3RM1 ch
            where ASSIGNED_TO is NULL 
            and ASSIGN_DEPT='Prevadzka App'
            and STATUS !='CLOSED'
            order by ORIG_DATE_ENTERED desc
            """

    # Execute the SQL query to list all the tables
    cursor.execute(sql)

    # Fetch and print the table names
    APP_INC = cursor.fetchall()

    if 'q' in request.GET:
        q=request.GET['q']

        sql_search ="""SELECT *, DATEADD(hour, 2, ORIG_DATE_ENTERED) as My_time
                        FROM dbo.CM3RM1 ch
                        where
                        BRIEF_DESCRIPTION LIKE ?  
                        or DESCRIPTION LIKE ?  
                        or UPDATE_ACTION LIKE ?  
                        or CLOSING_COMMENTS LIKE ? 
                        order by ORIG_DATE_ENTERED desc
                        """
        with connection.cursor() as cursor:
            text=str(q)
            print(text)
            cursor.execute(sql_search, '%' + str(q) + '%', '%' + str(q) + '%', '%' + str(q) + '%', '%' + str(q) + '%')
            APP_INC = dictfetchall(cursor)
            # for row in APP_INC:
            #     print(row.NUMBER)

    context = {'APP_INC':APP_INC}

    return render(request, 'authentication/hpsm_c.html', context )

################ Logging #####################
import os
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

# Definujte cestu k priečinku 'logs'
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

# def view_log(request):
#     # Získajte aktuálny dátum
#     current_date = datetime.now().strftime("%d%m%Y")
    
#     head='Warning log z aktuálneho dňa'

#     # Cesta k súboru s logmi z aktuálneho dňa
#     log_file_path = os.path.join(LOG_DIR, f'warnings_{current_date}.log')

#     # Skontrolujte, či súbor existuje
#     if os.path.exists(log_file_path):
#         with open(log_file_path, 'r', encoding='utf-8') as file:
#             log_content = file.read()
#     else:
#         log_content = "Log súbor neexistuje alebo nebol ešte vytvorený pre dnešný deň."

#     # Odoslanie obsahu logu do šablóny
#     return render(request, 'view_log.html', {'log_content': log_content, 'head':head})

def info_log(request):
    # Získajte aktuálny dátum
    current_date = datetime.now().strftime("%d%m%Y")
    head='Log aktivit z aktuálneho dňa'

    # Cesta k súboru s logmi z aktuálneho dňa
    log_file_path = os.path.join(LOG_DIR, f'info.log')

    # Skontrolujte, či súbor existuje
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as file:
            log_content = file.read()
    else:
        log_content = "Log súbor neexistuje alebo nebol ešte vytvorený pre dnešný deň."

    # Odoslanie obsahu logu do šablóny
    return render(request, 'view_log.html', {'log_content': log_content, 'head':head})

@login_required
def bo_log(request):
    # delete dir
    dir = r"C:\Users\Public\APP\Prod_logs\save_logs_prod\APP"
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "APP"  
        parent_dir = r"C:\Users\Public\APP\Prod_logs\save_logs_prod"
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "APP"  
        parent_dir = r"C:\Users\Public\APP\Prod_logs\save_logs_prod"
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    # path =r"C:\Users\Public\APP\Prod_logs\save_logs_prod\acis-web01_BO\\"
    # isExist = os.path.exists(path)
    # if not isExist:
    #     os.makedirs(path)
    #     print("The new directory is created!")
    source_folder = r"\\acis-web01\\WEB\\BO\\Logs\\"
    # destination_folder = r"C:\Users\Public\APP\Prod_logs\save_logs_prod\acis-web01_BO\\"
    
    folder = r"C:\Users\Public\APP\Prod_logs\save_logs_prod\APP\\"
    try:
        with open(folder + 'web_BO_log.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB BO log from ACIS  ----------\n')
            print("Create web_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_web_log = r"C:\Users\Public\APP\Prod_logs\save_logs_prod\APP\web_BO_log.txt"

    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_web_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /acis-web01_BO/', filename )
       
    # # error color
    # with open(folder_web_log, 'r', encoding="utf-8") as file:
    #     filedata = file.read()
    #     # filedata = filedata.replace('INFO', 'INFO' )
    #     filedata = filedata.replace("INFO", "{}print{}".format(Fore.BLUE, Fore.RESET))

        
    # with open(folder_web_log, 'w', encoding="utf-8") as file:
    #     file.write(filedata)
    #     file.close()

    # open txt web_BO_log.txt
    f = open(folder_web_log, 'r', encoding="utf-8")
    file_content = f.read()
    # file_content = file_content.replace("INFO", "{}sadfasf{}".format(Fore.BLUE, Fore.RESET))
    f.close()
    context = {'file_content': file_content}
    return render(request, "txt.html", context)

@login_required
def logs(request):
    # remove these print statements later
    # if request.method == "GET":
    #     os.startfile(r'\\fileserver.internal.example.com\billien\CIS')

    # if request.method == 'POST':
    #     os.startfile(r'\\fileserver.internal.example.com\billien\CIS')
    
    return render(request, 'logs.html') #{'fname' : request.user.username }

def open_all_logs(request):
    os.startfile(r'\\fileserver.internal.example.com\billien\CIS')
    # return render(request, 'logs.html')
    return render(request,'logs.html')
    #     response = HttpResponse(path, content_type=mime_type)
    #     # Set the HTTP header for sending to browser
    #     response['Content-Disposition'] = "attachment; filename=%s" % filename
    #     # Return the response value
    #     return response

def download_acisBO(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisBO'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisBO"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisBO"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-web01\\WEB\\BO\\Logs\\"

    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisBO/'
    try:
        with open(folder + 'ACIS_BO_logs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-BO LOGS from ACIS  ----------\n')
            print("Create web_logs.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisBO/ACIS_BO_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_BO_logs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_BO_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisBO/' + filename
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

def download_bcisBO(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisBO'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisBO"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisBO"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-web01\\BOLogs\\"

    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisBO/'
    try:
        with open(folder + 'BCIS_BO_logs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-BO LOGS from BCIS  ----------\n')
            print("Create web_logs.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisBO/BCIS_BO_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_BO_logs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_BO_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisBO/' + filename
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

def download_acisPOS(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisPOS'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisPOS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisPOS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-web01\\WEB\\POS\\Logs\\"

    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisPOS/'
    try:
        with open(folder + 'ACIS_POS_logs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-POS LOGS from ACIS  ----------\n')
            print("Create web_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisPOS/ACIS_POS_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_POS_logs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_POS_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisPOS/' + filename
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

def download_bcisPOS(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisPOS'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisPOS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisPOS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-web01\\POSLogs\\"

    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisPOS/'
    try:
        with open(folder + 'BCIS_POS_log.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-POS LOGS from BCIS  ----------\n')
            print("Create web_logs.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisPOS/BCIS_POS_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_POS_logs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_POS_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisPOS/' + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value

    response.status_code = 200
    return response

def download_acisFCI(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisFCI'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisFCI"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisFCI"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-web02\\FCILogs\\"
    
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisFCI/'
    try:
        with open(folder + 'ACIS_FCI_logs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-FCI LOGS from ACIS  ----------\n')
            print("Create web_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisFCI/ACIS_FCI_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_FCI_log/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_FCI_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisFCI/' + filename
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

def download_bcisFCI(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisFCI'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisFCI"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisFCI"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-web02\\FCILogs\\"
    
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisFCI/'
    try:
        with open(folder + 'BCIS_FCI_logs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-FCI LOGS from BCIS  ----------\n')
            print("Create web_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisFCI/BCIS_FCI_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_FCI_log/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_FCI_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisFCI/' + filename
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

def download_acisSC(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisSC'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisSC"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisSC"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-web02\\SCLogs\\"
    
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisSC/'
    try:
        with open(folder + 'ACIS_SC_logs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-SC LOGS from ACIS  ----------\n')
            print("Create web_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisSC/ACIS_SC_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_SC_log/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_SC_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisSC/' + filename
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

def download_bcisSC(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisSC'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisSC"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisSC"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-web02\\SCLogs\\"
    
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisSC/'
    try:
        with open(folder + 'BCIS_SC_logs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL WEB-SC LOGS from BCIS  ----------\n')
            print("Create web_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisSC/BCIS_SC_logs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if "Web" in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_SC_log/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_SC_logs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisSC/' + filename
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

def download_acisIS_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisIS'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-is01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisIS/'
    try:
        with open(folder + 'ACIS_IS_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL IS ErrorLogs from ACIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisIS/ACIS_IS_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_IS_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_IS_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisIS/' + filename
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

def download_bcisIS_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisIS'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-is01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisIS/'
    try:
        with open(folder + 'BCIS_IS_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL IS ErrorLogs from BCIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisIS/BCIS_IS_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_IS_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_IS_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisIS/' + filename
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

def download_acisIS_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisIS'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-is01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisIS/'
    try:
        with open(folder + 'ACIS_IS_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL IS APPLogs from ACIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisIS/ACIS_IS_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_IS_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_IS_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisIS/' + filename
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

def download_bcisIS_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisIS'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisIS"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-is01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisIS/'
    try:
        with open(folder + 'BCIS_IS_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL IS APPLogs from BCIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisIS/BCIS_IS_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_IS_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_IS_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisIS/' + filename
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

def download_acisAPP01_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP01'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP01/'
    try:
        with open(folder + 'ACIS_APP01_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP01 ErrorLogs from ACIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP01/ACIS_APP01_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP01_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP01_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP01/' + filename
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

def download_acisAPP02_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP02'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app02\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP02/'
    try:
        with open(folder + 'ACIS_APP02_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP02 ErrorLogs from ACIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP02/ACIS_APP02_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP02_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP02/' + filename
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

def download_acisAPP03_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP03'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app03\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP03/'
    try:
        with open(folder + 'ACIS_APP03_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP03 ErrorLogs from ACIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP03/ACIS_APP03_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP03_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP03_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP03/' + filename
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

def download_acisAPP04_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP04'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app04\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP04/'
    try:
        with open(folder + 'ACIS_APP04_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP04 ErrorLogs from ACIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP04/ACIS_APP04_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP04_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP04_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP04/' + filename
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

def download_bcisAPP01_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP01'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP01/'
    try:
        with open(folder + 'BCIS_APP01_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP01 ErrorLogs from BCIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP01/BCIS_APP01_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP01_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP01_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP01/' + filename
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

def download_bcisAPP02_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP02'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app02\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP02/'
    try:
        with open(folder + 'BCIS_APP02_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP02 ErrorLogs from BCIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP02/BCIS_APP02_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP02_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP02_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP02/' + filename
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

def download_bcisAPP03_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP03'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app03\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP03/'
    try:
        with open(folder + 'BCIS_APP03_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP03 ErrorLogs from BCIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP03/BCIS_APP03_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP03_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP03_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP03/' + filename
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

def download_bcisAPP04_error(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP04'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app04\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP04/'
    try:
        with open(folder + 'BCIS_APP04_ErrorLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APP04 ErrorLogs from BCIS  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP04/BCIS_APP04_ErrorLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'Error' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP04_ErrorLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP04_ErrorLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP04/' + filename
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

def download_acisAPP01_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP01'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP01/'
    try:
        with open(folder + 'ACIS_APP01_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APPLogs from ACIS/APP01  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP01/ACIS_APP01_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP01_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP01_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP01/' + filename
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

def download_acisAPP02_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP02'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app02\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP02/'
    try:
        with open(folder + 'ACIS_APP02_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL  APPLogs from ACIS/acisAPP02  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP02/ACIS_APP02_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP02_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP02_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP02/' + filename
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

def download_acisAPP03_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP03'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app03\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP03/'
    try:
        with open(folder + 'ACIS_APP03_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL  APPLogs from ACIS/acisAPP03  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP03/ACIS_APP03_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP03_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP03_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP03/' + filename
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

def download_acisAPP04_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/acisAPP04'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "acisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "acisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\acis-app04\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/acisAPP04/'
    try:
        with open(folder + 'ACIS_APP04_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL  APPLogs from ACIS/acisAPP04  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/acisAPP04/ACIS_APP04_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nACIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /ACIS_APP03_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'ACIS_APP04_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/acisAPP04/' + filename
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

def download_bcisAPP01_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP01'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP01"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app01\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP01/'
    try:
        with open(folder + 'BCIS_APP01_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL APPLogs from BCIS/APP01  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP01/BCIS_APP01_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP01_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP01_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP01/' + filename
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

def download_bcisAPP02_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP02'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP02"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app02\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP02/'
    try:
        with open(folder + 'BCIS_APP02_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL  APPLogs from BCIS/bcisAPP02  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP02/BCIS_APP02_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP02_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP02_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP02/' + filename
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

def download_bcisAPP03_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP03'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP03"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app03\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP03/'
    try:
        with open(folder + 'BCIS_APP03_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL  APPLogs from BCIS/bcisAPP03  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP03/BCIS_APP03_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP03_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP03_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP03/' + filename
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

def download_bcisAPP04_app(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # delete dir
    dir = filepath = BASE_DIR + '/download_logs/bcisAPP04'
    isExist = os.path.exists(dir)
    if isExist:
        shutil.rmtree(dir)
        directory = "bcisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        # create dir
        directory = "bcisAPP04"  
        parent_dir = BASE_DIR + '/download_logs/'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    source_folder = r"\\bcis-app04\\Logs\\"
        
    # create txt file 
    folder = filepath = BASE_DIR + '/download_logs/bcisAPP04/'
    try:
        with open(folder + 'BCIS_APP04_APPLogs.txt', 'w') as f:
            f.write('---------------------------------------------  ALL  APPLogs from BCIS/bcisAPP04  ----------\n')
            print("Create is_log.txt")
    except FileNotFoundError:
        print("The 'docs' directory does not exist")
    folder_acis_log = BASE_DIR + '/download_logs/bcisAPP04/BCIS_APP04_APPLogs.txt'

    # append log in text
    for filename in os.listdir(source_folder):
        # if filename.endswith('.log'):       # konciaci na .log 
        # if filename.startswith('We', 7, 9):   # we je na 7 az 9 mieste
        if 'App' in str(filename):
    #         shutil.copy( source_folder + filename, destination_folder)
    #         # zapis do suboru web log txt
            with open(( source_folder + filename), 'r', encoding="utf-8") as reader, open(folder_acis_log,'a', encoding="utf-8") as a_writer:
                dog_breeds = reader.readlines()
                a_writer.write('\n')
                a_writer.write('\n')
                a_writer.write('\nBCIS//  ')
                a_writer.writelines(filename)
                a_writer.write(' \n')
                a_writer.write('  \n')
                a_writer.writelines((dog_breeds))
                a_writer.close()
                # koniec zapisu
                print('copied /BCIS_APP04_APPLogs/', filename )

    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'BCIS_APP04_APPLogs.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_logs/bcisAPP04/' + filename
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

from django.db import connection, connections
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@login_required
def users(request):

    db=CISDB.objects.get(user=request.user)
    con_CISDB_STDBY = cx_Oracle.connect(db.CISDB_username+"/"+db.CISDB_password+"@"+db.CISDB_hostname+":"+db.CISDB_port+"/"+db.CISDB_servicename)
    # cursor = con_CISDB_STDBY.cursor()

    job = CIS_SCHEDULED_JOB.objects.filter(job_id=59)
    j_instance = JOB_INSTANCE.objects.filter(job_id=59).order_by('-action_datetime')[:1]

    if 'q' in request.GET:
        q=request.GET['q'].lower()

        sql_ROLE_NAME ="""select ad.AD_USER_ID, ad.USERNAME, ad.SECURE_ID, CAST(FROM_TZ(CAST(ad.AD_CREATION_DATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as AD_CREATION_DATE, CAST(FROM_TZ(CAST(ad.DELETED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as DELETED_ON,
                            LISTAGG(rol.ROLE_NAME  || '; ') WITHIN GROUP (ORDER BY usr.user_id) "ROLE"
                            from CIS_AC.AD_USER ad
                            left join CIS_AC.USER_IN_ROLE usr on ad.AD_USER_ID=usr.USER_ID
                            left JOIN CIS_AC.ROLE rol on rol.ROLE_ID=usr.ROLE_ID
                            where ad.USERNAME like :usr  
                            GROUP BY ad.AD_USER_ID, ad.USERNAME, ad.SECURE_ID, ad.AD_CREATION_DATE, ad.DELETED_ON
                            ORDER BY AD_CREATION_DATE desc
                            """ 
        with con_CISDB_STDBY.cursor() as cursor:
            b = '%' + q + '%'
            cursor.execute(sql_ROLE_NAME, usr=b)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            us = dictfetchall(cursor)
            # print(us)
        
        sql_USER_DETAIL="""SELECT ad.USER_ID, ad.USER_NAME, ad.SECURE_ID, ad.SELFCARE_USER_GROUP_ID, CAST(FROM_TZ(CAST(ad.CREATION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CREATION_DATETIME, CAST(FROM_TZ(CAST(ad.EXPIRATION_DATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXPIRATION_DATE, CAST(FROM_TZ(CAST(ad.DELETED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as DELETED_ON, 
                            LISTAGG(rl.ROLE_NAME  || '; ') WITHIN GROUP (ORDER BY usr.user_id) "ROLE"
                            FROM CIS_AC.USER_DETAIL ad
                            left join CIS_AC.USER_IN_ROLE usr on ad.USER_ID=usr.USER_ID
                            left join  CIS_AC.ROLE rl on usr.ROLE_ID=rl.ROLE_ID
                            where USER_NAME like :usr
                            GROUP BY ad.USER_ID, ad.USER_NAME, ad.SECURE_ID, ad.SELFCARE_USER_GROUP_ID, ad.CREATION_DATETIME, ad.EXPIRATION_DATE, ad.DELETED_ON
                            ORDER BY CREATION_DATETIME desc"""
        with con_CISDB_STDBY.cursor() as cursor:
            d = '%' + q + '%'
            cursor.execute(sql_USER_DETAIL, usr=d)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ud = dictfetchall(cursor)




        # ud = CisUserDetail.objects.filter(username__contains=q)
    else:
        # us = CisAcAdUser.objects.all().order_by('-ad_creation_date')[:3]
        sql_aduser = """select * from (
                        select ad.AD_USER_ID, ad.USERNAME, ad.SECURE_ID, CAST(FROM_TZ(CAST(ad.AD_CREATION_DATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as AD_CREATION_DATE, CAST(FROM_TZ(CAST(ad.DELETED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as DELETED_ON,
                            LISTAGG(rol.ROLE_NAME  || '; ') WITHIN GROUP (ORDER BY usr.user_id) "ROLE"
                            from CIS_AC.AD_USER ad
                            left join CIS_AC.USER_IN_ROLE usr on ad.AD_USER_ID=usr.USER_ID
                            left JOIN CIS_AC.ROLE rol on rol.ROLE_ID=usr.ROLE_ID
                        --where ad.USERNAME like '%jozef%'
                        GROUP BY ad.AD_USER_ID, ad.USERNAME, ad.SECURE_ID, ad.AD_CREATION_DATE, ad.DELETED_ON
                        order by AD_CREATION_DATE desc)
                        where ROWNUM < 6 """
        with con_CISDB_STDBY.cursor() as cursor:
            cursor.execute(sql_aduser)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            us = dictfetchall(cursor)

        sql_USER_DETAIL="""select * from (
                        SELECT ad.USER_ID, ad.USER_NAME, ad.SECURE_ID, ad.SELFCARE_USER_GROUP_ID, CAST(FROM_TZ(CAST(ad.CREATION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CREATION_DATETIME, CAST(FROM_TZ(CAST(ad.EXPIRATION_DATE AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXPIRATION_DATE, CAST(FROM_TZ(CAST(ad.DELETED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as DELETED_ON, 
                            LISTAGG(rl.ROLE_NAME  || '; ') WITHIN GROUP (ORDER BY usr.user_id) "ROLE"
                        FROM CIS_AC.USER_DETAIL ad
                        left join CIS_AC.USER_IN_ROLE usr on ad.USER_ID=usr.USER_ID
                        left join  CIS_AC.ROLE rl on usr.ROLE_ID=rl.ROLE_ID
                        where CREATION_DATETIME >= trunc(sysdate-3)
                        GROUP BY ad.USER_ID, ad.USER_NAME, ad.SECURE_ID, ad.SELFCARE_USER_GROUP_ID, ad.CREATION_DATETIME, ad.EXPIRATION_DATE, ad.DELETED_ON
                        order by ad.CREATION_DATETIME desc
                        )
                        where ROWNUM < 6"""
        # with connections['cis_db'].cursor() as cursor:
        with con_CISDB_STDBY.cursor() as cursor:
            cursor.execute(sql_USER_DETAIL)
            ud = dictfetchall(cursor)

        
        # ud = CisUserDetail.objects.all().order_by('-creation_date')[:3]
    # # q = CisAcAdUser.objects.all()
    # print(q)

    sql_SCHEDULED_JOB = """SELECT * FROM (
            SELECT ins.SCHEDULED_JOB_ID, ins.START_ACTION_DATETIME, ins.EXECUTION_STATE_CODE,exe.EXECUTION_STATE_NAME, ins.EXPECTED_NUMBER_OF_ITEMS, ins.SUCCESSFULLY_PROCESSED_ITEMS
            FROM
            CIS_CO.JOB_INSTANCE ins 
            left join CIS_CO.EXECUTION_STATE_L exe on ins.EXECUTION_STATE_CODE=exe.EXECUTION_STATE_CODE
            where ins.SCHEDULED_JOB_ID=59 
            and exe.LANGUAGE_CODE='SK'
            order by START_ACTION_DATETIME desc)
            where  ROWNUM = 1
            """

    with con_CISDB_STDBY.cursor() as cursor:
        cursor.execute(sql_SCHEDULED_JOB)
        #rows = cursor.fetchall()        
        #rows = namedtuplefetchall(cursor)
        rows_ins = dictfetchall(cursor)
        # print(rows_ins)

    # cursor.close()
    # connection.close()    

    context ={'us': us, 'ud':ud, 'job':job, 'j_instance':j_instance, 'rows_ins': rows_ins}
    return render(request,'users.html', context)

 #(login_url='/signin')

@login_required
def jobs(request):

    cis_db=CISDB.objects.get(user=request.user)
    con_CISDB_STDBY = cx_Oracle.connect(cis_db.CISDB_username+"/"+cis_db.CISDB_password+"@"+cis_db.CISDB_hostname+":"+cis_db.CISDB_port+"/"+cis_db.CISDB_servicename)
    # cursor = con_CISDB_STDBY.cursor()

    job_s = ''
    # print('vysledok: '+job_s)\
    q = None

    sql_job = """SELECT * FROM(
                    SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME, 
                    EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS 
                    FROM CIS_CO.JOB_INSTANCE ji
                    left join CIS_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                    left join CIS_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
                    where
                    exs.LANGUAGE_CODE='SK' and START_ACTION_DATETIME >= trunc(sysdate-3) 
                                   --and ji.SCHEDULED_JOB_ID=143
                    and ji.EXECUTION_STATE_CODE!=4
                    --and UNSUCCESSFULLY_PROCESSED_ITEMS>0
                    or EXPECTED_NUMBER_OF_ITEMS !=SUCCESSFULLY_PROCESSED_ITEMS and exs.LANGUAGE_CODE='SK' and START_ACTION_DATETIME >= trunc(sysdate-3)
                    order by START_ACTION_DATETIME desc)
                    --where rownum <=8
                    """
    with con_CISDB_STDBY.cursor() as cursor:
        cursor.execute(sql_job)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        jobs_error = dictfetchall(cursor)

    if 'q' in request.GET:
        q=request.GET['q']

        sql_ROLE_NAME ="""SELECT CAST(FROM_TZ(CAST(ACTION_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACTION_DATETIME, ji.SCHEDULED_JOB_ID, JOB_NAME, EXECUTION_STATE_NAME, EXPECTED_NUMBER_OF_ITEMS, SUCCESSFULLY_PROCESSED_ITEMS, UNSUCCESSFULLY_PROCESSED_ITEMS 
                                FROM CIS_CO.JOB_INSTANCE ji
                                left join CIS_CO.EXECUTION_STATE_L exs on ji.EXECUTION_STATE_CODE=exs.EXECUTION_STATE_CODE
                                left join CIS_CO.SCHEDULED_JOB sj on ji.SCHEDULED_JOB_ID=sj.SCHEDULED_JOB_ID
                                where
                                exs.LANGUAGE_CODE='SK'
                                and START_ACTION_DATETIME >= trunc(sysdate-7)
                                and JOB_NAME like :id  
                                order by START_ACTION_DATETIME desc""" 
        with con_CISDB_STDBY.cursor() as cursor:
            c = '%' + q + '%'
            cursor.execute(sql_ROLE_NAME, id=c)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            job_s = dictfetchall(cursor)
            # print(job_s)
    # cursor.close()
    # connection.close()   

    context = { 'jobe': jobs_error, 'job_s':job_s, 'q':q }
    return render(request,'jobs.html', context)
# def url_redirect(request):
#     return redirect("//file://fileserver.internal.example.com/billien/CIS/")

@login_required
def bad_trans(request):
    # con_CISDB_STDBY = cx_Oracle.connect("DB_USER/DB_PASSWORD@db-host-b.internal.example.com:1521/cissrv_rdo")
    import cx_Oracle
    cis_db=CISDB.objects.get(user=request.user)
    print(cis_db.CISDB_username)
    con_CISDB_STDBY = cx_Oracle.connect(cis_db.CISDB_username+"/"+cis_db.CISDB_password+"@"+cis_db.CISDB_hostname+":"+cis_db.CISDB_port+"/"+cis_db.CISDB_servicename)
    # cursor = con_CISDB_STDBY.cursor()

    sql_REJECTED_TRANSACTION = """Select *
                                from CIS_FA.REJECTED_TRANSACTION
                                where DELETED_ON is NULL
                                ORDER BY TRANSACTION_DATA_ID
                                """
    with con_CISDB_STDBY.cursor() as cursor:
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
    cursor = con_CISDB_STDBY.cursor()

    # cursor = connections['cis_db'].cursor()

    cursor.callproc("dbms_output.enable")
    
    sqlCode = """
            declare 
            ----------------------------------------------------------------------------------------------
            v_transaction_data_id cis_fa.table_of_number_18_t := cis_fa.table_of_number_18_t(:cd);
            tid_to_display_count number := 5;
            consider_deleted_definition number := 0;
            ----------------------------------------------------------------------------------------------
            type t is table of varchar2(4000);
            criteria_ok t := t();
            criteria_bad t := t();
            transaction_item_def_id cis_fa.table_of_number_18_t := cis_fa.table_of_number_18_t();
            transaction_item_def_short cis_fa.table_of_varchar2_50_t := cis_fa.table_of_varchar2_50_t();
            oktab cis_fa.table_of_number_18_t := cis_fa.table_of_number_18_t();
            badtab cis_fa.table_of_number_18_t := cis_fa.table_of_number_18_t();
            val number;
            ok number;
            bad number;
            begin
            dbms_output.put_line (' ');
            -- transaction data loop
            for i in (select transaction_data_id, accounting_datetime
                        from cis_fa.transaction_data
                        where transaction_data_id in (select column_value from table(v_transaction_data_id))
                    ) loop
                dbms_output.put_line(lpad('*',100,'*'));
                dbms_output.put_line(rpad(' ',18,' ')
                                    ||'check transaction_data_id '||i.transaction_data_id
                                    ||', accounting datetime: '||to_char(cis_co.to_local_datetime(i.accounting_datetime),'dd.mm.yyyy')
                                    );
                dbms_output.put_line(lpad('*',100,'*'));
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
                            from cis_fa.transaction_item_def td
                                join cis_fa.transaction_def d using (transaction_def_id)
                            where exists (select 1.0 from cis_fa.selection_criteria sc where sc.transaction_item_def_id = td.transaction_item_def_id)
                            and (deleted_on is null and consider_deleted_definition = 0
                                or
                                consider_deleted_definition = 1
                                )
                                
                            order by transaction_item_def_short
                        ) loop
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
                                ,'nvl(to_char('||case upper(data_column_system_name) when 'OBU_OPERATION_TYPE_CODE' then 'OBU_STOCK_OPERATION_CODE' else data_column_system_name end||'),''null'')'
                                ||' in ('
                                ||listagg(''''||nvl(to_char(criteria_value),'null')||'''', ', ') within group (order by criteria_value nulls last)
                                ||')' criteria
                                ,data_column_system_name
                                ||case count(*) when 1 then ' = ' else ' in (' end
                                ||listagg(nvl(to_char(criteria_value),'null'), ', ') within group (order by criteria_value nulls last)
                                ||case count(*) when 1 then '' else ')' end disp_criteria
                            from cis_fa.selection_criteria sc
                                join cis_fa.data_column using (data_column_code)
                            where sc.transaction_item_def_id = j.transaction_item_def_id
                            group by data_column_system_name
                            order by data_column_system_name
                        ) loop
                    begin
                    execute immediate 'select '||case upper(k.data_column_system_name) when 'OBU_OPERATION_TYPE_CODE' then 'OBU_STOCK_OPERATION_CODE' else k.data_column_system_name end||' from cis_fa.transaction_data where transaction_data_id = '||i.transaction_data_id||' and '||k.criteria into val;
                    criteria_ok(criteria_ok.count) := criteria_ok(criteria_ok.count)||case when ok = 0 then '' else chr(10) end||'          '||k.disp_criteria||' --> '||nvl(to_char(val),'null');
                    ok := ok + 1;
                    exception
                    when no_data_found then 
                        execute immediate 'select '||case upper(k.data_column_system_name) when 'OBU_OPERATION_TYPE_CODE' then 'OBU_STOCK_OPERATION_CODE' else k.data_column_system_name end||' from cis_fa.transaction_data where transaction_data_id = '||i.transaction_data_id into val;
                        criteria_bad(criteria_bad.count) := criteria_bad(criteria_bad.count)||case when bad = 0 then '' else chr(10) end||'        x '||k.disp_criteria||' --> '||nvl(to_char(val),'null');
                        bad := bad + 1;
                    end;
                end loop;
                oktab.extend(1);
                oktab(oktab.count) := ok;
                badtab.extend(1);
                badtab(badtab.count) := bad;
                end loop;
                -- display results
                for i in (with b as (select column_value bad, rownum rn from table(badtab))
                            ,o as (select column_value ok, rownum rn from table(oktab))
                            ,tid as (select column_value transaction_item_def_id, rownum rn from table(transaction_item_def_id))
                            ,tsh as (select column_value transaction_item_def_short, rownum rn from table(transaction_item_def_short))
                        select t.*, rownum ord
                            from (
                                select ok, bad, rn, transaction_item_def_short, transaction_item_def_id, td.deleted_on, td.validity_start, td.validity_end
                                    from b 
                                        join o using (rn)
                                        join tid using (rn)
                                        join tsh using (rn)
                                        join cis_fa.transaction_item_def tid using(transaction_item_def_id, transaction_item_def_short)
                                        join cis_fa.transaction_def td on td.transaction_def_id = tid.transaction_def_id
                                    order by case when ok+bad = 0 then 0 else ok/(ok+bad) end desc, ok+bad desc, transaction_item_def_short, deleted_on desc nulls first
                                ) t
                            where rownum <= tid_to_display_count
                        ) loop
                dbms_output.put_line(case when i.ok+i.bad = 0 then '0%' else to_char(round(i.ok/(i.ok+i.bad)*100))||'%' end
                                    ||' '||i.transaction_item_def_short||' (item id '||i.transaction_item_def_id||'),'
                                    ||' validity: '||to_char(cis_co.to_local_datetime(i.validity_start),'dd.mm.yyyy')||' - '||nvl(to_char(cis_co.to_local_datetime(i.validity_end),'dd.mm.yyyy'),'...')
                                    ||case when i.deleted_on is not null then ' deleted on: '||to_char(cis_co.to_local_datetime(i.deleted_on),'dd.mm.yyyy') else '' end
                                    );
                if criteria_bad(i.rn) is not null then dbms_output.put_line(criteria_bad(i.rn)); end if;
                if criteria_ok(i.rn) is not null then dbms_output.put_line(criteria_ok(i.rn)); end if;
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
            f.write(m+ '\n')
        #     # f.write(str(l))
        #     f.writelines(str(m)
    folder_ = r"download_trans/Top_5_best_criteria.txt"

    p = open(folder_, 'r')
    file_content = p.read()
    p.close()

    # cursor.close()
    # connection.close()   
    
    context = { 'file_content':file_content, 'REJECTED_TRAN':REJECTED_TRANSACTION }
    
    return render(request,'transakce.html', context)

def download_DBMS(request):
    # ----download file ------------------
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'Top_5_best_criteria.txt'
    # Define the full file path
    filepath = BASE_DIR + '/download_trans/' + filename
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

@login_required
def awr(request):
    import sys
    # https://varmarakesh.bitbucket.io/python/2015/05/23/Oracle-AWR-Using-Python.html
    # cursor = con_CISDB_STDBY.cursor()

    cis_db=CISDB.objects.get(user=request.user)
    con_CISDB_STDBY = cx_Oracle.connect(cis_db.CISDB_username+"/"+cis_db.CISDB_password+"@"+cis_db.CISDB_hostname+":"+cis_db.CISDB_port+"/"+cis_db.CISDB_servicename)
    # cursor = con_CISDB_STDBY.cursor()

    sql_awr_SNAP_ID = """
                        SELECT SNAP_ID,
                        DBID,
                        INSTANCE_NUMBER,
                        CAST(FROM_TZ(CAST(BEGIN_INTERVAL_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as BEGIN_INTERVAL_TIME,
                        CAST(FROM_TZ(CAST(END_INTERVAL_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as END_INTERVAL_TIME
                        FROM dba_hist_snapshot
                        WHERE BEGIN_INTERVAL_TIME > trunc(sysdate-7,'DD')
                        AND
                        INSTANCE_NUMBER=2
                        ORDER BY SNAP_ID desc,
                        INSTANCE_NUMBER
                    """
 
    with con_CISDB_STDBY.cursor() as cursor:
        cursor.execute(sql_awr_SNAP_ID)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        AWR = dictfetchall(cursor)
        # print(AWR)
    
    if 'a' in request.GET and 'b' in request.GET:
        a=request.GET['a']
        b=request.GET['b']

        sql_awr_report = """
                        SELECT output FROM TABLE (dbms_workload_repository.awr_report_html(3286992334,2,:a,:b))
                        """
    
        with con_CISDB_STDBY.cursor() as cursor:
            
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
    return render(request,'awr.html', context)

def open_awr(request):
    # url = 'download_awr'+os.getcwd()+'/' + 'awr.html'
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # # Define text file name
    # filename = 'awr.html'
    # # Define the full file path
    # filepath = BASE_DIR + '/download_awr/' + filename
    return render(request, 'awr/awr.html')

@login_required
def dwh_control(request):
    import cx_Oracle
    # cis_db=CISDB.objects.get(user=request.user)
    dwh_db=DWHDB.objects.get(user=request.user)
    con_DWHDB_STDBY = cx_Oracle.connect(dwh_db.DWHDB_username+"/"+dwh_db.DWHDB_password+"@"+dwh_db.DWHDB_hostname+":"+dwh_db.DWHDB_port+"/"+dwh_db.DWHDB_servicename)
    # cursor = con_DWHDB_STDBY.cursor()

    sql_logs = """SELECT * FROM DWH_ETL.ETL_LOGS WHERE trunc (LOG_DATE) > SYSDATE - 10 AND  LOG_TYPE > 1 order by log_id desc"""

    with con_DWHDB_STDBY.cursor() as cursor:
        cursor.execute(sql_logs)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        dwh_logs = dictfetchall(cursor)
    # print(dwh_logs)

    sql_loading = """SELECT * FROM DWH_ETL.ETL_LOADINGS
                     WHERE LOAD_START > SYSDATE - 8 --AND LOAD_STATUS NOT IN ('R', 'S')
                     ORDER BY LOAD_START desc
                  """
    with con_DWHDB_STDBY.cursor() as cursor:
        cursor.execute(sql_loading)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        dwh_loading = dictfetchall(cursor)

    sql_PROCESSING_OVERVIEW = """	SELECT *
                                    FROM DWH_ETL.ETL_PROCESSING_OVERVIEW
                                    WHERE SRC_LOADING_START >= trunc(sysdate-2,'DD') --AND -- STG_SCHEMA_NAME LIKE 'STG_TCS3G_%' AND  AND (SRC_LOADING_STATUS != 2 OR PART_LOADING_STATUS != 2 OR STAGE_LOADING_STATUS != 2)
                                    ORDER by PART_LOADING_START desc
                  """
    with con_DWHDB_STDBY.cursor() as cursor:
        cursor.execute(sql_PROCESSING_OVERVIEW)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        dwh_PROCESSING_OVERVIEW = dictfetchall(cursor)
    
    # sql_ETL_TRACE_LOG = """SELECT *
    #                         FROM DWH_ETL.ETL_TRACE_LOG
    #                         WHERE LOG_TIMESTAMP >= trunc(sysdate-2,'DD') --AND LOG_TYPE_SEVERITY >= 4
    #                         --AND SOURCE_TABLE_OWNER='CIS_FA'\
    #                     ORDER BY LOG_TIMESTAMP desc
    #               """
    # with con_DWHDB_STDBY.cursor() as cursor:
    #     cursor.execute(sql_ETL_TRACE_LOG)
    #         #rows = cursor.fetchall()        
    #         #rows = namedtuplefetchall(cursor)
    #     dwh_trace_log = dictfetchall(cursor)

    context = {'dwh_loading': dwh_loading, 'dwh_PROCESSING_OVERVIEW':dwh_PROCESSING_OVERVIEW, 'dwh_logs':dwh_logs} 

    return render(request, 'dwh_control.html', context)

@login_required
def dwh_loading(request):
    import cx_Oracle
    # cis_db=CISDB.objects.get(user=request.user)
    dwh_db=DWHDB.objects.get(user=request.user)
    con_DWHDB_STDBY = cx_Oracle.connect(dwh_db.DWHDB_username+"/"+dwh_db.DWHDB_password+"@"+dwh_db.DWHDB_hostname+":"+dwh_db.DWHDB_port+"/"+dwh_db.DWHDB_servicename)
    # cursor = con_DWHDB_STDBY.cursor()

    sql_etl_processing_overview = """SELECT 
                                    ETL_LOAD_ID,
                                    STG_SCHEMA_NAME,
                                    SRC_LOADING_START,
                                    SRC_LOADING_END,
                                    DECODE(SRC_LOADING_STATUS, 3, '3 - chyba', 2, '2 - úspešne ukončené', 1, '1 - beží') SRC_LOADING_STATUS,
                                    PART_LOADING_START,
                                    PART_LOADING_END,
                                    DECODE(PART_LOADING_STATUS, 3, '3 - chyba', 2, '2 - úspešne ukončené', 1, '1 - beží') PART_LOADING_STATUS,
                                    STAGE_LOADING_START,
                                    STAGE_LOADING_END,
                                    DECODE(STAGE_LOADING_STATUS, 3, '3 - chyba', 2, '2 - úspešne ukončené', 1, '1 - beží') STAGE_LOADING_STATUS
                                    from DWH_ETL.ETL_PROCESSING_OVERVIEW where SRC_LOADING_START > TRUNC(sysdate-3, 'DD') ORDER BY SRC_LOADING_START desc
                                """
    with con_DWHDB_STDBY.cursor() as cursor:
        cursor.execute(sql_etl_processing_overview)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        etl_processing_overview = dictfetchall(cursor)
    
    sql_logs = """SELECT LOG_ID, LOAD_ID, JOB_ID, JOB_NAME, MOD_NAME, DECODE(LOG_TYPE, 3, '3-error', 2, '2-warning', 1, '1-info') LOG_TYPE,
 LOG_TEXT, LOG_STEP, LOG_DATE FROM DWH_ETL.ETL_LOGS WHERE trunc (LOG_DATE) > SYSDATE - 10 AND  LOG_TYPE > 1 order by log_id desc"""

    with con_DWHDB_STDBY.cursor() as cursor:
        cursor.execute(sql_logs)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        dwh_logs = dictfetchall(cursor)
    
    sql_ETL_LOADINGS = """  SELECT LOAD_ID, LOAD_PARAM, 
                            DECODE(LOAD_STATUS, 'W', 'W – upozornenie pri preskočenom loadingu', 'R', 'R – prebiehajúci', 'S', 'S – úspešne ukončený', 'E', 'E – chybne ukončený') LOAD_STATUS,
                            LOAD_START,
                            --CAST(FROM_TZ(CAST(LOAD_START AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LOAD_START,
                            LOAD_END,
                            --CAST(FROM_TZ(CAST(LOAD_END AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LOAD_END,
                            LOAD_NOTE,
                            ROUND((NVL(LOAD_END,LOAD_START)  - LOAD_START)*24, 0 ) || ' h' as diff_hours
                            from DWH_ETL.ETL_LOADINGS
                            where LOAD_START > TRUNC(sysdate-10, 'DD') 
                            order by LOAD_START desc
                        """
    with con_DWHDB_STDBY.cursor() as cursor:
        cursor.execute(sql_ETL_LOADINGS)
        # rows = cursor.fetchall()        
        # rows = namedtuplefetchall(cursor)
        ETL_LOADINGS = dictfetchall(cursor)
        
        
        # print(list(ETL_LOADINGS[2].items()))
        # print(rows)

    sql_ETL_TRACE_LOG = """SELECT 
                            ETL_TRACE_LOG_ID,
                            ETL_LOAD_ID,
                            CONFIG_ID,
                            PACKAGE_NAME,
                            PROCEDURE_NAME,
                            LINE_NUMBER,
                            SOURCE_DB_LINK,
                            SOURCE_TABLE_OWNER,
                            SOURCE_TABLE_NAME,
                            RUN_UNDER_SCHEMA,
                            CURRENT_SCHEMA,
                            TARGET_TABLE_OWNER,
                            TARGET_TABLE_NAME,
                            DECODE(LOG_TYPE_SEVERITY, 5, '5-chyba', 4, '4-upozornenie', 3, '3-informacia', 2, '2-odladovacie zaznamy', 1, '1-evidencia zaciatku a konca procedur') LOG_TYPE_SEVERITY,                     
                            LOG_TIMESTAMP,
                            LOG_MESSAGE_SHORT,
                            LOG_MESSAGE
                            FROM
                            DWH_ETL.ETL_TRACE_LOG 
                            where LOG_TIMESTAMP > trunc(sysdate,'DD')
                            order by LOG_TIMESTAMP desc
                            """
    with con_DWHDB_STDBY.cursor() as cursor:
        cursor.execute(sql_ETL_TRACE_LOG)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        ETL_TRACE_LOG = dictfetchall(cursor)

    context = {'etl_processing_overview':etl_processing_overview, 'ETL_LOADINGS':ETL_LOADINGS, 'dwh_logs':dwh_logs, 'ETL_TRACE_LOG':ETL_TRACE_LOG} 
    return render(request, 'dwh_loading.html', context)

@login_required
def bd_ack(request):
    import cx_Oracle
    cis_db=CISDB.objects.get(user=request.user)
    # print(cis_db.CISDB_username)
    con_CISDB_STDBY = cx_Oracle.connect(cis_db.CISDB_username+"/"+cis_db.CISDB_password+"@"+cis_db.CISDB_hostname+":"+cis_db.CISDB_port+"/"+cis_db.CISDB_servicename)
    cursor = con_CISDB_STDBY.cursor()

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
                    
                FROM cis_ede.ede_log bd
                JOIN cis_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN CIS_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN cis_ede.ede_log ack
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
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
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

                FROM cis_ede.ede_log bd
                JOIN cis_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN CIS_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN cis_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                --AND bd.created_on              > sysdate - 3
                )
                WHERE BD_CREATED_ON > to_date(%s, 'DD-MM-YYYY HH24:MI:SS')
                ORDER BY bd_created_on desc
        """
 
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_x, [x])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
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

                FROM cis_ede.ede_log bd
                JOIN cis_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN CIS_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN cis_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                --AND bd.created_on              > sysdate - 3
                )
                WHERE BD_CREATED_ON < to_date(%s, 'DD-MM-YYYY HH24:MI:SS')
                ORDER BY bd_created_on desc
        """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_y, [y])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
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

                FROM cis_ede.ede_log bd
                JOIN cis_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN CIS_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN cis_ede.ede_log ack
                ON bd.ede_log_id               = ack.referred_ede_log_id
                AND ack.ede_message_type_code  = 1
                AND ack.ede_log_status_code    = 1
                WHERE p.provider_abbreviation IN ( 'EW', 'ITIS' )
                AND bd.ede_message_type_code   = 4
                --AND bd.exported_on is not NULL
                --AND bd.created_on              > sysdate - 26 / 24
                --AND bd.created_on              > sysdate - 3
                )
                WHERE BD_CREATED_ON > to_date(%s, 'DD-MM-YYYY HH24:MI:SS')
                        AND BD_CREATED_ON < to_date(%s, 'DD-MM-YYYY HH24:MI:SS')
                ORDER BY bd_created_on desc
        """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_xy, [x,y])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
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

                FROM cis_ede.ede_log bd
                JOIN cis_ede.ede_log_status_l bds
                ON bd.ede_log_status_code = bds.ede_log_status_code
                AND bds.language_code     = 'CS'
                JOIN CIS_ECM.EETS_PROVIDER p
                ON bd.eets_provider_id = p.EETS_PROVIDER_ID
                LEFT JOIN cis_ede.ede_log ack
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
        with con_CISDB_STDBY.cursor() as cursor:
            cursor.execute(sql_ack)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            ack = dictfetchall(cursor)
            # print(ack)
            # print(ack)
    # print(y + 'toto ma byt y')
    
 
    context = {'ack':ack, 'ack_None':ack_None}
    return render(request, 'bd_ack.html', context)

    # # # # ERROR  ####
    # from django.conf.urls import (handler403, handler404, handler500)

    # def handler500(request):
    #     return render(request, 'authentication/profil.html')

@login_required
def wl_bl(request):
    import cx_Oracle
    cis_db=CISDB.objects.get(user=request.user)
    # print(cis_db.CISDB_username)
    con_CISDB_STDBY = cx_Oracle.connect(cis_db.CISDB_username+"/"+cis_db.CISDB_password+"@"+cis_db.CISDB_hostname+":"+cis_db.CISDB_port+"/"+cis_db.CISDB_servicename)
    cursor = con_CISDB_STDBY.cursor()
    
    error_wl_bl ="""
            Select
            EETS_INTEGRATION_LOG_ITEM_ID, INTEGRATION_LOG_ID, EETS_INT_LOG_STATUS_NAME, REJECT_METHOD_RESULT, exl.EXCEPTION_LIST_TYPE_NAME, APPROVAL_STATUS_CODE,
            p.PROVIDER_ABBREVIATION, MESSAGE_NUMBER, NEXT_MESSAGE_NUMBER, VERSION, 
            --EXCEPTION_LIST_VALID_FROM, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_FROM,
            --EXCEPTION_LIST_VALID_TO, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_TO,
            APPROVAL_DATE_TIME, APPROVED_BY, 
            --STARTED_ON,
            CAST(FROM_TZ(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as STARTED_ON,      
            LOG_FILE_CREATED_ON, 
            --ACK_FILE_CREATED_ON, 
            CAST(FROM_TZ(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_FILE_CREATED_ON,
            --PROCESS_DATE_TIME, 
            CAST(FROM_TZ(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as PROCESS_DATE_TIME,
            PROCESS_COUNT
            FROM CIS_ECM.EETS_INTEGRATION_LOG_ITEM ite
            JOIN cis_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'CS'
            JOIN cis_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND il.language_code = 'CS'
            JOIN CIS_ECM.EETS_PROVIDER p           ON ite.eets_provider_id = p.EETS_PROVIDER_ID
            --where EXCEPTION_LIST_VALID_FROM >= trunc(sysdate-7,'DD')
            where ACK_FILE_CREATED_ON is NULL and EXCEPTION_LIST_VALID_FROM >= trunc(sysdate-7,'DD') 
            or EETS_INT_LOG_STATUS_NAME != 'Zpracovaný'
            and EXCEPTION_LIST_VALID_FROM >= trunc(sysdate-7,'DD')
            ORDER BY EXCEPTION_LIST_VALID_FROM desc
            """
    cursor.execute(error_wl_bl)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
    wl_bl_error = dictfetchall(cursor)

    x = None
    y = None

    if 'x' in request.GET and request.GET['y'] =='':

        x = request.GET['x']
        y = request.GET['y']

        sql_x="""
            Select
            EETS_INTEGRATION_LOG_ITEM_ID, INTEGRATION_LOG_ID, EETS_INT_LOG_STATUS_NAME, REJECT_METHOD_RESULT, exl.EXCEPTION_LIST_TYPE_NAME, APPROVAL_STATUS_CODE,
            p.PROVIDER_ABBREVIATION, MESSAGE_NUMBER, NEXT_MESSAGE_NUMBER, VERSION, 
            --EXCEPTION_LIST_VALID_FROM, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_FROM,
            --EXCEPTION_LIST_VALID_TO, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_TO,
            APPROVAL_DATE_TIME, APPROVED_BY, 
            --STARTED_ON,
            CAST(FROM_TZ(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as STARTED_ON,      
            LOG_FILE_CREATED_ON, 
            --ACK_FILE_CREATED_ON, 
            CAST(FROM_TZ(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_FILE_CREATED_ON,
            --PROCESS_DATE_TIME, 
            CAST(FROM_TZ(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as PROCESS_DATE_TIME,
            PROCESS_COUNT
            FROM CIS_ECM.EETS_INTEGRATION_LOG_ITEM ite
            JOIN cis_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'CS'
            JOIN cis_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND il.language_code = 'CS'
            JOIN CIS_ECM.EETS_PROVIDER p           ON ite.eets_provider_id = p.EETS_PROVIDER_ID
            where EXCEPTION_LIST_VALID_FROM >= to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS') - (2 / 24))
            ORDER BY EXCEPTION_LIST_VALID_FROM desc
            """


        # > to_date(%s, 'DD-MM-YYYY HH24:MI:SS')
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_x, [x])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            wl_bl = dictfetchall(cursor)

    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']

        sql_y="""
            Select
            EETS_INTEGRATION_LOG_ITEM_ID, INTEGRATION_LOG_ID, EETS_INT_LOG_STATUS_NAME, REJECT_METHOD_RESULT, exl.EXCEPTION_LIST_TYPE_NAME, APPROVAL_STATUS_CODE,
            p.PROVIDER_ABBREVIATION, MESSAGE_NUMBER, NEXT_MESSAGE_NUMBER, VERSION, 
            --EXCEPTION_LIST_VALID_FROM, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_FROM,
            --EXCEPTION_LIST_VALID_TO, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_TO,
            APPROVAL_DATE_TIME, APPROVED_BY, 
            --STARTED_ON,
            CAST(FROM_TZ(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as STARTED_ON,      
            LOG_FILE_CREATED_ON, 
            --ACK_FILE_CREATED_ON, 
            CAST(FROM_TZ(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_FILE_CREATED_ON,
            --PROCESS_DATE_TIME, 
            CAST(FROM_TZ(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as PROCESS_DATE_TIME,
            PROCESS_COUNT
            FROM CIS_ECM.EETS_INTEGRATION_LOG_ITEM ite
            JOIN cis_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'CS'
            JOIN cis_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND il.language_code = 'CS'
            JOIN CIS_ECM.EETS_PROVIDER p           ON ite.eets_provider_id = p.EETS_PROVIDER_ID
            where EXCEPTION_LIST_VALID_FROM < to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS') - (2 / 24))
            ORDER BY EXCEPTION_LIST_VALID_FROM desc
            """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_y, [y])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            wl_bl = dictfetchall(cursor)
    
    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
            Select
            EETS_INTEGRATION_LOG_ITEM_ID, INTEGRATION_LOG_ID, EETS_INT_LOG_STATUS_NAME, REJECT_METHOD_RESULT, exl.EXCEPTION_LIST_TYPE_NAME, APPROVAL_STATUS_CODE,
            p.PROVIDER_ABBREVIATION, MESSAGE_NUMBER, NEXT_MESSAGE_NUMBER, VERSION, 
            --EXCEPTION_LIST_VALID_FROM, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_FROM,
            --EXCEPTION_LIST_VALID_TO, 
            CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_TO,
            APPROVAL_DATE_TIME, APPROVED_BY, 
            --STARTED_ON,
            CAST(FROM_TZ(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as STARTED_ON,      
            LOG_FILE_CREATED_ON, 
            --ACK_FILE_CREATED_ON, 
            CAST(FROM_TZ(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_FILE_CREATED_ON,
            --PROCESS_DATE_TIME, 
            CAST(FROM_TZ(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as PROCESS_DATE_TIME,
            PROCESS_COUNT
            FROM CIS_ECM.EETS_INTEGRATION_LOG_ITEM ite
            JOIN cis_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'CS'
            JOIN cis_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND il.language_code = 'CS'
            JOIN CIS_ECM.EETS_PROVIDER p           ON ite.eets_provider_id = p.EETS_PROVIDER_ID
            where 
            EXCEPTION_LIST_VALID_FROM >= to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS') - (2 / 24))
            and EXCEPTION_LIST_VALID_FROM < to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS') - (2 / 24))
            ORDER BY EXCEPTION_LIST_VALID_FROM desc
            """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_xy, [x,y])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            wl_bl = dictfetchall(cursor)
        

    else:
        sql_wl_bl ="""
                    Select
                    EETS_INTEGRATION_LOG_ITEM_ID, INTEGRATION_LOG_ID, EETS_INT_LOG_STATUS_NAME, REJECT_METHOD_RESULT, exl.EXCEPTION_LIST_TYPE_NAME, APPROVAL_STATUS_CODE,
                    p.PROVIDER_ABBREVIATION, MESSAGE_NUMBER, NEXT_MESSAGE_NUMBER, VERSION, 
                    --EXCEPTION_LIST_VALID_FROM, 
                    CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_FROM AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_FROM,
                    --EXCEPTION_LIST_VALID_TO, 
                    CAST(FROM_TZ(CAST(EXCEPTION_LIST_VALID_TO AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as EXCEPTION_LIST_VALID_TO,
                    APPROVAL_DATE_TIME, APPROVED_BY, 
                    --STARTED_ON,
                    CAST(FROM_TZ(CAST(STARTED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as STARTED_ON,      
                    LOG_FILE_CREATED_ON, 
                    --ACK_FILE_CREATED_ON, 
                    CAST(FROM_TZ(CAST(ACK_FILE_CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as ACK_FILE_CREATED_ON,
                    --PROCESS_DATE_TIME, 
                    CAST(FROM_TZ(CAST(PROCESS_DATE_TIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as PROCESS_DATE_TIME,
                    PROCESS_COUNT
                    FROM CIS_ECM.EETS_INTEGRATION_LOG_ITEM ite
                    JOIN cis_ECM.EETS_INT_LOG_STATUS_L il ON ite.EETS_IL_STATUS_CODE = il.EETS_INT_LOG_STATUS_CODE AND il.language_code = 'CS'
                    JOIN cis_ECM.EXCEPTION_LIST_TYPE_L exl ON ite.EXCEPTION_LIST_TYPE_CODE = exl.EXCEPTION_LIST_TYPE_CODE AND il.language_code = 'CS'
                    JOIN CIS_ECM.EETS_PROVIDER p           ON ite.eets_provider_id = p.EETS_PROVIDER_ID
                    where EXCEPTION_LIST_VALID_FROM >= trunc(sysdate-5,'DD')
                    ORDER BY EXCEPTION_LIST_VALID_FROM desc
                    """
        with con_CISDB_STDBY.cursor() as cursor:
                cursor.execute(sql_wl_bl)
                #rows = cursor.fetchall()        
                #rows = namedtuplefetchall(cursor)
                wl_bl = dictfetchall(cursor) 

    context = {'wl_bl':wl_bl, 'wl_bl_error': wl_bl_error}
    return render(request, 'wl_bl.html', context)

@login_required
def obu_event(request):

    cis_db=CISDB.objects.get(user=request.user)
    # print(cis_db.CISDB_username)
    con_CISDB_STDBY = cx_Oracle.connect(cis_db.CISDB_username+"/"+cis_db.CISDB_password+"@"+cis_db.CISDB_hostname+":"+cis_db.CISDB_port+"/"+cis_db.CISDB_servicename)
    cursor = con_CISDB_STDBY.cursor()

    x = None
    y = None

    sql_event ="""
            Select
            OBU_EH_ID,
            OBU_STOCK_ITEM_ID,
            OBU_SN,
            ACCOUNT_ID,
            ACCOUNT_NUMBER,
            ACCOUNT_TYPE_CODE,
            ACCOUNT_TYPE_NAME,
            POSTPAID_ACCOUNT_TYPE_CODE,
            POSTPAID_ACCOUNT_TYPE_NAME,
            --CREATED_ON as CREATED_ON,
            CAST(FROM_TZ(CAST(CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CREATED_ON,
            EXECUTED_BY	APPLICATION_CODE,
            POS_ID,
            RETAIL_PARTNER_ABBR,
            POS_NUMBER,
            POS_TYPE_CODE,
            LOCATION_TYPE_NAME,
            OPERATION_CODE,
            OPERATION_NAME,
            OBU_ID,
            STOCK_ID,
            OBU_OL_STATUS_CODE,
            OBU_OL_STATUS_NAME,
            OPERATIONAL_STATUS,
            OBU_OP_STATUS_NAME,
            ORDER_DATA_ID
            from xosa.CIS_OL_OBU_EVENT
            where CREATED_ON >  trunc(sysdate,'DD')- (2 / 24)
            and OPERATION_NAME='Neúspěšný výdej zákazníkovi'
            order by CREATED_ON desc
            """
    cursor.execute(sql_event)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
    event_error = dictfetchall(cursor)

    if 'x' in request.GET and request.GET['y'] =='':

        x = request.GET['x']
        y = request.GET['y']

        sql_x="""Select
            OBU_EH_ID,
            OBU_STOCK_ITEM_ID,
            OBU_SN,
            ACCOUNT_ID,
            ACCOUNT_NUMBER,
            ACCOUNT_TYPE_CODE,
            ACCOUNT_TYPE_NAME,
            POSTPAID_ACCOUNT_TYPE_CODE,
            POSTPAID_ACCOUNT_TYPE_NAME,
            --CREATED_ON as CREATED_ON,
            CAST(FROM_TZ(CAST(CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CREATED_ON,
            EXECUTED_BY	APPLICATION_CODE,
            POS_ID,
            RETAIL_PARTNER_ABBR,
            POS_NUMBER,
            POS_TYPE_CODE,
            LOCATION_TYPE_NAME,
            OPERATION_CODE,
            OPERATION_NAME,
            OBU_ID,
            STOCK_ID,
            OBU_OL_STATUS_CODE,
            OBU_OL_STATUS_NAME,
            OPERATIONAL_STATUS,
            OBU_OP_STATUS_NAME,
            ORDER_DATA_ID
            from xosa.CIS_OL_OBU_EVENT
            where CREATED_ON >= to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS')- (2 / 24))
            order by CREATED_ON desc
            """

        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_x, [x])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sql_event = dictfetchall(cursor)
    
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']

        sql_y="""
            Select
            OBU_EH_ID,
            OBU_STOCK_ITEM_ID,
            OBU_SN,
            ACCOUNT_ID,
            ACCOUNT_NUMBER,
            ACCOUNT_TYPE_CODE,
            ACCOUNT_TYPE_NAME,
            POSTPAID_ACCOUNT_TYPE_CODE,
            POSTPAID_ACCOUNT_TYPE_NAME,
            --CREATED_ON as CREATED_ON,
            CAST(FROM_TZ(CAST(CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CREATED_ON,
            EXECUTED_BY	APPLICATION_CODE,
            POS_ID,
            RETAIL_PARTNER_ABBR,
            POS_NUMBER,
            POS_TYPE_CODE,
            LOCATION_TYPE_NAME,
            OPERATION_CODE,
            OPERATION_NAME,
            OBU_ID,
            STOCK_ID,
            OBU_OL_STATUS_CODE,
            OBU_OL_STATUS_NAME,
            OPERATIONAL_STATUS,
            OBU_OP_STATUS_NAME,
            ORDER_DATA_ID
            from xosa.CIS_OL_OBU_EVENT
            where CREATED_ON < to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS') - (2 / 24))
            order by CREATED_ON desc
            """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_y, [y])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sql_event = dictfetchall(cursor)
    
    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        sql_xy="""
            Select
            OBU_EH_ID,
            OBU_STOCK_ITEM_ID,
            OBU_SN,
            ACCOUNT_ID,
            ACCOUNT_NUMBER,
            ACCOUNT_TYPE_CODE,
            ACCOUNT_TYPE_NAME,
            POSTPAID_ACCOUNT_TYPE_CODE,
            POSTPAID_ACCOUNT_TYPE_NAME,
            --CREATED_ON as CREATED_ON,
            CAST(FROM_TZ(CAST(CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CREATED_ON,
            EXECUTED_BY	APPLICATION_CODE,
            POS_ID,
            RETAIL_PARTNER_ABBR,
            POS_NUMBER,
            POS_TYPE_CODE,
            LOCATION_TYPE_NAME,
            OPERATION_CODE,
            OPERATION_NAME,
            OBU_ID,
            STOCK_ID,
            OBU_OL_STATUS_CODE,
            OBU_OL_STATUS_NAME,
            OPERATIONAL_STATUS,
            OBU_OP_STATUS_NAME,
            ORDER_DATA_ID
            from xosa.CIS_OL_OBU_EVENT     
            where      
            CREATED_ON >= to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS') - (2 / 24))
            and CREATED_ON < to_char(to_date(%s, 'DD-MM-YYYY HH24:MI:SS') - (2 / 24))
            order by CREATED_ON desc
            """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_xy, [x,y])
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
            sql_event = dictfetchall(cursor)
    
    else:
        sql_event ="""
            Select
            OBU_EH_ID,
            OBU_STOCK_ITEM_ID,
            OBU_SN,
            ACCOUNT_ID,
            ACCOUNT_NUMBER,
            ACCOUNT_TYPE_CODE,
            ACCOUNT_TYPE_NAME,
            POSTPAID_ACCOUNT_TYPE_CODE,
            POSTPAID_ACCOUNT_TYPE_NAME,
            --CREATED_ON as CREATED_ON,
            CAST(FROM_TZ(CAST(CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as CREATED_ON,
            EXECUTED_BY	APPLICATION_CODE,
            POS_ID,
            RETAIL_PARTNER_ABBR,
            POS_NUMBER,
            POS_TYPE_CODE,
            LOCATION_TYPE_NAME,
            OPERATION_CODE,
            OPERATION_NAME,
            OBU_ID,
            STOCK_ID,
            OBU_OL_STATUS_CODE,
            OBU_OL_STATUS_NAME,
            OPERATIONAL_STATUS,
            OBU_OP_STATUS_NAME,
            ORDER_DATA_ID
            from xosa.CIS_OL_OBU_EVENT
            where CREATED_ON >  trunc(sysdate,'DD')- (2 / 24)
            --and OPERATION_NAME='Neúspěšný výdej zákazníkovi'
            order by CREATED_ON desc
            """
        cursor.execute(sql_event)
            #rows = cursor.fetchall()        
            #rows = namedtuplefetchall(cursor)
        sql_event = dictfetchall(cursor)

    context = {'sql_event':sql_event, 'event_error':event_error}
    return render(request, 'obu_event.html', context)

@login_required
def cisdb(request):
    export = ''
    column_names_list = ''
    q = None

    if 'q' in request.GET:
        q=request.GET['q']

        cis_db=CISDB.objects.get(user=request.user)
        con_CISDB_STDBY = cx_Oracle.connect(cis_db.CISDB_username+"/"+cis_db.CISDB_password+"@"+cis_db.CISDB_hostname+":"+cis_db.CISDB_port+"/"+cis_db.CISDB_servicename)
    
        sql_query =q

        with con_CISDB_STDBY.cursor() as cursor:
            cursor.execute(sql_query)
            # export1 = cursor.description
            column_names_list = [x[0] for x in cursor.description]
            # export = dictfetchall(cursor)
            

            # cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
            export = cursor.fetchall()
            # print(export)

    context = {'export':export, 'column_names_list':column_names_list,  'q':q }
    return render(request, 'cisdb.html', context)

@login_required
def dwhdb(request):
    export = ''
    column_names_list = ''
    q = None

    if 'q' in request.GET:
        q=request.GET['q']

        dwh_db=DWHDB.objects.get(user=request.user)
        con_DWHDB_STDBY = cx_Oracle.connect(dwh_db.DWHDB_username+"/"+dwh_db.DWHDB_password+"@"+dwh_db.DWHDB_hostname+":"+dwh_db.DWHDB_port+"/"+dwh_db.DWHDB_servicename)
    
        sql_query =q

        with con_DWHDB_STDBY.cursor() as cursor:
            cursor.execute(sql_query)
            # export1 = cursor.description
            column_names_list = [x[0] for x in cursor.description]
            # export = dictfetchall(cursor)
            

            # cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
            export = cursor.fetchall()
            # print(export)

    context = {'export':export, 'column_names_list':column_names_list, 'q':q }
    return render(request, 'dwhdb.html', context)

@login_required
def sc_login(request):
    db=CISDB.objects.get(user=request.user)
    con_CISDB_STDBY = cx_Oracle.connect(db.CISDB_username+"/"+db.CISDB_password+"@"+db.CISDB_hostname+":"+db.CISDB_port+"/"+db.CISDB_servicename)
    # cursor = con_CISDB_STDBY.cursor()

    x = None
    y = None
    sc_sms =''

    if 'x' in request.GET and request.GET['y'] =='':
        
    # if x is not None and x != '' :
        x = request.GET['x']
        y = request.GET['y']
    # if 'x' in request.GET and 'y' == ' ' :
        sql_phone="""SELECT 
                l.USER_NAME,
                SELFCARE_USER_GROUP_ID,
                det.PHONE,
                ud.USER_ID,
                det.EMAIL,
                CAST(FROM_TZ(CAST(l.LOGIN_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LOGIN_DATETIME,
                lr.LOGIN_ATTEMPT_RESULT_NAME,
                ud.LAST_LOGIN_DATETIME,
                ud.LAST_ACTIVITY_DATETIME
                FROM CIS_AC.LOGIN_ATTEMPT l
                LEFT JOIN CIS_AC.LOGIN_ATTEMPT_RESULT_L lr ON l.LOGIN_ATTEMPT_RESULT_CODE=lr.LOGIN_ATTEMPT_RESULT_CODE AND lr.LANGUAGE_CODE='CS'
                LEFT JOIN CIS_AC.USER_DATA ud ON ud.USER_ID=l.USER_ID
                LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=l.USER_ID
                    where PHONE like %s
                    --and l.LOGIN_ATTEMPT_RESULT_CODE !=1 and ud.USER_ID is not null
                    order by l.LOGIN_DATETIME desc"""

        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_phone, [x])
                    #rows = cursor.fetchall()        
                    #rows = namedtuplefetchall(cursor)
            sc_result = dictfetchall(cursor)

        sql_p_sms="""
                    select
                    a.USER_ID as "ID_Uzivatela",
                    a.PHONE as "Telefonne_cislo",
                    det.USER_NAME as "Username",
                    --a.CREATED_ON as "SMS_odoslana_dňa",
                    CAST(FROM_TZ(CAST(a.CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as "Datum_odoslania_SMS"
                    --a.*
                    from CIS_AC.LOGIN_OTP a
                    LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=a.USER_ID
                    where a.phone = %s -- skopirovat tel. cislo z IM alebo ho vyhladat v BO - PV/Kontaktne osoby
                    ORDER BY CREATED_ON desc
                    """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_p_sms, [x])
                    #rows = cursor.fetchall()        
                    #rows = namedtuplefetchall(cursor)
            sc_sms = dictfetchall(cursor)
    elif 'y' in request.GET and request.GET['x'] =='':
        x =None
        y = request.GET['y']
        sql_username="""SELECT 
                l.USER_NAME,
                SELFCARE_USER_GROUP_ID,
                det.PHONE,
                ud.USER_ID,
                det.EMAIL,
                CAST(FROM_TZ(CAST(l.LOGIN_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LOGIN_DATETIME,
                lr.LOGIN_ATTEMPT_RESULT_NAME,
                ud.LAST_LOGIN_DATETIME,
                ud.LAST_ACTIVITY_DATETIME
                FROM CIS_AC.LOGIN_ATTEMPT l
                LEFT JOIN CIS_AC.LOGIN_ATTEMPT_RESULT_L lr ON l.LOGIN_ATTEMPT_RESULT_CODE=lr.LOGIN_ATTEMPT_RESULT_CODE AND lr.LANGUAGE_CODE='CS'
                LEFT JOIN CIS_AC.USER_DATA ud ON ud.USER_ID=l.USER_ID
                LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=l.USER_ID
                    where l.USER_NAME like %s
                    --and l.LOGIN_ATTEMPT_RESULT_CODE !=1 and ud.USER_ID is not null
                    order by l.LOGIN_DATETIME desc"""
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_username, [y])
                    #rows = cursor.fetchall()        
                    #rows = namedtuplefetchall(cursor)
            sc_result = dictfetchall(cursor)

        sql_p_sms="""
                    select
                    a.USER_ID as "ID_Uzivatela",
                    a.PHONE as "Telefonne_cislo",
                    det.USER_NAME as "Username",
                    --a.CREATED_ON as "SMS_odoslana_dňa",
                    CAST(FROM_TZ(CAST(a.CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as "Datum_odoslania_SMS"
                    --a.*
                    from CIS_AC.LOGIN_OTP a
                    LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=a.USER_ID
                    where det.USER_NAME = %s
                    ORDER BY CREATED_ON desc
                    """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_p_sms, [y])
                    #rows = cursor.fetchall()        
                    #rows = namedtuplefetchall(cursor)
            sc_sms = dictfetchall(cursor)
            print(sc_sms)
    
    elif 'x' in request.GET and 'y' in request.GET:
        x=request.GET['x']
        y=request.GET['y']
        # print(x)
        # print(y)

        sql_p_u="""SELECT 
                l.USER_NAME,
                SELFCARE_USER_GROUP_ID,
                det.PHONE,
                ud.USER_ID,
                det.EMAIL,
                CAST(FROM_TZ(CAST(l.LOGIN_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LOGIN_DATETIME,
                lr.LOGIN_ATTEMPT_RESULT_NAME,
                ud.LAST_LOGIN_DATETIME,
                ud.LAST_ACTIVITY_DATETIME
                FROM CIS_AC.LOGIN_ATTEMPT l
                LEFT JOIN CIS_AC.LOGIN_ATTEMPT_RESULT_L lr ON l.LOGIN_ATTEMPT_RESULT_CODE=lr.LOGIN_ATTEMPT_RESULT_CODE AND lr.LANGUAGE_CODE='CS'
                LEFT JOIN CIS_AC.USER_DATA ud ON ud.USER_ID=l.USER_ID
                LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=l.USER_ID
                    where l.USER_NAME like %s and phone like %s
                    --and l.LOGIN_ATTEMPT_RESULT_CODE !=1 and ud.USER_ID is not null
                    order by l.LOGIN_DATETIME desc"""
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_p_u, [y,x])
                    #rows = cursor.fetchall()        
                    #rows = namedtuplefetchall(cursor)
            sc_result = dictfetchall(cursor)

        sql_p_sms="""
                    select
                    a.USER_ID as "ID_Uzivatela",
                    a.PHONE as "Telefonne_cislo",
                    det.USER_NAME as "Username",
                    --a.CREATED_ON as "SMS_odoslana_dňa",
                    CAST(FROM_TZ(CAST(a.CREATED_ON AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as "Datum_odoslania_SMS"
                    --a.*
                    from CIS_AC.LOGIN_OTP a
                    LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=a.USER_ID
                    where det.USER_NAME = %s and a.phone = %s
                    ORDER BY CREATED_ON desc
                    """
        with connections['cis_db'].cursor() as cursor:
            cursor.execute(sql_p_sms, [y,x])
                    #rows = cursor.fetchall()        
                    #rows = namedtuplefetchall(cursor)
            sc_sms = dictfetchall(cursor)
            # print(sc_sms)
    
    else:
        sql_login="""
                    SELECT 
                    l.USER_NAME,
                    SELFCARE_USER_GROUP_ID,
                    det.PHONE,
                    ud.USER_ID,
                    det.EMAIL,
                    CAST(FROM_TZ(CAST(l.LOGIN_DATETIME AS TIMESTAMP), 'GMT') AT TIME ZONE 'CET' AS DATE) as LOGIN_DATETIME,
                    lr.LOGIN_ATTEMPT_RESULT_NAME,
                    ud.LAST_LOGIN_DATETIME,
                    ud.LAST_ACTIVITY_DATETIME
                    FROM CIS_AC.LOGIN_ATTEMPT l
                    LEFT JOIN CIS_AC.LOGIN_ATTEMPT_RESULT_L lr ON l.LOGIN_ATTEMPT_RESULT_CODE=lr.LOGIN_ATTEMPT_RESULT_CODE AND lr.LANGUAGE_CODE='CS'
                    LEFT JOIN CIS_AC.USER_DATA ud ON ud.USER_ID=l.USER_ID
                    LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=l.USER_ID
                        where LOGIN_DATETIME >= trunc(sysdate-0,'DD')-(2/24) 
                        and l.LOGIN_ATTEMPT_RESULT_CODE !=1 and ud.USER_ID is not null
                        order by l.LOGIN_DATETIME desc
                    """
        with con_CISDB_STDBY.cursor() as cursor:
                cursor.execute(sql_login)
                #rows = cursor.fetchall()        
                #rows = namedtuplefetchall(cursor)
                sc_result = dictfetchall(cursor)
                # print(sc_result)


    # ------------------------------- graph ----------------------------------------------
    labels = []
    data = []
    neprihlaseny_nep= 0
    neprihlaseny_jed_heslo = 0
    neprihlaseny_pos = 0

    select_graph="""SELECT 
                        LOGIN_ATTEMPT_RESULT_NAME,
                            COUNT(*) as pocet

                    FROM CIS_AC.LOGIN_ATTEMPT l
                    LEFT JOIN CIS_AC.LOGIN_ATTEMPT_RESULT_L lr ON l.LOGIN_ATTEMPT_RESULT_CODE=lr.LOGIN_ATTEMPT_RESULT_CODE AND lr.LANGUAGE_CODE='CS'
                    LEFT JOIN CIS_AC.USER_DATA ud ON ud.USER_ID=l.USER_ID
                    LEFT JOIN CIS_AC.USER_DETAIL det ON det.USER_ID=l.USER_ID
                        where l.LOGIN_DATETIME >= trunc(sysdate-0,'DD')  + INTERVAL '-120' MINUTE
                        --and l.LOGIN_ATTEMPT_RESULT_CODE !=1 
                        and ud.USER_ID is not null
                        GROUP BY LOGIN_ATTEMPT_RESULT_NAME"""
    with con_CISDB_STDBY.cursor() as cursor:
        db_data = cursor.execute(select_graph)
        db_result = cursor.execute(select_graph)

        nmcol=[row[0] for row in db_data.description]

        for row in cursor:
            # print(row[nmcol.index('LOGIN_ATTEMPT_RESULT_NAME')])
            labels.append(row[nmcol.index('LOGIN_ATTEMPT_RESULT_NAME')])
            # print(labels)

    with con_CISDB_STDBY.cursor() as cursor:
        db_result = cursor.execute(select_graph)
        uspesne_login=db_result.fetchone()[1]
        print(uspesne_login)
        # print(uspesne_login)
        neprihlaseny_heslo=db_result.fetchone()[1]
        print(neprihlaseny_heslo)
        neprihlaseny_jed_heslo=db_result.fetchone()[1]
        print(neprihlaseny_jed_heslo)
          
        if neprihlaseny_jed_heslo is None:
            print('a')
            neprihlaseny_jed_heslo=0
            print('jed ' + int(neprihlaseny_jed_heslo))
        print('jed heslo' + str(neprihlaseny_jed_heslo))
        
        
        # print(neprihlaseny_nep)
        if neprihlaseny_pos is None:
            print('b')
            neprihlaseny_pos=0
        else:
            print('sdfafsd')
            # neprihlaseny_nep=(db_result.fetchone()[1])

        spolu= uspesne_login+neprihlaseny_heslo+neprihlaseny_jed_heslo+neprihlaseny_pos
        
        # print(spolu)
        succes_login=int((uspesne_login/spolu*100))
        # print(succes_login)
        error_login=int((neprihlaseny_heslo/spolu*100))
        error_one_login=int((neprihlaseny_jed_heslo/spolu*100))
        error_pos_login=int((neprihlaseny_pos/spolu*100))

        data = [succes_login, error_login, error_one_login, error_pos_login]


    
    context = {'sc_result':sc_result, 'labels': labels, 'data': data,
                'uspesne_login':uspesne_login, 'neprihlaseny_heslo':neprihlaseny_heslo, 'neprihlaseny_jed_heslo':neprihlaseny_jed_heslo,
                'neprihlaseny_pos':neprihlaseny_pos, 'sc_sms':sc_sms}
    return render(request, 'sc_login.html', context)

@login_required
def val_test(request):

    context = {}
    return render(request, 'val_test.html', context)

def handler500(request):
    messages.error(request, "500 Error Page (Not Found)")
    context = {}
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response


@login_required
def test(request):
    import cx_Oracle
    EMS_DWH=EMS_DWHDB.objects.get(user=request.user)
    con_BILLDB_STDBY = cx_Oracle.connect(EMS_DWH.EMS_DWHDB_username+"/"+EMS_DWH.EMS_DWHDB_password+"@"+EMS_DWH.EMS_DWHDB_hostname+":"+EMS_DWH.EMS_DWHDB_port+"/"+EMS_DWH.EMS_DWHDB_servicename)
    cursor = con_BILLDB_STDBY.cursor()
    print('connect'+' / ' +EMS_DWH.EMS_DWHDB_username+" / "+EMS_DWH.EMS_DWHDB_password )
    print(cursor)
    return render(request, 'base_ems.html')



