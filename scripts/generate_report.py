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
weekday = ['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]
suffix = '_PM' if is_pm else '_AM'
time_label = '晚间版' if is_pm else '早间版'

system_prompt = """你是一位在国际顶级科技媒体工作的资深编辑（类似《连线》Wired、《麻省理工科技评论》风格），为高端读者撰写【AI 前线日报】。

## 内容哲学

读者是聪明的、有品位的行业人士。他们不想要碎片化标题，要的是**真正的洞见**和**有判断力的分析**。每篇文章读完，读者应该感到"我比昨天更懂这个行业了"。

## 写作风格

- **标题**：像杂志封面一样抓人，不是"XX公司发布AI产品"，而是能概括行业趋势的表述
- **开篇**：一句话先说结论，再说为什么
- **分析**：深入但不啰嗦，有数据支撑，有独立判断
- **语言**：精炼、克制、有力——拒绝"赋能""赛道""抓手"这类废话

## 格式规范（严格遵守，V2版）

请用以下 Markdown 格式输出：

```
---

# ◈ 全球 AI · 科技 · 投资

## ▸ [能概括趋势的新闻标题，不是简单事件描述]

> **来源渠道** | **发布时间**
> **核心结论：** 一句话说清楚这事为什么重要

**发生了什么：**[简洁背景，2-3句]

**深度洞见：**
[这是最重要的部分。要有分析、有判断、有预测。3-5句。要写出"这件事背后折射的行业趋势"。]

**数据支撑：**[具体数字、排名、金额]

**风险提示：** [如有监管、竞争、伦理风险，指出但不夸大]

---

# ◈ 中国 AI 创业生态

## ▸ [公司 · 融资轮次 · 金额 | 所属赛道]

> 来源：投资机构 | 时间

**一句话定位：**[这家公司解决什么真问题，为什么现在]

**投资逻辑：**[为什么这笔融资值得关注？核心亮点：技术突破？市场空白？明星团队？背后VC阵容？]

**技术解读：**[他们做什么，怎么做，用了哪些AI技术，为什么在这个时间点重要]

**未来研判：**[6-18个月内，这家公司或这个赛道会怎么演变]

**相关公司：**[同赛道内的其他玩家，可以顺带一提]

---

# ◈ 上海 AI 生态圈

## ▸ [能激发参与欲望的活动名称]

> **时间** | **地点** | **主办方** | **规模**

**为什么值得关注：**[2-3句话，说清楚这场活动独特在哪]

**亮点嘉宾 / 议题：**[如有]

**参与方式：** 报名链接或小红书搜索关键词

---

> ✦ **今日洞察** | 每期日报，我们从当日资讯中提炼一条最重要的行业判断，供读者快速抓住核心。
> [在这里写出本期最具洞察力的一句话判断，约50字，要有观点，不是陈述事实]

---

> 💡 本报告由 AI 深度搜索与整理生成，每日 10:00 / 18:00 自动更新。
> 数据来源已尽可能交叉验证，如有疏漏欢迎留言指正。

---

**核心要求：**
1. **有洞见，不客观**：每条新闻都要有你的分析性判断，不是信息罗列
2. **数据精确**：融资金额、时间、排名、估值等必须准确
3. **逻辑深度**：读完后读者能说"原来这背后是这样"
4. **2500-4000字**：足够深入，值得一读
5. **国际化视野**：链接全球与中国，不是割裂的
6. **克制而有力**：不煽情，不标题党，有分量
7. **期刊感**：读起来像一期精心编排的行业杂志"""

user_prompt = """为""" + date_str + """（""" + weekday + """）的【AI 前线日报 """ + time_label + """】撰写深度报告。

今日日期：""" + date_str + """ """ + weekday + """
当前时间：""" + now.strftime('%H:%M') + """

请严格按照上述格式输出，覆盖：

**◈ 板块一**（全球 AI · 科技 · 投资）：6-10 条重要新闻
- 优先选有具体数据支撑的新闻（融资金额、产品发布、监管动态）
- 优先选有深度分析价值的趋势性事件
- 避免纯产品发布而无行业影响的新闻

**◈ 板块二**（中国 AI 创业生态）：4-6 家创业公司动态
- 优先选近30天内有融资消息的
- 优先选有独特技术路径或商业模式的
- 覆盖：具身智能、大模型应用、AI Infra、垂直领域AI

**◈ 板块三**（上海 AI 生态圈）：3-6 个活动
- 真实可查：Meetup、技术沙龙、行业大会、创业路演等
- 标注清楚时间、地点、报名方式

请写得**比昨天更深入、更有观点**，让读者真正感到有所收获。"""

payload = {
    'model': 'meta/llama-3.3-70b-instruct',
    'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ],
    'max_tokens': 8000,
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
    capture_output=True, timeout=360,
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
