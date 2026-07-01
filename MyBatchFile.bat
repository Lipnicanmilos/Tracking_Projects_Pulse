@echo off
start /B cmd /c call ./env/Scripts/activate.bat & c:\Tracking_Projects_Pulse\env\Scripts\python.exe manage.py runserver --insecure 8000 --noreload
pause