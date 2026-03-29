"""
Gunicorn configuration file for production deployment.
Usage: gunicorn -c gunicorn_config.py config.wsgi:application
"""

import multiprocessing
import os

# ============================================================
# SERVER SOCKET
# ============================================================
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:10000')  # Render uses port 10000
backlog = 2048

# ============================================================
# WORKERS
# ============================================================
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# ============================================================
# SERVER MECHANICS
# ============================================================
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# ============================================================
# LOGGING
# ============================================================
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')  # stdout
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')    # stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'

# ============================================================
# PROCESS NAME
# ============================================================
proc_name = 'analytics-api'

# ============================================================
# HOOKS
# ============================================================
def on_starting(server):
    print("Gunicorn server starting...")

def on_exit(server):
    print("Gunicorn server exiting...")