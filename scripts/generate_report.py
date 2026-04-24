#!/usr/bin/env python3
import os
import requests
from datetime import datetime

api_key = os.environ.get('NVIDIA_API_KEY')
github_output = os.environ.get('GITHUB_OUTPUT', '')

if not api_key:
    print("NVIDIA_API_KEY not found in environment variables")
    filename = f"AI-Report_{datetime.now().strftime('%Y-%m-%d')}_ERROR.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Error: NVIDIA_API_KEY not configured\n\nPlease set the NVIDIA_API_KEY in GitHub Secrets.")
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f"filename={filename}\n")
    exit(1)

url = "https://integrate.api.nvidia.com/v1/chat/completions"

now = datetime.now()
is_pm = now.hour >= 12
date_str = now.strftime('%Y年%m月%d日')
report_type = "下午" if is_pm else "上午"

system_prompt = """You are a professional AI industry analyst. Your task is to generate a comprehensive daily AI industry report based on the current date.

## Output Requirements
1. Language: Chinese (Simplified)
2. Format: Markdown with proper headings, bullet points, and structure
3. Date: Current date must be clearly mentioned in the report

## Report Structure
Generate a daily report with the following three sections:

### Section 1: Global AI/Tech/Investment News
- Top 5-8 significant news items from the past 24 hours
- Cover: AI breakthroughs, tech company moves, investment rounds, policy updates
- Each news item should have a brief analysis (1-2 sentences)
- Format: - **News title**: Analysis

### Section 2: China AI Startup Data Analysis
- 3-5 Chinese AI startups with recent funding/investment activities
- Include: Company name, funding amount, investors, sector, and potential
- Focus on: Embodied AI (robotics), AI Agents, China model progress
- Format: - **Company**: [Amount] | [Investors] | [Sector] | [Analysis]

### Section 3: Shanghai AI-Related Events
- 3-5 upcoming or recent AI events in Shanghai
- Cover: Conferences, meetups, hackathons, industry gatherings
- Include: Event name, date, venue, organizer, registration link if available
- Format: - **Event**: [Date] | [Venue] | [Organizer] | [Registration]

## Content Standards
- Be specific with data, names, and figures
- Provide your own analysis and insights, not just facts
- Highlight opportunities and risks
- Total length: 800-1500 Chinese characters"""

user_prompt = f"""请根据 {date_str} 的最新信息，生成一份专业的AI行业日报。

请确保：
1. 涵盖全球AI/科技/投资领域的最新动态
2. 分析中国AI创业公司的融资和动态数据
3. 整理上海地区近期AI相关活动信息

报告时间段：过去24小时内的重要新闻

请用中文输出完整的日报内容。"""

payload = {
    "model": "nvidia/llama-3.1-nemotron-70b-instruct",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    "max_tokens": 4000,
    "temperature": 0.7
}

headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json; charset=utf-8"
}

try:
    # Use explicit encoding for the request
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        suffix = "_PM" if is_pm else "_AM"
        filename = f"AI-Report_{now.strftime('%Y-%m-%d')}{suffix}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Report generated: {filename}")
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write(f"filename={filename}\n")
    else:
        print(f"API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
        suffix = "_PM" if is_pm else "_AM"
        filename = f"AI-Report_{now.strftime('%Y-%m-%d')}{suffix}.md"
        
        error_content = f"""# AI Daily Report - Error

**Date**: {date_str} {report_type}

## Error Information

**API Status Code**: {response.status_code}

**Error Details**:
```
{response.text}
```

Please check the NVIDIA API key and endpoint configuration.
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(error_content)
        
        if github_output:
            with open(github_output, 'a', encoding='utf-8') as f:
                f.write(f"filename={filename}\n")
                
except requests.exceptions.Timeout:
    print("Request timeout - API took too long to respond")
    suffix = "_PM" if is_pm else "_AM"
    filename = f"AI-Report_{now.strftime('%Y-%m-%d')}{suffix}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"""# AI Daily Report - Timeout

**Date**: {date_str} {report_type}

## Error Information

The NVIDIA API request timed out. Please try again later or check the API status.

""")
    
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f"filename={filename}\n")
            
except Exception as e:
    print(f"Error: {str(e)}")
    suffix = "_PM" if is_pm else "_AM"
    filename = f"AI-Report_{now.strftime('%Y-%m-%d')}{suffix}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"""# AI Daily Report - Error

**Date**: {date_str} {report_type}

## Error Information

**Error**: {str(e)}

""")
    
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f"filename={filename}\n")
