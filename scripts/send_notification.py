#!/usr/bin/env python3
import os, requests
from datetime import datetime
import glob

# 直接使用新的 SendKey（方糖服务号）
sckey = 'SCT341644TZiX7nw1wWX7AqagsvbJymoa2'
now = datetime.now()
is_pm = now.hour >= 12
report_type = 'Evening' if is_pm else 'Morning'

files = sorted(glob.glob('AI-Report_*.md'))
if files:
    latest = files[-1]
    with open(latest, 'r', encoding='utf-8') as f:
        content = f.read()
else:
    content = '[No report generated]'

summary = content[:500] + '...' if len(content) > 500 else content

url = 'https://sctapi.ftqq.com/' + sckey + '.send'
data = {
    'title': 'AI Daily Report ' + report_type + ' | ' + now.strftime('%m/%d %H:%M'),
    'desp': summary
}

try:
    resp = requests.post(url, data=data)
    print('Notification sent:', resp.text)
except Exception as e:
    print('Notification failed:', str(e))
