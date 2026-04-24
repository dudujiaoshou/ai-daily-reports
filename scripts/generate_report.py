#!/usr/bin/env python3
import os
import requests
from datetime import datetime

api_key = os.environ.get('NVIDIA_API_KEY')
github_output = os.environ.get('GITHUB_OUTPUT', '')

if not api_key:
    filename = f"AI-Report_{datetime.now().strftime('%Y-%m-%d')}_ERROR.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# Error: NVIDIA_API_KEY not configured\n')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f'filename={filename}\n')
    exit(1)

url = 'https://integrate.api.nvidia.com/v1/chat/completions'

now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y年%m月%d日')
report_type = '下午' if is_pm else '上午'
suffix = '_PM' if is_pm else '_AM'
filename = f"AI-Report_{now.strftime('%Y-%m-%d')}{suffix}.md"

system_prompt = (
    "You are a professional AI industry analyst. Generate a daily AI industry report in Simplified Chinese. "
    "Date: " + date_str + ". "
    "Structure: 1) Global AI/Tech/Investment news (5-8 items with analysis), "
    "2) Chinese AI startup data (3-5 companies with funding, investors, sector), "
    "3) Shanghai AI events (3-5 upcoming events with date, venue, organizer, registration). "
    "Format: Markdown. Length: 800-1500 Chinese characters. Be specific with data and provide your own insights."
)

user_prompt = f"Generate a professional AI industry report for {date_str}, covering global AI news, Chinese AI startup dynamics, and Shanghai AI events. Output in Simplified Chinese."

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

        print('Report generated: ' + filename)

        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write(f'filename={filename}\n')
    else:
        print('API Error: ' + str(response.status_code))
        print('Response: ' + response.text)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'# AI Daily Report - Error\n\n**Date**: {date_str} {report_type}\n\n## Error\n\n**Status**: {response.status_code}\n\n**Details**:\n{response.text}\n')

        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write(f'filename={filename}\n')

except Exception as e:
    print('Error: ' + str(e))
    import traceback
    traceback.print_exc()

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'# AI Daily Report - Error\n\n**Date**: {date_str} {report_type}\n\n## Error\n\n{str(e)}\n')

    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f'filename={filename}\n')
