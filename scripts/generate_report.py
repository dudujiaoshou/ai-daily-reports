#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import subprocess
from datetime import datetime

# Force UTF-8
if sys.version_info[0] >= 3:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api_key = os.environ.get('NVIDIA_API_KEY')
github_output = os.environ.get('GITHUB_OUTPUT', '')

if not api_key:
    print('NVIDIA_API_KEY not found')
    exit(1)

now = datetime.now()
is_pm = now.hour >= 12
suffix = '_PM' if is_pm else '_AM'
filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'

# Build the API request using curl (handles encoding better)
import json

payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'user', 'content': 'Generate a short AI industry news report in Chinese. Include: 1) Global AI tech news, 2) China AI startup funding, 3) Shanghai AI events. Format as Markdown.'}
    ],
    'max_tokens': 2000,
    'temperature': 0.7
}

json_data = json.dumps(payload)

# Write JSON to temp file to avoid shell encoding issues
with open('/tmp/request.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

# Use curl with explicit headers
cmd = [
    'curl', '-s', '-X', 'POST',
    'https://integrate.api.nvidia.com/v1/chat/completions',
    '-H', 'Authorization: Bearer ' + api_key,
    '-H', 'Content-Type: application/json',
    '-d', '@/tmp/request.json',
    '--max-time', '120'
]

print('Calling NVIDIA API with curl...')
try:
    result = subprocess.run(cmd, capture_output=True, timeout=130)
    response_text = result.stdout.decode('utf-8', errors='replace')
    
    if result.returncode != 0:
        stderr_text = result.stderr.decode('utf-8', errors='replace')
        print('Curl error:', stderr_text)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('# Error\n\nCurl error: ' + stderr_text)
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
        exit(1)
    
    # Parse response
    response = json.loads(response_text)
    
    if 'choices' in response:
        content = response['choices'][0]['message']['content']
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Report generated: ' + filename)
        print('Length:', len(content))
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
    else:
        print('API Error:', response)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('# Error\n\n' + json.dumps(response, indent=2))
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
                
except subprocess.TimeoutExpired:
    print('Request timeout')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# Timeout\n\nThe request timed out.')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
            
except Exception as e:
    import traceback
    print('Error:', str(e))
    traceback.print_exc()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# Error\n\n' + str(e) + '\n\n' + traceback.format_exc())
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
