#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, subprocess, tempfile
from datetime import datetime

api_key = os.environ.get('NVIDIA_API_KEY', '').strip()
if not api_key:
    print('ERROR: NVIDIA_API_KEY not set')
    sys.exit(1)

url = 'https://integrate.api.nvidia.com/v1/chat/completions'
now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y年%m月%d日')

system_prompt = "你是一位专业的AI行业分析师。请为当前日期生成一份综合的每日AI行业报告。报告必须包含三个板块，全部使用简体中文：1. 全球AI/Tech/投资新闻：5-8条过去24小时重要新闻，每条附1-2句分析 2. 中国AI创业公司动态：3-5家公司，包含融资金额、投资方、领域和分析 3. 上海AI相关活动：3-5个即将举办的活动，包含日期、场地、报名链接。内容要具体有数据，800-1500字。"

user_prompt = f'请为{date_str}生成AI行业日报，三大板块。'

payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ],
    'max_tokens': 4000,
    'temperature': 0.7
}

# Use curl to make the request (avoids Python HTTP client encoding issues)
# Write payload to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)
    tmp_file = f.name

try:
    print('Calling NVIDIA API with curl...')
    # Build curl command - use ASCII only for headers
    curl_cmd = [
        'curl', '-s', '-X', 'POST',
        url,
        '-H', 'Authorization: Bearer ' + api_key,
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/request.json',
        '-w', '\n%{http_code}',
        '-o', '/tmp/response.json'
    ]

    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', url,
         '-H', 'Authorization: Bearer ' + api_key,
         '-H', 'Content-Type: application/json',
         '-d', '@/tmp/request.json',
         '-w', '\n%{http_code}'],
        capture_output=True, timeout=130,
        env={**os.environ, 'HOME': '/tmp'}
    )

    # Write payload to /tmp for curl
    with open('/tmp/request.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)

    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', url,
         '-H', 'Authorization: Bearer ' + api_key,
         '-H', 'Content-Type: application/json',
         '-d', '@/tmp/request.json',
         '-w', '\n%{http_code}'],
        capture_output=True, timeout=130,
        cwd='/tmp'
    )

    output = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
    print(f'Curl return code: {result.returncode}')
    if stderr:
        print(f'Stderr: {stderr[:200]}')

    # Parse: last line is HTTP status, rest is response body
    lines = output.strip().split('\n')
    if len(lines) >= 2:
        http_code = lines[-1]
        response_body = '\n'.join(lines[:-1])
    else:
        http_code = '000'
        response_body = output

    print(f'HTTP code: {http_code}')

    if http_code == '200':
        result_json = json.loads(response_body)
        content = result_json['choices'][0]['message']['content']
        suffix = '_PM' if is_pm else '_AM'
        filename = f"AI-Report_{now.strftime('%Y-%m-%d')}{suffix}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Report saved: {filename} ({len(content)} chars)')
        github_output = os.environ.get('GITHUB_OUTPUT', '')
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write(f'filename={filename}\n')
    else:
        print(f'API Error: {response_body[:300]}')
        sys.exit(1)

finally:
    try:
        os.unlink(tmp_file)
    except:
        pass
    try:
        os.unlink('/tmp/request.json')
        os.unlink('/tmp/response.json')
    except:
        pass
