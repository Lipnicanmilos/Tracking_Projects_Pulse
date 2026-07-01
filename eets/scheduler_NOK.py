import logging, os, json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job
from .views import report_EETS_Lego #, test_job_my  # Ensure you import your new job function

from django.conf import settings
from apscheduler.triggers.cron import CronTrigger

def test_job_my():
    print('test_job_my')

# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

def start():
    if settings.DEBUG:
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    jobs_file_path = os.path.join(settings.BASE_DIR, 'eets', 'static', 'json', 'jobs.json')

    try:
        with open(jobs_file_path, 'r') as file:
            jobs_data = json.load(file)

        # Handle EETS_Lego job
        eets_lego_job = next((job for job in jobs_data if job['model'] == 'EETS_Lego'), None)
        if eets_lego_job:
            eets_lego_run_config = json.loads(eets_lego_job['fields']['run'])
            trigger = CronTrigger(**eets_lego_run_config)
            scheduler.add_job(report_EETS_Lego, trigger, id="EETS_Lego", replace_existing=True)
        else:
            logging.warning("EETS_Lego job not found in jobs.json")

        # Handle test_job_my job
        test_job = next((job for job in jobs_data if job['model'] == 'test_job_my'), None)
        if test_job:
            test_job_run_config = json.loads(test_job['fields']['run'])
            trigger = CronTrigger(**test_job_run_config)
            scheduler.add_job(test_job_my, trigger, id="test_job_my", replace_existing=True, max_instances=1)
        else:
            logging.warning("test_job_my job not found in jobs.json")

    except FileNotFoundError:
        logging.error(f"jobs.json file not found at {jobs_file_path}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON data in jobs.json file")
    except KeyError as e:
        logging.error(f"KeyError: {e}")

    register_events(scheduler)
    scheduler.start()

def reload_report_EETS_Lego_job():
    job_id = "EETS_Lego"
    try:
        # Remove the existing job
        scheduler.remove_job(job_id)
    except JobLookupError:
        logging.warning(f"Job {job_id} not found")

    jobs_file_path = os.path.join(settings.BASE_DIR, 'eets', 'static', 'json', 'jobs.json')

    try:
        with open(jobs_file_path, 'r') as file:
            jobs_data = json.load(file)
    except FileNotFoundError:
        logging.error(f"jobs.json file not found at {jobs_file_path}")
        return
    except JSONDecodeError:
        logging.error(f"Invalid JSON data in jobs.json file")
        return

    eets_lego_job = None
    for job in jobs_data:
        if job['model'] == 'EETS_Lego':
            eets_lego_job = job
            break

    if eets_lego_job:
        eets_lego_run_config = json.loads(eets_lego_job['fields']['run'])
        hour = eets_lego_run_config['hour']
        minute = eets_lego_run_config['minute']
        day = eets_lego_run_config['day']
        month = eets_lego_run_config['month']
        trigger = CronTrigger(hour=hour, minute=minute, day=day, month=month)

        # Add the new job
        scheduler.add_job(report_EETS_Lego, trigger, id=job_id, replace_existing=True)
    else:
        logging.warning("EETS_Lego job not found in jobs.json")