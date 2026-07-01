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
      	# Hook into the apscheduler logger
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    # Adding this job here instead of to crons.
    # This will do the following:
    # - Add a scheduled job to the job store on application initialization
    # - The job will execute a model class method at midnight each day
    # - replace_existing in combination with the unique ID prevents duplicate copies of the job
    # scheduler.add_job("work.models.MyModel.my_class_method", "cron", id="my_class_method", hour='12', replace_existing=True)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = os.path.join(BASE_DIR, 'work', 'static', 'json', 'jobs.json')
    
    with open(file_name, 'r') as file:
        json_inputs = json.load(file)
    for json_input in json_inputs:
        if json_input['model'] == 'marketingove_statistiky':
            marketingove_statistiky = json_input
            break
    run_dict = json.loads(marketingove_statistiky['fields']['run'])
    print(run_dict)
    hour = run_dict['hour']
    minute = run_dict['minute']
    day = run_dict['day']
    month = run_dict['month']

    trigger = CronTrigger(hour=hour, minute=minute, day=day, month=month)
    print(trigger)
    # with open(file_name, 'r') as file:
    #     json_inputs = json.load(file)
    # set_run= [json_input['fields']['run'] for json_input in json_inputs if json_input['model'] == 'marketingove_statistiky']
    # set_run_text=list(set_run)[0]
    # run_args = set_run_text
    # # trigger = CronTrigger(**run_args)

    scheduler.add_job(report_Mark_stat, trigger, id="marketingove_statistiky", replace_existing=True)
    scheduler.add_job(my_job, 'cron', month= '*', day= '*', hour= '10',  minute='39', id="test_", replace_existing=True)
    # Add the scheduled jobs to the Django admin interface
    register_events(scheduler)

    scheduler.start()

