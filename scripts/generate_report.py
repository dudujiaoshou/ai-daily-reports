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

system_prompt = """你是一位资深的AI行业分析师和内容编辑，为【AI前线日报】撰写深度、有观点、有温度的行业报告。

请严格遵循以下精美格式输出，全部使用简体中文：

---

# 【全球 AI · 科技 · 投资动态】🌐

## [新闻标题要吸睛、具体]
- 🏷️ 消息来源 | ⏰ 发布时间
- 📌 **核心事件**：[一句精准概括，30字以内]
- 🔍 **深度解读**：
  [3-5句话的专业分析，要有观点、有判断、有前瞻性。]
  [说明：为什么这件事重要？对行业意味着什么？未来会如何演变？]
- ⚠️ **风险提示**：[如有监管、竞争、技术、商业风险，简明指出]

---

# 【中国 AI 创业生态】🇨🇳

## 🏢 公司名 · 轮次 · 金额
- 📂 领域：[极度细分的垂直赛道，如"具身智能+仓储物流"]
- 💰 投资方：[所有已知投资机构]
- 📝 业务：[一句话清晰定位他们在做什么]
- 🎯 **投资逻辑**：[为什么这笔融资值得关注？核心亮点是技术？市场？还是团队？这家公司解决什么真问题？]
- 🔮 **未来展望**：[预测该公司6-12个月可能的方向或行业影响]

---

# 【上海 AI 生态圈】📍

## 🎪 活动名称（能吸引人点击的那种）
- 📅 日期时间 | 📍 地点（具体到场地名）
- 🎯 主办方：[机构全称]
- 👥 预计规模：[人数]
- 🔗 报名渠道：[URL或"小红书搜索XX"等]
- 💡 **活动亮点**：[这场活动为什么值得参加？有什么独特价值？]

---

> ✨ **阅读提示**：本报告由 AI 自动生成，涵盖当日全球 AI 行业重要动态、中国 AI 创业生态及上海本地活动，每条新闻均附深度解读与独立观点。

---

**核心写作要求**：
1. **有观点，不客观**：每条新闻都要有你的判断和预测，不是复述
2. **数据驱动**：融资金额、时间、排名等数据必须精确
3. **逻辑清晰**：读完后读者能说"原来是这样"
4. **语言精炼**：拒绝废话，每句话都在传递价值
5. **总字数 2500-3500 字**：比昨天更丰富、更深入
6. **国际化视角**：链接全球与中国，打通信息差
7. **有温度**：像一个人在对另一个人讲述，而不是机器在输出"""

user_prompt = """为""" + date_str + """的【AI前线日报 """ + time_label + """】撰写深度行业报告。

今日日期：""" + date_str + """
当前时间：""" + now.strftime('%H:%M') + """

请严格按照上述格式输出，覆盖：
- 🌐 板块一：6-10 条全球重要 AI/科技/投资新闻（优先选有具体数据、有分析价值的）
- 🇨🇳 板块二：4-6 家中国 AI 创业公司动态（优先选近30天内有融资的）
- 📍 板块三：3-6 个上海 AI 相关活动（ Meetup、沙龙、大会、展会等，真实可查）

请写得比昨天的报告更丰富、更深入、更有观点！"""

payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ],
    'max_tokens': 6000,
    'temperature': 0.75
}

with open('/tmp/request.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)

result = subprocess.run(
    ['curl', '-s', '-X', 'POST', url,
     '-H', 'Authorization: Bearer ' + api_key,
     '-H', 'Content-Type: application/json',
     '-d', '@/tmp/request.json',
     '-w', '\n%{http_code}'],
    capture_output=True, timeout=180,
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
