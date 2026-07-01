from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoScheduledJob
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def my_job():
    print("I love python {}".format(datetime.now()))

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # add jobs here
    scheduler.add_job(my_job, 'interval', minutes=1)
    scheduler.start()

if __name__ == '__main__':

    start()