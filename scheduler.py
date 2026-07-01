# scheduler.py
import logging
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import register_events

# Importujte potrebné funkcie z vašich aplikácií
from eets.views_scheduler import report_EETS_Lego, Rating_job, PX_obe_positions
from work.views_ems import report_Mark_stat, paywell_scheduler, inactivity_report, daily_reports
from edz.views import report_edz_podania

# Vytvorenie scheduleru
scheduler = None

def start():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

        if settings.DEBUG:
            logging.basicConfig()
            logging.getLogger('apscheduler').setLevel(logging.DEBUG)

        # Načítanie úloh z jobs.json
        load_jobs('eets/static/json/jobs.json', {
            'model': 'EETS_Lego',
            'function': report_EETS_Lego
        })
        load_jobs('work/static/json/jobs.json', {
            'model': 'marketingove_statistiky',
            'function': report_Mark_stat
        })
        load_jobs('edz/static/json/jobs.json', {
            'model': 'EDZ_Podania',
            'function': report_edz_podania
        })
        # load_jobs('eets/static/json/jobs.json', {
        #     'model': 'EETS_RATING',
        #     'function': Rating_job
        # })
        load_jobs('eets/static/json/jobs.json', {
            'model': 'EETS_OBE',
            'function': PX_obe_positions
        })
        load_jobs('work/static/json/jobs.json', {
             'model': 'paywell',
             'function': paywell_scheduler
        })
        load_jobs('work/static/json/jobs.json', {
             'model': 'inactivity',
             'function': inactivity_report
        })
        load_jobs('work/static/json/jobs.json', {
             'model': 'daily_reports',
             'function': daily_reports
        })

        register_events(scheduler)
        scheduler.start()

def load_jobs(file_path, job_info):
    jobs_file_path = os.path.join(settings.BASE_DIR, file_path)

    try:
        with open(jobs_file_path, 'r') as file:
            jobs_data = json.load(file)

        job = next((job for job in jobs_data if job['model'] == job_info['model']), None)
        if job:
            run_config = json.loads(job['fields']['run'])
            trigger = CronTrigger(**run_config)
            #scheduler.add_job(job_info['function'], trigger, id=job_info['model'], replace_existing=True)
            scheduler.add_job(
                job_info['function'],
                trigger,
                id=job_info['model'],
                replace_existing=True,
                misfire_grace_time=60,  # tolerancia na zmeškanie (v sekundách)
                coalesce=True,          # zlučuje zmeškané joby do jedného spustenia
                max_instances=1         # zabráni paralelnému spusteniu
            )

        else:
            logging.warning(f"{job_info['model']} job not found in {file_path}")

    except FileNotFoundError:
        logging.error(f"jobs.json file not found at {jobs_file_path}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON data in jobs.json file")
    except KeyError as e:
        logging.error(f"KeyError: {e}")

# Funkcie na opätovné načítanie úloh
# (nechajte ich tak, ako sú, ak ich plánujete použiť)

    except FileNotFoundError:
        logging.error(f"jobs.json file not found at {jobs_file_path}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON data in jobs.json file")
    except KeyError as e:
        logging.error(f"KeyError: {e}")

def reload_job(job_id, file_path, job_info):
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        logging.warning(f"Job {job_id} not found")

    load_jobs(file_path, job_info)

# opatovne nacitanie dat do schedulera z json ku konkretnym jobom

def reload_job_if_lego(job_id, file_path):
    try:
        if job_id == 'EETS_Lego':
            reload_job(job_id, file_path, {
                'model': job_id,
                'function': report_EETS_Lego
            })
        else:
            logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
    except Exception as e:
        logging.error(f"Error reloading job {job_id}: {e}")

# def reload_job_if_rating(job_id, file_path):
#     try:
#         # Skontrolujte, či by sa job mal deaktivovať
#         if job_id == 'EETS_RATING':
#             logging.info(f"Job '{job_id}' je deaktivovaný a nebude opätovne načítaný.")
#             return  # Preskočte opätovné načítanie tohto jobu
#         else:
#             reload_job(job_id, file_path, {
#                 'model': job_id,
#                 'function': Rating_job
#             })
#     # try:
#     #     if job_id == 'EETS_RATING':
#     #         reload_job(job_id, file_path, {
#     #             'model': job_id,
#     #             'function': Rating_job
#     #         })
#     #     else:
#     #         logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
#     except Exception as e:
#         logging.error(f"Error reloading job {job_id}: {e}")

def reload_job_if_obe_positions(job_id, file_path):
    try:
        if job_id == 'EETS_OBE':
            reload_job(job_id, file_path, {
                'model': job_id,
                'function': PX_obe_positions
            })
        else:
            logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
    except Exception as e:
        logging.error(f"Error reloading job {job_id}: {e}")

def reload_job_if_markstat(job_id, file_path):
    try:
        if job_id == 'marketingove_statistiky':
            reload_job(job_id, file_path, {
                'model': job_id,
                'function': report_Mark_stat
            })
        else:
            logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
    except Exception as e:
        logging.error(f"Error reloading job {job_id}: {e}")

def reload_job_if_edz_podania(job_id, file_path):
    try:
        if job_id == 'EDZ_Podania':
            reload_job(job_id, file_path, {
                'model': job_id,
                'function': report_edz_podania
            })
        else:
            logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
    except Exception as e:
        logging.error(f"Error reloading job {job_id}: {e}")

def reload_job_if_paywell(job_id, file_path):
    try:
        if job_id == 'paywell':
            reload_job(job_id, file_path, {
                'model': job_id,
                'function': paywell_scheduler
            })
        else:
            logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
    except Exception as e:
        logging.error(f"Error reloading job {job_id}: {e}")

def reload_job_if_inactivity(job_id, file_path):
    try:
        if job_id == 'inactivity':
            reload_job(job_id, file_path, {
                'model': job_id,
                'function': inactivity_report
            })
        else:
            logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
    except Exception as e:
        logging.error(f"Error reloading job {job_id}: {e}")

def reload_job_if_daily_reports(job_id, file_path):
    try:
        if job_id == 'daily_reports':
            reload_job(job_id, file_path, {
                'model': job_id,
                'function': daily_reports
            })
        else:
            logging.warning(f"Job ID '{job_id}' is not recognized for reloading.")
    except Exception as e:
        logging.error(f"Error reloading job {job_id}: {e}")
