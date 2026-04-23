#!/usr/bin/env python3
import os
import requests
from datetime import datetime
import glob

sckey = os.environ.get('SERVERCHAN_SCKEY')
now = datetime.now()
is_pm = now.hour >= 12
report_type = "Evening" if is_pm else "Morning"

# Find the latest report file
files = glob.glob("AI鏃ユ姤_*.md")
if files:
    latest = max(files)
    with open(latest, 'r', encoding='utf-8') as f:
        content = f.read()
else:
    content = "[No report generated]"

summary = content[:500] + "..." if len(content) > 500 else content

url = "https://sc.ftqq.com/" + sckey + ".send"
data = {
    "text": "AI Daily Report " + report_type + " | " + now.strftime('%m/%d %H:%M'),
    "desp": "**GitHub**: https://github.com/dudujiaoshou/ai-daily-reports\n\n---\n" + summary
}

try:
    resp = requests.post(url, data=data)
    print("Notification sent: " + resp.text)
except Exception as e:
    print("Notification failed: " + str(e))
