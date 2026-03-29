"""
Gunicorn configuration file for production deployment.
"""

import multiprocessing
import os

bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:10000')  # Render uses port 10000
backlog = 2048

workers = int(os.environ.get('GUNICORN_WORKERS', '1'))
worker_class = 'sync'
threads = 2  # Added: Use 2 threads per worker for concurrency
worker_connections = 100  # Reduced from 1000 (memory concern)
timeout = 60  # Reduced from 120 (prevent hung requests holding memory)
keepalive = 2

daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')  # stdout
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')    # stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

access_log_format = '%(h)s %(l)s %(b)s "%(r)s" %(s)s %(D)s'


proc_name = 'analytics-api'

def on_starting(server):
    print("Gunicorn server starting...")

def on_exit(server):
    print("Gunicorn server exiting...")