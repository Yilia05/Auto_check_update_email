import logging
import os
import datetime
import thread
from apscheduler.schedulers.background import BackgroundScheduler

log_filename = "update_log"
LOG = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

log_format = '[%(asctime)s]   %(message)s'
logging.basicConfig(format=log_format,datafmt='%Y-%m-%d %H:%M:%S %p', level=logging.INFO, filename='update_check.log',
                    filemode='w')


def start():
    LOG.info('---------------start-------------')
    scheduler.add_job(test_job, 'interval', seconds=10)

    test_job()
    scheduler.start()


def test_job():
    print "hello, world! now time is : ", datetime.datetime.today()


def node_all_job():
    os.system('./crontabfile.sh')

if __name__ == '__main__':
    thread.start_new_thread(start, ())
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    while 1:
        pass
