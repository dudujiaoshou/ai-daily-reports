#!/usr/bin/env python3
import requests
from datetime import datetime
import glob
import sys

# 微信配置
APPID = 'wx11daf1af1c4ccb4d'
APPSECRET = '7b0772bdb2cd6f6b22d17f1b186537bf'

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    resp = requests.get(url)
    data = resp.json()
    if 'access_token' not in data:
        print(f'获取 access_token 失败: {data}')
        return None
    return data['access_token']

def add_draft(token, title, content):
    url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
    payload = {
        'articles': [
            {
                'title': title,
                'author': 'AI Daily',
                'digest': title,
                'content': content,
                'content_source_url': '',
                'need_open_comment': 0,
                'only_fans_can_comment': 0
            }
        ]
    }
    resp = requests.post(url, json=payload)
    return resp.json()

def publish_draft(token, media_id):
    url = f'https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}'
    resp = requests.post(url, json={'media_id': media_id})
    return resp.json()

print('微信发布 - AI 日报推送')
print(f'AppID: {APPID[:10]}***')

# 获取报告
files = sorted(glob.glob('AI-Report_*.md'))
if files:
    latest = files[-1]
    with open(latest, 'r', encoding='utf-8') as f:
        content = f.read()
else:
    print('未找到报告文件')
    sys.exit(1)

print(f'找到报告: {latest}')

# 获取 access_token
token = get_access_token()
if not token:
    sys.exit(1)

# 创建草稿
now = datetime.now()
is_pm = now.hour >= 12
report_type = '晚间版' if is_pm else '早间版'
title = f'【AI日报】{now.strftime("%m/%d")} {report_type}'

result = add_draft(token, title, content)
print(f'创建草稿: {result}')

if 'media_id' in result:
    media_id = result['media_id']
    print(f'草稿 media_id: {media_id}')
    pub_result = publish_draft(token, media_id)
    print(f'发布结果: {pub_result}')
    if pub_result.get('errcode') == 0:
        print('发布成功!')
    else:
        print(f'发布失败: {pub_result}')
else:
    print(f'创建草稿失败: {result}')
