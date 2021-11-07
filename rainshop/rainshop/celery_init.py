from __future__ import absolute_import
import os
from celery.decorators import task
import celery as cel
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings

import celery.signals
logger = get_task_logger('django')

# set the default Django settings module for the 'celery_' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainshop.settings')
app = cel.Celery('rainshop', task_ignore_result=False)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
	"""
	This method sets up periodic tasks.
	"""
	# handling of the periodic task that deletes all blacklisted tokens
	sender.add_periodic_task()
