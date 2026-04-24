#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, requests
from datetime import datetime

api_key = os.environ.get('NVIDIA_API_KEY', '')
if not api_key:
    print('ERROR: NVIDIA_API_KEY not set')
    sys.exit(1)

url = 'https://integrate.api.nvidia.com/v1/chat/completions'
now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y年%m月%d日')

system_prompt = """你是一位专业的AI行业分析师。请为当前日期生成一份综合的每日AI行业报告。
报告必须包含三个板块，全部使用简体中文：
1. 全球AI/Tech/投资新闻：5-8条过去24小时重要新闻，每条附1-2句分析
2. 中国AI创业公司动态：3-5家公司，包含融资金额、投资方、领域和分析
3. 上海AI相关活动：3-5个即将举办的活动，包含日期、场地、报名链接
内容要具体有数据，800-1500字。"""

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

# Build headers WITHOUT charset in Content-Type (semicolons in headers can cause issues)
# Use only ASCII characters in headers
req_headers = {
    'Authorization': 'Bearer ' + api_key,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print('Calling NVIDIA API...')
try:
    resp = requests.post(url, headers=req_headers, json=payload, timeout=120)
    print(f'Response status: {resp.status_code}')

    if resp.status_code == 200:
        # Manual UTF-8 decode to avoid any encoding issues
        raw_text = resp.content.decode('utf-8')
        result = json.loads(raw_text)
        content = result['choices'][0]['message']['content']
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
        print(f'API Error {resp.status_code}: {resp.text[:200]}')
        sys.exit(1)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
