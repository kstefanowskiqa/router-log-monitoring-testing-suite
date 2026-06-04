import socket
import os
import json
import matplotlib.pyplot as plt
import glob
import traceback
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ========================
# CONFIGURATION
# ========================

UDP_IP = "0.0.0.0"  # Listening computer IP (change as needed)
UDP_PORT = 0000           # UDP port for syslog (change as needed)

LOG_DIR = "logs"
HISTORY_DIR = "history"
CHART_DIR = "charts"
DAILY_STATS_FILE = "daily_stats.json"
GLOBAL_STATS_FILE = "global_stats.json"
SYSTEM_LOG = "system_log.txt"
CONFIG_FILE = "config.json"

BURST_THRESHOLD_5SEC = 300
BURST_ALERT_COOLDOWN = 10

HEARTBEAT_INTERVAL = 60  # seconds for heartbeat log

# Forced day offset (0 = no offset)
forced_day_offset = 0
offset_lock = threading.Lock()

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

# ========================
# AUXILIARY FUNCTIONS
# ========================

def get_now():
    """
    Returns current datetime adjusted by forced_day_offset (days).
    """
    with offset_lock:
        offset = forced_day_offset
    return datetime.now() + timedelta(days=offset)

def get_today():
    """
    Returns today's date (YYYY-MM-DD) using get_now().
    """
    return get_now().strftime("%Y-%m-%d")

def get_log_file():
    """
    Returns the path to today's log file.
    """
    return os.path.join(LOG_DIR, f"{get_today()}.log")

def load_json(filepath):
    """
    Loads JSON data from a file or returns {} if the file doesn't exist or is invalid.
    """
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_system_event(f"Failed to load JSON {filepath}: {e}")
    return {}

def save_json(filepath, data):
    """
    Saves data as JSON to a file, overwriting existing content.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        log_system_event(f"Failed to save JSON {filepath}: {e}")

def reset_system_log():
    """
    Rotates system log if too large and writes a header for a new session.
    """
    if os.path.exists(SYSTEM_LOG) and os.path.getsize(SYSTEM_LOG) > 5_000_000:
        os.rename(SYSTEM_LOG, SYSTEM_LOG + ".old")
    with open(SYSTEM_LOG, "a", encoding="utf-8") as f:
        f.write("=== NEW SESSION ===\n")
        f.write(f"Start: {get_now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

def log_system_event(message):
    """
    Appends a timestamped message to the system log file.
    """
    timestamp = get_now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SYSTEM_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def reset_daily_stats():
    """
    Returns a new daily statistics dictionary.
    """
    return {
        "date": get_today(),
        "start_timestamp": get_now().timestamp(),
        "total_entries": 0,
        "blocked_attempts": 0,
        "per_hour": defaultdict(int),
        "per_minute": defaultdict(int),
        "peak_hour": None,
        "peak_hour_count": 0
    }

def generate_daily_chart(daily_stats, final=True):
    """
    Generates a daily chart (entries per hour) and saves it (FINAL version).
    """
    date_str = daily_stats["date"]
    hours = sorted(daily_stats["per_hour"].keys())
    values = [daily_stats["per_hour"][h] for h in hours]
    if not hours:
        return
    plt.figure()
    plt.plot(hours, values, marker='o')
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = os.path.join(CHART_DIR, f"{date_str}_FINAL.png")
    try:
        plt.savefig(filename)
        log_system_event(f"Generated chart: {filename}")
    except Exception as e:
        log_system_event(f"Failed to save chart {filename}: {e}")
    plt.close()

def update_top10():
    """
    Updates 'top10_days.json' with top 10 days by total_entries.
    """
    files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
    results = []
    for file in files:
        data = load_json(file)
        if data:
            results.append({"date": data["date"], "total_entries": data["total_entries"]})
    top10 = sorted(results, key=lambda x: x["total_entries"], reverse=True)[:10]
    save_json("top10_days.json", top10)
    log_system_event("Updated top10_days.json.")

def detect_anomaly(new_day_total):
    """
    Logs an anomaly if today's total_entries > 3x the historical average.
    """
    files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
    totals = []
    for file in files:
        data = load_json(file)
        if data:
            totals.append(data["total_entries"])
    if len(totals) < 3:
        return
    avg = sum(totals) / len(totals)
    if new_day_total > avg * 3:
        anomalies = load_json("anomalies.json") or []
        anomalies.append({
            "date": get_today(),
            "value": new_day_total,
            "average": round(avg, 2)
        })
        save_json("anomalies.json", anomalies)
        log_system_event("A TRAFFIC ANOMALY WAS DETECTED.")

# ========================
# CONFIG HOT-RELOAD SETUP
# ========================

class ConfigHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global forced_day_offset
        if not event.src_path.endswith(CONFIG_FILE):
            return
        # Debounce rapid events (~1 second)
        now_ts = time.time()
        if hasattr(self, 'last_reload') and (now_ts - self.last_reload) < 1:
            return
        self.last_reload = now_ts
        # Reload config
        config = load_json(CONFIG_FILE)
        if "forced_day_offset" in config:
            with offset_lock:
                forced_day_offset = config["forced_day_offset"]
            log_system_event(f"Reload config: forced_day_offset={forced_day_offset}")

# Start watchdog observer for config changes
try:
    observer = Observer()
    observer.schedule(ConfigHandler(), path=".", recursive=False)
    observer.start()
except Exception:
    log_system_event("Failed to start config observer.")

# Initial load of config (if exists)
config = load_json(CONFIG_FILE)
if "forced_day_offset" in config:
    with offset_lock:
        forced_day_offset = config["forced_day_offset"]
    log_system_event(f"Initial forced_day_offset={forced_day_offset}")
else:
    log_system_event("No config or forced_day_offset not set; using default offset 0.")

# ========================
# MAIN APPLICATION LOOP
# ========================

start_time = time.time()
process_id = os.getpid()
processed_packets = 0
last_heartbeat = time.time()
last_burst_alert = 0

reset_system_log()
log_system_event("=== SCRIPT START ===")
log_system_event(f"PID: {process_id}")
log_system_event(f"Listening on UDP {UDP_IP}:{UDP_PORT}")

# Set up UDP socket with timeout for non-blocking receive
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(1.0)  # 1 second timeout

daily_stats = reset_daily_stats()
global_stats = load_json(GLOBAL_STATS_FILE)
if not global_stats:
    global_stats = {"total_entries": 0, "weekly": {}, "monthly": {}, "yearly": {}}

burst_window = deque()

while True:
    try:
        now_ts = time.time()
        now = get_now()

        # Heartbeat logging
        if now_ts - last_heartbeat >= HEARTBEAT_INTERVAL:
            uptime_minutes = round((now_ts - start_time) / 60, 2)
            log_system_event(f"Heartbeat | uptime: {uptime_minutes} min | packets: {processed_packets}")
            last_heartbeat = now_ts

        # Day rollover check
        if get_today() != daily_stats["date"]:
            log_system_event("Change of day - archiving.")
            archived = {
                **daily_stats,
                "per_hour": dict(daily_stats["per_hour"]),
                "per_minute": dict(daily_stats["per_minute"])
            }
            archive_file = os.path.join(HISTORY_DIR, f"{daily_stats['date']}.json")
            save_json(archive_file, archived)
            generate_daily_chart(daily_stats, final=True)
            update_top10()
            detect_anomaly(archived["total_entries"])
            daily_stats = reset_daily_stats()
            burst_window.clear()

        # Receive UDP packet (non-blocking with timeout)
        try:
            data, addr = sock.recvfrom(1024)
            processed_packets += 1
        except socket.timeout:
            data = None

        if data:
            # Burst detection within 5s window
            burst_window.append(now_ts)
            while burst_window and (now_ts - burst_window[0] > 5):
                burst_window.popleft()
            if len(burst_window) > BURST_THRESHOLD_5SEC:
                if now_ts - last_burst_alert >= BURST_ALERT_COOLDOWN:
                    log_system_event(f"ALERT: >{BURST_THRESHOLD_5SEC} logs in 5s")
                    last_burst_alert = now_ts

            # Append log entry to today's file
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = data.decode(errors="ignore").strip()
            log_entry_full = f"{addr[0]}:{addr[1]} -> {log_entry}"
            try:
                with open(get_log_file(), "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {log_entry_full}\n")
            except Exception:
                log_system_event(f"Failed to write to log file: {get_log_file()}")

            print(f"[{timestamp}] {log_entry_full}")

            # Update stats
            hour_key = now.strftime("%Y-%m-%d %H")
            minute_key = now.strftime("%Y-%m-%d %H:%M")
            week_key = f"{now.isocalendar().year}-W{now.isocalendar().week}"
            month_key = now.strftime("%Y-%m")
            year_key = now.strftime("%Y")

            daily_stats["total_entries"] += 1
            daily_stats["per_hour"][hour_key] += 1
            daily_stats["per_minute"][minute_key] += 1
            if daily_stats["per_hour"][hour_key] > daily_stats["peak_hour_count"]:
                daily_stats["peak_hour_count"] = daily_stats["per_hour"][hour_key]
                daily_stats["peak_hour"] = hour_key
            if any(x in log_entry.lower() for x in ["blocked", "denied", "drop"]):
                daily_stats["blocked_attempts"] += 1

            global_stats["total_entries"] += 1
            global_stats["weekly"][week_key] = global_stats["weekly"].get(week_key, 0) + 1
            global_stats["monthly"][month_key] = global_stats["monthly"].get(month_key, 0) + 1
            global_stats["yearly"][year_key] = global_stats["yearly"].get(year_key, 0) + 1

            elapsed = now.timestamp() - daily_stats["start_timestamp"]
            daily_stats["avg_per_minute"] = round(
                daily_stats["total_entries"] / (elapsed/60) if elapsed > 0 else 0, 2
            )

            save_json(DAILY_STATS_FILE, {
                **daily_stats,
                "per_hour": dict(daily_stats["per_hour"]),
                "per_minute": dict(daily_stats["per_minute"])
            })
            save_json(GLOBAL_STATS_FILE, global_stats)

    except Exception:
        error_info = traceback.format_exc()
        log_system_event("!!! MAIN LOOP ERROR !!!")
        log_system_event(error_info)
        continue
