#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, subprocess
from datetime import datetime

api_key = os.environ.get('NVIDIA_API_KEY', '').strip()
if not api_key:
    print('ERROR: NVIDIA_API_KEY not set')
    sys.exit(1)

url = 'https://integrate.api.nvidia.com/v1/chat/completions'
now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y年%m月%d日')
suffix = '_PM' if is_pm else '_AM'
time_label = '晚间版' if is_pm else '早间版'

system_prompt = """你是一位资深的AI行业研究员，为【AI前线日报】撰写深度行业报告。

请严格遵循以下精美格式输出，全部使用简体中文：

---

# 【全球 AI · 科技 · 投资动态】🌐

## [新闻标题]
- 🏷️ 消息来源 | ⏰ 发布时间
- 📌 **核心事件**：[一句话概括]
- 🔍 **深度解读**：[2-3句专业分析，说明为什么重要、对行业的影响]
- ⚠️ **风险提示**：[如有潜在风险需指出]

---

# 【中国 AI 创业生态】🇨🇳

## 🏢 公司名 / 轮次 / 融资金额
- 📂 所在领域：[细分领域]
- 💰 投资方：[投资机构名称]
- 📝 业务概述：[一句话介绍]
- 🎯 **投资逻辑**：[为什么这笔投资值得关注，对行业意味着什么]

---

# 【上海 AI 生态圈】📍

## 🎪 活动名称
- 📅 日期/时间 | 📍 地点
- 🎯 主办方
- 🔗 报名/直播链接

---

> ✨ **阅读提示**：本报告由 AI 自动生成，涵盖当日全球 AI 行业重要动态、中国 AI 创业生态及上海本地活动，每条新闻均附深度解读。

---

**要求**：
1. 每条新闻必须有深度解读，不能只是摘要
2. 融资金额必须精确到具体数字
3. 活动必须有真实的报名渠道
4. 总字数 1500-2500 字
5. 语言精炼、专业、有洞见
6. 避免空洞的套话，每句话都要有价值"""

user_prompt = """为""" + date_str + """的【AI前线日报 """ + time_label + """】撰写深度行业报告。

今日日期：""" + date_str + """
当前时间：""" + now.strftime('%H:%M') + """

请严格按照上述格式输出，覆盖：
- 🌐 板块一：5-8 条全球重要 AI/科技/投资新闻（优先选有具体数据、有分析价值的）
- 🇨🇳 板块二：3-5 家中国 AI 创业公司动态（优先选有融资的）
- 📍 板块三：3-5 个上海 AI 相关活动（ Meetup、沙龙、大会、展会等）"""

payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ],
    'max_tokens': 5000,
    'temperature': 0.7
}

with open('/tmp/request.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)

result = subprocess.run(
    ['curl', '-s', '-X', 'POST', url,
     '-H', 'Authorization: Bearer ' + api_key,
     '-H', 'Content-Type: application/json',
     '-d', '@/tmp/request.json',
     '-w', '\n%{http_code}'],
    capture_output=True, timeout=150,
    cwd='/tmp'
)

output = result.stdout.decode('utf-8', errors='replace')

lines = output.strip().split('\n')
if len(lines) >= 2:
    http_code = lines[-1]
    response_body = '\n'.join(lines[:-1])
else:
    http_code = '000'
    response_body = output

print('HTTP code:', http_code)

if http_code == '200':
    result_json = json.loads(response_body)
    content = result_json['choices'][0]['message']['content']
    filename = "AI-Report_" + now.strftime('%Y-%m-%d') + suffix + ".md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Report saved:', filename, '(' + str(len(content)) + ' chars)')
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write('filename=' + filename + '\n')
else:
    print('API Error:', response_body[:500])
    sys.exit(1)
