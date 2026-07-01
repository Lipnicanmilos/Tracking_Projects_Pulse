import logging, os, json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job
from .views import report_edz_crv, report_edz_podania

from django.conf import settings

from apscheduler.triggers.cron import CronTrigger


# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG_EDZ)

def start():
    if settings.DEBUG:
      	# Hook into the apscheduler logger
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    jobs_file_path = os.path.join(settings.BASE_DIR, 'edz', 'static', 'json', 'jobs.json')

    try:
        with open(jobs_file_path, 'r') as file:
            jobs_data = json.load(file)

        edz_crv_job = None
        edz_podania_job = None

        for job in jobs_data:
            if job['model'] == 'EDZ_CRV':
                edz_crv_job = job

            elif job['model'] == 'EDZ_Podania':
                edz_podania_job = job

        if edz_crv_job:
            edz_crv_run_config = json.loads(edz_crv_job['fields']['run'])
            hour = edz_crv_run_config['hour']
            minute = edz_crv_run_config['minute']
            day = edz_crv_run_config['day']
            month = edz_crv_run_config['month']
            trigger = CronTrigger(hour=hour, minute=minute, day=day, month=month)
        else:
            logging.warning("EDZ_CRV job not found in jobs.json")
            return

        if edz_podania_job:
            edz_podania_run_config = json.loads(edz_podania_job['fields']['run'])
            hour_podania = edz_podania_run_config['hour']
            minute_podania = edz_podania_run_config['minute']
            day_podania = edz_podania_run_config['day']
            month_podania = edz_podania_run_config['month']
            trigger_podania = CronTrigger(hour=hour_podania, minute=minute_podania, day=day_podania, month=month_podania)
        else:
            logging.warning("EDZ_Podania job not found in jobs.json")
            return


    except FileNotFoundError:

        logging.error(f"jobs.json file not found at {jobs_file_path}")

    except JSONDecodeError:

        logging.error(f"Invalid JSON data in jobs.json file")

    except KeyError as e:

        logging.error(f"KeyError: {e}")

    scheduler.add_job(report_edz_crv, trigger, id="EDZ_CRV", replace_existing=True)
    scheduler.add_job(report_edz_podania, trigger_podania, id="EDZ_Podania", replace_existing=True)

    register_events(scheduler)

    scheduler.start()

def reload_edz_podania_job():
    job_id = "EDZ_Podania"
    try:
        # Remove the existing job
        scheduler.remove_job(job_id)
    except JobLookupError:
        logging.warning(f"Job {job_id} not found")

    jobs_file_path = os.path.join(settings.BASE_DIR, 'edz', 'static', 'json', 'jobs.json')

    try:
        with open(jobs_file_path, 'r') as file:
            jobs_data = json.load(file)
    except FileNotFoundError:
        logging.error(f"jobs.json file not found at {jobs_file_path}")
        return
    except JSONDecodeError:
        logging.error(f"Invalid JSON data in jobs.json file")
        return

    edz_podania_job = None
    for job in jobs_data:
        if job['model'] == 'EDZ_Podania':
            edz_podania_job = job
            break

    if edz_podania_job:
        edz_podania_run_config = json.loads(edz_podania_job['fields']['run'])
        hour_podania = edz_podania_run_config['hour']
        minute_podania = edz_podania_run_config['minute']
        day_podania = edz_podania_run_config['day']
        month_podania = edz_podania_run_config['month']
        trigger_podania = CronTrigger(hour=hour_podania, minute=minute_podania, day=day_podania, month=month_podania)

        # Add the new job
        scheduler.add_job(report_edz_podania, trigger_podania, id=job_id, replace_existing=True)
    else:
        logging.warning("EDZ_Podania job not found in jobs.json")

def reload_edz_crv_job():
    job_id = "EDZ_CRV"
    try:
        # Remove the existing job
        scheduler.remove_job(job_id)
    except JobLookupError:
        logging.warning(f"Job {job_id} not found")

    jobs_file_path = os.path.join(settings.BASE_DIR, 'edz', 'static', 'json', 'jobs.json')

    try:
        with open(jobs_file_path, 'r') as file:
            jobs_data = json.load(file)
    except FileNotFoundError:
        logging.error(f"jobs.json file not found at {jobs_file_path}")
        return
    except JSONDecodeError:
        logging.error(f"Invalid JSON data in jobs.json file")
        return

    edz_crv_job = None
    for job in jobs_data:
        if job['model'] == 'EDZ_CRV':
            edz_crv_job = job
            break

    if edz_crv_job:
        edz_crv_run_config = json.loads(edz_crv_job['fields']['run'])
        hour = edz_crv_run_config['hour']
        minute = edz_crv_run_config['minute']
        day = edz_crv_run_config['day']
        month = edz_crv_run_config['month']
        trigger = CronTrigger(hour=hour, minute=minute, day=day, month=month)

        # Add the new job
        scheduler.add_job(report_edz_crv, trigger, id=job_id, replace_existing=True)
    else:
        logging.warning("EDZ_CRV job not found in jobs.json")