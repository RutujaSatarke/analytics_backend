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
# WORKERS - OPTIMIZED FOR 512MB RAM
# ============================================================
# CRITICAL: On 512MB RAM, we can only afford 1-2 worker processes
# Each worker baseline = 60-80MB (Django + models loaded)
# workers = 1: Uses ~120MB total (1 worker + master process)
# workers = 2: Uses ~200MB total (2 workers + master process)
# Formula: For 512MB, safe maximum = 1 worker with threads, or 2 max
workers = int(os.environ.get('GUNICORN_WORKERS', '1'))
worker_class = 'sync'
threads = 2  # Added: Use 2 threads per worker for concurrency
worker_connections = 100  # Reduced from 1000 (memory concern)
timeout = 60  # Reduced from 120 (prevent hung requests holding memory)
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