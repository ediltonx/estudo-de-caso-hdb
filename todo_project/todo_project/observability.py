from prometheus_client import Counter


http_requests_total = Counter(
    'todo_app_http_requests_total',
    'Total HTTP requests handled by the application',
    ['endpoint', 'method', 'status']
)

user_actions_total = Counter(
    'todo_app_user_actions_total',
    'User actions captured by the application',
    ['action', 'result']
)


def record_http_request(endpoint: str, method: str, status: int) -> None:
    http_requests_total.labels(endpoint=endpoint, method=method, status=str(status)).inc()


def record_user_action(action: str, result: str) -> None:
    user_actions_total.labels(action=action, result=result).inc()