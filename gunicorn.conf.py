import os

bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
workers = int(os.getenv('GUNICORN_WORKERS', '4'))
worker_class = 'uvicorn.workers.UvicornWorker'
timeout = int(os.getenv('GUNICORN_TIMEOUT', '120'))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '5'))
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
