import logging, os, json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job
from .views_ems import my_job, report_Mark_stat

from django.conf import settings

import ast

from apscheduler.triggers.cron import CronTrigger

# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

def start():
    if settings.DEBUG:

        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'work', 'static', 'json', 'jobs.json')
    
    with open(file_name, 'r') as file:
        json_inputs = json.load(file)
    for json_input in json_inputs:
        if json_input['model'] == 'marketingove_statistiky':
            marketingove_statistiky = json_input
            break
    run_dict = json.loads(marketingove_statistiky['fields']['run'])
    hour = run_dict['hour']
    minute = run_dict['minute']
    day = run_dict['day']
    month = run_dict['month']

    trigger = CronTrigger(hour=hour, minute=minute, day=day, month=month)

    scheduler.add_job(report_Mark_stat, trigger, id="marketingove_statistiky", replace_existing=True)
    register_events(scheduler)

    scheduler.start()

def reload_marketingove_statistiky_job():
    job_id = "marketingove_statistiky"
    try:
        # Remove the existing job
        scheduler.remove_job(job_id)
    except JobLookupError:
        logging.warning(f"Job {job_id} not found")

    file_name = os.path.join(settings.BASE_DIR, 'work', 'static', 'json', 'jobs.json')

    try:
        with open(file_name, 'r') as file:
            json_inputs = json.load(file)
    except FileNotFoundError:
        logging.error(f"jobs.json file not found at {file_name}")
        return
    except JSONDecodeError:
        logging.error(f"Invalid JSON data in jobs.json file")
        return

    marketingove_statistiky_job = None
    for json_input in json_inputs:
        if json_input['model'] == 'marketingove_statistiky':
            marketingove_statistiky_job = json_input
            break

    if marketingove_statistiky_job:
        run_config = json.loads(marketingove_statistiky_job['fields']['run'])
        hour = run_config['hour']
        minute = run_config['minute']
        day = run_config['day']
        month = run_config['month']
        trigger = CronTrigger(hour=hour, minute=minute, day=day, month=month)

        # Add the new job
        scheduler.add_job(report_Mark_stat, trigger, id=job_id, replace_existing=True)
    else:
        logging.warning("marketingove_statistiky job not found in jobs.json")
