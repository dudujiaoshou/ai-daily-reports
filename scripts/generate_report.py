#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests
from datetime import datetime

api_key = os.environ.get('NVIDIA_API_KEY')
github_output = os.environ.get('GITHUB_OUTPUT', '')

if not api_key:
    print('NVIDIA_API_KEY not found in environment variables')
    now = datetime.now()
    is_pm = now.hour >= 12
    suffix = '_PM' if is_pm else '_AM'
    filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# Error: NVIDIA_API_KEY not configured\n\nPlease set the NVIDIA_API_KEY in GitHub Secrets.')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
    exit(1)

url = 'https://integrate.api.nvidia.com/v1/chat/completions'

now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y年%m月%d日')
report_type = '下午' if is_pm else '上午'

system_prompt = '''你是一位专业的AI行业分析师。你的任务是生成一份综合的每日AI行业报告，日期为''' + date_str + '''。

# 输出格式要求
1. 语言：简体中文
2. 格式：Markdown格式，包含标题、项目符号和结构化内容
3. 日期：报告中必须明确标注当前日期

# 报告结构
请生成一份包含以下三个板块的日报：

## 板块1：全球AI/Tech/投资新闻
- 过去24小时内最重要的5-8条AI相关新闻
- 覆盖：AI突破性进展、科技公司动态、投资融资、政策更新等
- 每条新闻需要有简短分析（1-2句话）
- 格式：- **新闻标题**：分析

## 板块2：中国AI创业公司数据分析
- 3-5家中国AI创业公司近期动态
- 包含：融资金额、投资方、领域、以及分析
- 重点关注：具身智能（机器人）、AI Agents、中国模型进展
- 格式：- **公司名**：[金额] | [投资方] | [领域] | [分析]

## 板块3：上海AI相关活动
- 3-5个即将举办或近期举办的AI活动
- 包含：活动名称、日期、场地、主办方、报名链接（如有）
- 格式：- **活动名**：[日期] | [场地] | [主办方] | [报名链接]

# 内容标准
- 内容要具体，包含数据、人名、金额等信息
- 提供你自己的分析和洞察，不仅仅是罗列事实
- 突出投资机会和风险
- 总字数：800-1500个中文字符'''

user_prompt = '请为' + date_str + '生成一份专业的AI行业日报，涵盖全球AI新闻、中国AI创业动态和上海AI活动。'

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
    'Content-Type': 'application/json; charset=utf-8'
}

try:
    # KEY FIX: Manual JSON encoding with UTF-8 to avoid latin-1 codec error
    json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    print('Calling NVIDIA API with model: meta/llama-3.3-70b-instruct')
    response = requests.post(url, headers=headers, data=json_data, timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        suffix = '_PM' if is_pm else '_AM'
        filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('Report generated successfully: ' + filename)
        print('Content length: ' + str(len(content)) + ' chars')
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
    else:
        print('API Error: ' + str(response.status_code))
        print('Response: ' + response.text)
        
        suffix = '_PM' if is_pm else '_AM'
        filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
        
        error_content = '# AI Daily Report - Error\n\n**Date**: ' + date_str + ' ' + report_type + '\n\n## Error Information\n\n**API Status Code**: ' + str(response.status_code) + '\n\n**Error Details**:\n```\n' + response.text + '\n```\n\nPlease check the NVIDIA API key and endpoint configuration.\n'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(error_content)
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write('filename=' + filename + '\n')
                
except requests.exceptions.Timeout:
    print('Request timeout - API took too long to respond')
    suffix = '_PM' if is_pm else '_AM'
    filename = 'AI-Report_' + now.strftime('%Y-%m-%d') + suffix + '.md'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('# AI Daily Report - Timeout\n\n**Date**: ' + date_str + ' ' + report_type + '\n\n## Error Information\n\nThe NVIDIA API request timed out. Please try again later or check the API status.\n')
    
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
        f.write('# AI Daily Report - Error\n\n**Date**: ' + date_str + ' ' + report_type + '\n\n## Error Information\n\n**Error**: ' + str(e) + '\n\n```\n' + traceback.format_exc() + '\n```\n')
    
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
