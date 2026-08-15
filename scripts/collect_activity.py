import psutil
import datetime
import json
import os
from collections import Counter

def collect_activity(target_date):
    date_str = target_date.strftime("%Y-%m-%d")

    # CPU and memory
    cpu_percent = psutil.cpu_percent(interval=2)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Top processes by CPU usage
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort and take top 5
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
    top_mem = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]

    # Count process names (anonymized usage summary)
    name_counts = Counter([p['name'] for p in processes if p['name']])
    common_apps = name_counts.most_common(5)

    activity = {
        "date": date_str,
        "cpu_percent": cpu_percent,
        "memory_percent": mem.percent,
        "disk_usage_percent": disk.percent,
        "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        "process_count": len(processes),
        "top_cpu_processes": top_cpu,
        "top_memory_processes": top_mem,
        "most_common_apps": common_apps
    }

    os.makedirs("logs", exist_ok=True)

    # Rotate logs: append to the current log file until it reaches MAX_SIZE,
    # then start a new file. Use newline-delimited JSON entries.
    MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    # Find existing rotated files
    files = [f for f in os.listdir("logs") if f.startswith("activity-log-") and f.endswith('.json')]
    def extract_index(name):
        try:
            return int(name.rsplit('-', 1)[-1].rsplit('.', 1)[0])
        except Exception:
            return 0

    if not files:
        idx = 1
        current_filename = os.path.join("logs", f"activity-log-{idx}.json")
    else:
        files_sorted = sorted(files, key=extract_index)
        latest = files_sorted[-1]
        latest_path = os.path.join("logs", latest)
        latest_size = os.path.getsize(latest_path)
        latest_idx = extract_index(latest)
        if latest_size >= MAX_SIZE:
            idx = latest_idx + 1
            current_filename = os.path.join("logs", f"activity-log-{idx}.json")
        else:
            current_filename = latest_path

    # Append newline-delimited JSON entry
    with open(current_filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(activity, ensure_ascii=False))
        f.write("\n")

    print(f"Activity log appended to {current_filename}")

if __name__ == "__main__":
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    collect_activity(yesterday)
