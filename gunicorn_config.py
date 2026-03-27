"""
Gunicorn configuration file for production deployment.
Usage: gunicorn -c gunicorn_config.py config.wsgi:application
"""

import multiprocessing
import os
from decouple import config

# Server socket
bind = config('GUNICORN_BIND', default='0.0.0.0:8000')
backlog = 2048

# Worker Processes
workers = config('GUNICORN_WORKERS', default=multiprocessing.cpu_count() * 2 + 1, cast=int)
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = config('GUNICORN_ACCESS_LOG', default='-')
errorlog = config('GUNICORN_ERROR_LOG', default='-')
loglevel = config('GUNICORN_LOG_LEVEL', default='info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'analytics-api'

# Server hooks
def on_starting(server):
    print("Gunicorn server starting...")

def on_exit(server):
    print("Gunicorn server exiting...")