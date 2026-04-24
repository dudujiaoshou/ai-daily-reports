#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import subprocess
import json
from datetime import datetime

# Force UTF-8
if sys.version_info[0] >= 3:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

api_key = os.environ.get('NVIDIA_API_KEY')
github_output = os.environ.get('GITHUB_OUTPUT', '')
sckey = os.environ.get('SERVERCHAN_SCKEY', '')

if not api_key:
    print('NVIDIA_API_KEY not found')
    exit(1)

now = datetime.now()
is_pm = now.hour >= 12
suffix = '_PM' if is_pm else '_AM'
filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'

# Build payload
payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'user', 'content': 'Generate a short AI industry news report in Chinese. Include: 1) Global AI tech news, 2) China AI startup funding, 3) Shanghai AI events. Format as Markdown.'}
    ],
    'max_tokens': 2000,
    'temperature': 0.7
}

json_data = json.dumps(payload)

# Write JSON to temp file
with open('/tmp/request.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

# Use curl
cmd = [
    'curl', '-s', '-w', '\\n%{http_code}', '-X', 'POST',
    'https://integrate.api.nvidia.com/v1/chat/completions',
    '-H', 'Authorization: Bearer ' + api_key,
    '-H', 'Content-Type: application/json',
    '-d', '@/tmp/request.json',
    '--max-time', '120'
]

print('Calling NVIDIA API with curl...')
try:
    result = subprocess.run(cmd, capture_output=True, timeout=130)
    
    # Decode outputs
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
    
    print('Curl return code:', result.returncode)
    
    if stderr:
        print('Curl stderr:', stderr[:500])
    
    # Parse response - last line is HTTP status
    lines = stdout.strip().split('\n')
    if len(lines) >= 2:
        http_code = lines[-1]
        response_body = '\n'.join(lines[:-1])
        print('HTTP code:', http_code)
    else:
        http_code = ''
        response_body = stdout
    
    print('Response body length:', len(response_body))
    print('Response body preview:', response_body[:200] if response_body else '(empty)')
    
    if not response_body:
        print('ERROR: Empty response from API')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('# Error\n\nEmpty response from NVIDIA API\nStderr: ' + stderr)
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
        exit(1)
    
    # Parse JSON response
    try:
        response = json.loads(response_body)
    except json.JSONDecodeError as e:
        print('JSON parse error:', str(e))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('# Error\n\nJSON parse error: ' + str(e) + '\n\nResponse: ' + response_body[:1000])
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
        exit(1)
    
    if 'choices' in response:
        content = response['choices'][0]['message']['content']
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Report generated: ' + filename)
        print('Length:', len(content))
        
        # Send notification
        if sckey:
            import requests as req
            report_type = 'Evening' if is_pm else 'Morning'
            summary = content[:500] + '...' if len(content) > 500 else content
            notif_url = 'https://sctapi.ftqq.com/' + sckey + '.send'
            notif_data = {
                'title': 'AI Daily Report ' + report_type + ' | ' + now.strftime('%m/%d %H:%M'),
                'desp': '**GitHub**: https://github.com/dudujiaoshou/ai-daily-reports\n\n---\n' + summary
            }
            try:
                notif_resp = req.post(notif_url, data=notif_data, timeout=10)
                print('Notification:', notif_resp.text[:100])
            except Exception as e:
                print('Notification error:', str(e))
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
    else:
        print('API Error:', json.dumps(response, indent=2)[:500])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('# Error\n\nAPI Error: ' + json.dumps(response, indent=2))
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
