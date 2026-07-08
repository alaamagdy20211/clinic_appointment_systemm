from prometheus_client import Counter
from prometheus_client import Histogram

appointments_status_changes_total = Counter(
    "appointments_status_changes_total",
    "Total number of appointments status changes" ,
    ["specialty","status"]
)


appointments_created_total = Counter(
    "appointments_created_total",
    "Total number of appointments created" ,
    ["specialty"]
)


appointment_creation_duration_seconds = Histogram(
    "appointment_creation_duration_seconds",
    "Time spent creating appointments"
)