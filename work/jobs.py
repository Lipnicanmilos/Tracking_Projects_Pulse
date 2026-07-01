from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .views_ems import my_job, report_Mark_stat


    #https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(my_job, 'cron', hour='23', minute=33)
    # job na marketingove statistiky
    # trigger = CronTrigger(year="*", month="*", day="3", hour="0", minute="35", second="00")
    # scheduler.add_job(report_Mark_stat, trigger=trigger, id=str(id))
    scheduler.add_job(report_Mark_stat,'cron', month= '*', day= '3', hour= '12',  minute='36', id="marketingove_statistiky")
    # scheduler.add_job(report_Mark_stat, 'cron', month='*', day=3, hour=0, minute=55, second=00)
    scheduler.start()
    
    
