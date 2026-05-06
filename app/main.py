import socket
import os
import json
import matplotlib.pyplot as plt
import glob
import traceback
import time
from datetime import datetime
from collections import defaultdict, deque

# ========================
# KONFIGURACJA
# ========================

UDP_IP = "0.0.0.0" # Komputer IP
UDP_PORT = XXXX # UDP Set on the router

LOG_DIR = "logs"
HISTORY_DIR = "history"
CHART_DIR = "charts"
DAILY_STATS_FILE = "daily_stats.json"
GLOBAL_STATS_FILE = "global_stats.json"
SYSTEM_LOG = "system_log.txt"

BURST_THRESHOLD_5SEC = 300

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

last_hourly_update = None

# ========================
# POMOCNICZE
# ========================

def log_system_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SYSTEM_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def get_log_file():
    return os.path.join(LOG_DIR, f"{get_today()}.log")

def reset_daily():
    return {
        "date": get_today(),
        "start_timestamp": datetime.now().timestamp(),
        "total_entries": 0,
        "blocked_attempts": 0,
        "per_hour": defaultdict(int),
        "per_minute": defaultdict(int),
        "peak_hour": None,
        "peak_hour_count": 0
    }

def generate_daily_chart(daily_stats, final=False):
    date_str = daily_stats["date"]
    hours = sorted(daily_stats["per_hour"].keys())
    values = [daily_stats["per_hour"][h] for h in hours]

    if not hours:
        return

    plt.figure()
    plt.plot(hours, values)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if final:
        filename = os.path.join(CHART_DIR, f"{date_str}_FINAL.png")
    else:
        filename = os.path.join(CHART_DIR, f"{date_str}_LIVE.png")

    plt.savefig(filename)
    plt.close()

    log_system_event(f"Wygenerowano wykres: {filename}")

def update_top10():
    files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
    results = []

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            results.append({
                "date": data["date"],
                "total_entries": data["total_entries"]
            })

    top10 = sorted(results, key=lambda x: x["total_entries"], reverse=True)[:10]
    save_json("top10_days.json", top10)
    log_system_event("Zaktualizowano TOP10 dni.")

def detect_anomaly(new_day_total):
    files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
    totals = []

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
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
        log_system_event("WYKRYTO ANOMALIĘ RUCHU.")

def reset_system_log():
    with open(SYSTEM_LOG, "w", encoding="utf-8") as f:
        f.write("=== NOWA SESJA ===\n")
        f.write(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

# ========================
# START APLIKACJI (bez main, bez supervisor)
# ========================

start_time = time.time()
process_id = os.getpid()
processed_packets = 0
last_heartbeat = time.time()

reset_system_log()
log_system_event("=== START SKRYPTU ===")
log_system_event(f"PID procesu: {process_id}")
log_system_event(f"Nasłuchiwanie na {UDP_IP}:{UDP_PORT}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Nasłuchiwanie logów...")

daily_stats = reset_daily()
global_stats = load_json(GLOBAL_STATS_FILE)

if not global_stats:
    global_stats = {
        "total_entries": 0,
        "weekly": {},
        "monthly": {},
        "yearly": {}
    }

burst_window = deque()

while True:
    try:
        data, addr = sock.recvfrom(4096)
        processed_packets += 1
        now_ts = time.time()

        burst_window.append(now_ts)

        while burst_window and now_ts - burst_window[0] > 5:
            burst_window.popleft()

        if len(burst_window) > BURST_THRESHOLD_5SEC:
            log_system_event(f"ALERT: BURST > {BURST_THRESHOLD_5SEC} logów / 5s")
        
        log_entry = data.decode(errors="ignore").strip()
        now = datetime.now()

        # ===== Heartbeat co 60 sek =====
        if time.time() - last_heartbeat >= 60:
            uptime = round((time.time() - start_time) / 60, 2)
            log_system_event(f"Heartbeat | uptime: {uptime} min | pakiety: {processed_packets}")
            last_heartbeat = time.time()

        # ===== Aktualizacja wykresu co godzinę =====
        current_hour = now.strftime("%Y-%m-%d %H")
        if last_hourly_update != current_hour:
            generate_daily_chart(daily_stats)
            last_hourly_update = current_hour

        # ===== Zmiana dnia =====
        if daily_stats["date"] != get_today():
            log_system_event("Zmiana dnia - archiwizacja.")

            archived_data = {
                **daily_stats,
                "per_hour": dict(daily_stats["per_hour"]),
                "per_minute": dict(daily_stats["per_minute"])
            }

            archive_file = os.path.join(HISTORY_DIR, f"{daily_stats['date']}.json")
            save_json(archive_file, archived_data)

            generate_daily_chart(daily_stats, final=True)
            update_top10()
            detect_anomaly(archived_data["total_entries"])

            daily_stats = reset_daily()

        # ===== Zapis logu =====
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(get_log_file(), "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {log_entry}\n")

        print(f"[{timestamp}] {log_entry}")

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

        elapsed_seconds = now.timestamp() - daily_stats["start_timestamp"]
        elapsed_minutes = elapsed_seconds / 60
        avg_per_min = daily_stats["total_entries"] / elapsed_minutes if elapsed_minutes > 0 else 0
        daily_stats["avg_per_minute"] = round(avg_per_min, 2)

        save_json(DAILY_STATS_FILE, {
            **daily_stats,
            "per_hour": dict(daily_stats["per_hour"]),
            "per_minute": dict(daily_stats["per_minute"])
        })

        save_json(GLOBAL_STATS_FILE, global_stats)

    except Exception:
        error_info = traceback.format_exc()
        log_system_event("!!! BŁĄD W PĘTLI GŁÓWNEJ !!!")
        log_system_event(error_info)
