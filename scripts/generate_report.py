#!/usr/bin/env python3
import os
import requests
from datetime import datetime

api_key = os.environ.get('NVIDIA_API_KEY')
github_output = os.environ.get('GITHUB_OUTPUT', '')

if not api_key:
    filename = 'AI-Report_ERROR.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('Error: NVIDIA_API_KEY not configured')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
    exit(1)

url = 'https://integrate.api.nvidia.com/v1/chat/completions'

now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y-%m-%d')
report_type = 'PM' if is_pm else 'AM'
suffix = '_PM' if is_pm else '_AM'
filename = 'AI-Report_' + date_str + suffix + '.md'

system_prompt = (
    'You are a professional AI industry analyst. Generate a comprehensive daily AI industry report. '
    'Date: ' + date_str + '. '
    'Structure: Section 1) Global AI/Tech/Investment news (5-8 items with brief analysis), '
    'Section 2) Chinese AI startup data (3-5 companies with funding amount, investors, sector, analysis), '
    'Section 3) Shanghai AI events (3-5 upcoming events with date, venue, organizer, registration link if available). '
    'Format: Markdown with proper headings. Length: 800-1500 Chinese characters. '
    'Be specific with data, names, and figures. Provide your own insights and highlight opportunities and risks.'
)

user_prompt = (
    'Generate a professional AI industry daily report for ' + date_str + '. '
    'Cover: (1) Global AI/Tech/Investment news from the past 24 hours, '
    '(2) Chinese AI startup funding and developments, '
    '(3) Shanghai AI-related events and meetups. '
    'Output in Simplified Chinese (Simplified Chinese, not Traditional). Use Markdown format.'
)

payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ],
    'max_tokens': 4000,
    'temperature': 0.7
}

headers = {
    'Authorization': 'Bearer ' + api_key,
    'Content-Type': 'application/json'
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        print('SUCCESS: Report generated - ' + filename)

        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
    else:
        err_msg = 'API Error ' + str(response.status_code) + ': ' + response.text[:500]
        print(err_msg)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('AI Daily Report - Error\n\nStatus: ' + str(response.status_code) + '\n\n' + response.text)

        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')

except Exception as e:
    print('Error: ' + str(e))
    import traceback
    traceback.print_exc()

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('AI Daily Report - Error\n\n' + str(e) + '\n')

    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
