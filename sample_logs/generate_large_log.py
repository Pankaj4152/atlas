"""
Generator for realistic, high-volume production server log datasets.
Simulates a multi-tier microservices application:
- API Gateway
- Auth Service
- Payment Service
- Database Cluster
- Cache / Redis
- Background Worker Pool
Includes normal operation, memory leaks, brute-force auth attempts,
database connection exhaustion cascades, and deadlocks across 5,000+ log lines.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_production_server_logs(
    output_path: str = "sample_logs/production_server_large.log",
    total_lines: int = 5000,
    start_time: datetime = None
):
    if start_time is None:
        start_time = datetime(2026, 11, 18, 9, 0, 0)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    users = [f"usr_{random.randint(1000, 9999)}" for _ in range(50)]
    ips = [f"192.168.1.{i}" for i in range(10, 80)] + ["10.0.4.15", "172.16.0.44", "203.0.113.88"]
    services = ["api-gateway", "auth-service", "order-service", "payment-service", "postgres-db", "redis-cache", "worker-pool"]
    endpoints = [
        ("GET", "/api/v1/products"),
        ("GET", "/api/v1/user/profile"),
        ("POST", "/api/v1/cart/items"),
        ("POST", "/api/v1/checkout"),
        ("GET", "/api/v1/health"),
        ("POST", "/api/v1/auth/login"),
    ]

    current_ts = start_time
    lines = []

    print(f"Generating {total_lines} realistic production log lines...")

    # We will simulate 60 minutes of server operation
    for i in range(total_lines):
        # Progress time gradually (average 0.72 seconds between logs = ~5,000 logs in 1 hour)
        current_ts += timedelta(milliseconds=random.randint(400, 1100))
        minute_offset = int((current_ts - start_time).total_seconds() / 60)

        # Inject realistic failure scenarios at specific minute intervals:
        # Scenario 1: Minute 12-14 -> Brute-force auth attack from external IP
        # Scenario 2: Minute 27-29 -> Memory pressure warning and GC pause
        # Scenario 3: Minute 42-45 -> Major Database Connection Pool Exhaustion & Worker Thread Crash cascade

        if 12 <= minute_offset <= 14 and random.random() < 0.65:
            # Brute-force auth spike
            attacker_ip = "203.0.113.88"
            svc = "auth-service"
            level = "ERROR" if random.random() < 0.85 else "WARN"
            target_usr = random.choice(["admin", "root", "usr_1001", "usr_9999"])
            msg = f"Failed authentication attempt for user '{target_usr}' from {attacker_ip}: invalid credentials (attempt #{random.randint(10, 120)})"

        elif 27 <= minute_offset <= 29 and random.random() < 0.50:
            # Memory leak / resource strain
            svc = "worker-pool"
            if random.random() < 0.4:
                level = "WARN"
                mem = random.randint(84, 94)
                msg = f"Heap memory usage critical: {mem}% utilized. JVM invoking Full GC pause ({random.randint(1200, 3400)}ms)"
            else:
                level = "INFO"
                msg = f"Background queue processing delayed: worker thread pool saturated (queue_depth={random.randint(400, 950)})"

        elif 42 <= minute_offset <= 45 and random.random() < 0.70:
            # Cascading database exhaustion and service crash
            dice = random.random()
            if dice < 0.25:
                svc = "postgres-db"
                level = "CRITICAL" if random.random() < 0.5 else "ERROR"
                msg = f"Connection pool exhausted: active=100/100, pending_queue={random.randint(80, 240)}, timeout exceeded (5000ms)"
            elif dice < 0.55:
                svc = "order-service"
                level = "ERROR"
                msg = f"Database query failed: could not acquire connection from pool for transaction tx_{random.randint(10000, 99999)}"
            elif dice < 0.75:
                svc = "api-gateway"
                level = "ERROR"
                msg = f"Upstream dependency order-service timed out: HTTP 504 Gateway Timeout after 5002ms"
            else:
                svc = "worker-pool"
                level = "CRITICAL"
                msg = f"Fatal worker thread crash: unhandled ConnectionPoolExhaustedException in ConsumerThread-{random.randint(1, 8)}"

        else:
            # Normal server operations
            dice = random.random()
            svc = random.choice(services)
            ip = random.choice(ips)
            usr = random.choice(users)

            if dice < 0.85:
                level = "INFO"
                method, path = random.choice(endpoints)
                latency = random.randint(4, 45)
                if svc == "api-gateway":
                    msg = f"Handled {method} {path} for {usr} from {ip} status=200 latency={latency}ms"
                elif svc == "postgres-db":
                    msg = f"Executed statement: SELECT * FROM {random.choice(['users', 'orders', 'products'])} in {latency}ms"
                elif svc == "redis-cache":
                    msg = f"Cache hit key=session:{usr} (ttl={random.randint(300, 3600)}s)"
                elif svc == "auth-service":
                    msg = f"User session refreshed successfully for {usr}"
                else:
                    msg = f"Heartbeat check passed: service={svc} healthy=true active_tasks={random.randint(1, 15)}"
            elif dice < 0.95:
                level = "WARN"
                latency = random.randint(800, 1600)
                msg = f"Slow query execution: SELECT * FROM analytics took {latency}ms on host 10.0.0.5"
            else:
                level = "ERROR"
                msg = f"Client aborted request: ECONNRESET on connection {ip}:443"

        ts_str = current_ts.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{ts_str} {level} [{svc}] {msg}"
        lines.append(log_line)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    size_kb = round(out_file.stat().st_size / 1024, 2)
    print(f"Generated {len(lines)} lines -> {out_file} ({size_kb} KB)")
    return str(out_file)


if __name__ == "__main__":
    generate_production_server_logs()
