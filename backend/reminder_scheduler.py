# backend/reminder_scheduler.py
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()
DEFAULT_USER = os.getenv("DEFAULT_USER", "junior")
API_BASE = os.getenv("API_BASE", "http://localhost:8000")  # if calling endpoints

scheduler = BackgroundScheduler()

def send_reminder_via_api(user: str, message: str):
    # This will call your own /send_message endpoint to create a message and trigger agent
    try:
        requests.post(f"{API_BASE}/send_message", json={"user": user, "text": message}, timeout=5)
    except Exception as e:
        print("Failed to call /send_message:", e)

def schedule_daily_reminder(hour:int=13, minute:int=00, user: str = DEFAULT_USER):
    # example: schedule every day at hour:minute
    scheduler.add_job(lambda: send_reminder_via_api(user, "It's time to practice English! 🎯"),
                      "cron", hour=hour, minute=minute, id="daily_practice")
    scheduler.start()
