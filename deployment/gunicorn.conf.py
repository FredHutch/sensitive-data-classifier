bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 300
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
