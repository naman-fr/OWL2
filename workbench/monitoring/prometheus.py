from prometheus_client import Counter, Histogram

# Metrics
TASK_REQUEST_COUNT = Counter(
    'owl_task_requests_total',
    'Total number of task execution requests',
    ['model_role', 'status']
)

TASK_LATENCY = Histogram(
    'owl_task_latency_seconds',
    'Time spent processing a task',
    ['model_role']
)
