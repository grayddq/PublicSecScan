# -*- coding: utf-8 -*-
from celery import Celery, platforms
from lib.scanAwvs import *

NAME, VERSION, AUTHOR, LICENSE = "PublicSecScan", "V0.1", "咚咚呛", "Public (FREE)"

app = Celery()
platforms.C_FORCE_ROOT = True
DEBUG_INFO = True
app.conf.update(
    CELERY_IMPORTS=("tasks",),
    BROKER_URL='redis://:' + REDIS_PASSWORD + '@' + REDIS_HOST + ':' + str(REDIS_PORT) + '/' + str(REDIS_DB),
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_REDIS_MAX_CONNECTIONS=5000,
    BROKER_HEARTBEAT=30,
    BROKER_TRANSPORT_OPTIONS={'visibility_timeout': 3600},
    # CELERY_ROUTES={
    #    'tasks.sec_dispath': {'queue': 'sec_dispath'},
    # },
)


@app.task(name='tasks.sec_dispath')
def sec_dispath(targets):
    try:
        AWVS_Scan(targets).run()
    except Exception, e:
        return
    return
