from prometheus_client import Counter, Histogram

# Metric to count the number of prediction requests
prediction_requests = Counter(
    'prediction_requests_total', 
    'Total number of prediction requests',
)

# Metric to count prediction errors
prediction_errors = Counter(
    'prediction_errors_total', 
    'Total number of prediction errors',
)

# Histogram to measure the duration of a prediction request
prediction_duration = Histogram(
    'prediction_latencyd_seconds', 
    'Time spent for prediction',
)