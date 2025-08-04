# Configuración de Gunicorn para producción
import multiprocessing
import os

# Configuración de workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"  # Worker estándar para Flask
max_requests = 1000
max_requests_jitter = 100

# Timeouts estándar
timeout = 30
keepalive = 2
graceful_timeout = 30

# Configuración de red
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configuración de procesos
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None

# Configuración de memoria
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm"

# Configuración para Render
forwarded_allow_ips = "*"
proxy_allow_ips = "*"

# Configuración SSL/HTTPS
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
