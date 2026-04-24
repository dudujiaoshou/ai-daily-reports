#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import json
import requests
from datetime import datetime

# Force UTF-8 output
if sys.version_info[0] >= 3:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api_key = os.environ.get('NVIDIA_API_KEY')
github_output = os.environ.get('GITHUB_OUTPUT', '')

if not api_key:
    print('NVIDIA_API_KEY not found')
    now = datetime.now()
    is_pm = now.hour >= 12
    suffix = '_PM' if is_pm else '_AM'
    filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# Error: NVIDIA_API_KEY not configured')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
    exit(1)

url = 'https://integrate.api.nvidia.com/v1/chat/completions'

now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y') + ' year ' + now.strftime('%m') + ' month ' + now.strftime('%d') + ' day'
report_type = 'PM' if is_pm else 'AM'

system_prompt = """You are a professional AI industry analyst. Generate a daily AI industry report.

Report format:
# AI Daily Report DATE TIME

## Global AI/Tech/Investment News
- News title: Brief analysis

## China AI Startup Dynamics
- Company: [Amount] | [Investor] | [Field] | [Analysis]

## Shanghai AI Events
- Event: [Date] | [Venue]

Total: 500-800 words."""

user_prompt = 'Please generate AI daily report for today.'

payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ],
    'max_tokens': 2000,
    'temperature': 0.7
}

# Use ONLY ASCII headers to avoid latin-1 encoding error
headers = {
    'Authorization': 'Bearer ' + api_key,
    'Content-Type': 'application/json'
}

try:
    # Use json=payload which handles encoding properly
    print('Calling NVIDIA API...')
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        suffix = '_PM' if is_pm else '_AM'
        filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('Report generated: ' + filename)
        print('Length: ' + str(len(content)))
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
    else:
        print('API Error: ' + str(response.status_code))
        print('Response: ' + response.text[:500])
        
        suffix = '_PM' if is_pm else '_AM'
        filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('# Error\n\nStatus: ' + str(response.status_code) + '\n\n' + response.text)
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
                
except requests.exceptions.Timeout:
    print('Request timeout')
    suffix = '_PM' if is_pm else '_AM'
    filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# Timeout\n\nThe request timed out.')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
            
except Exception as e:
    import traceback
    print('Error: ' + str(e))
    traceback.print_exc()
    suffix = '_PM' if is_pm else '_AM'
    filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# Error\n\n' + str(e) + '\n\n' + traceback.format_exc())
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
