import sqlite3
from apscheduler.util import undefined
import logging
import uuid

logger = logging.getLogger("scheduler_logger")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('mylog.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

def add_interval_schedule(schedudler, func, **kwargs):

    params = {
        'args': None,
        'kwargs': None,
        'name': None,
        'misfire_grace_time': undefined,
        'coalesce': undefined,
        'max_instances': undefined,
        'next_run_time': undefined,
        'jobstore': 'default',
        'executor': 'default',
        'trigger': 'interval',
        'replace_existing':False}
    for k, v in kwargs.items():
        if k not in ('trigger','args', 'kwargs', 'id', 'name', 'misfire_grace_time', 'coalesce'
                     'max_instances', 'next_run_time', 'jobstore', 'executor', 'replace_existing',
                     'trigger', 'days', 'weeks', 'hours', 'minutes', 'seconds', 'start_date', 'end_date'):
            logger.error('%s is not supported'%k)
        else:
            params[k] = v

    if params['name']:
        logger.info('定时器\'%s\'的参数为%s' % (params['name'], params))
    else:
        logger.info('定时器\'%s\'的参数为%s'%(func.__name__, params))

    id = str(uuid.uuid1())
    try:
        schedudler.add_job(id=id, func=func, **params)
        return "定时器添加成功"
    except Exception as e:
        logger.error("定时器添加失败，错误信息：%s"%e)
        return "定时器添加失败，详细信息请见log文件"

def del_scheduler(scheduler, id):
    if query_scheduler(id):
        try:
            scheduler.remove_job(id)
            return "已删除：%s"%id
        except Exception as e:
            logger.error("定时器删除失败，错误信息：%s" % e)
            return "定时器删除失败，详细信息请见log文件"
    else:
        return "定时器删除失败，无该id的job: %s"%id
        logger.info("无该id的job: %s"%id)

def query_scheduler(id=None):
    db_path = 'config/scheduler/jobstores.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apscheduler_jobs';")
    is_table_exists = cur.fetchall()
    result = []
    if is_table_exists and id:
        cur.execute("select * from apscheduler_jobs where id='%s'"%id)
        result = cur.fetchall()
    else:
        cur.execute("select * from apscheduler_jobs")
        result = cur.fetchall()
    if result:
        return True
    else:
        return False

def get_scheduler_list(scheduler):
    job_infos = []
    for j in scheduler.get_jobs():
        job_infos.append({'id': j.id, 'name': j.name})
    return job_infos