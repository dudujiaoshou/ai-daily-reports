#!/usr/bin/env python3
import requests
from datetime import datetime
import glob
import sys
import base64

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

def upload_thumb_image(token):
    """上传封面图（使用纯色占位图）"""
    # 创建一个简单的 200x200 PNG 纯色图
    import struct, zlib
    
    def create_png(w, h, r, g, b):
        def png_chunk(chunk_type, data):
            c = chunk_type + data
            crc = zlib.crc32(c) & 0xffffffff
            return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)
        
        header = b'\x89PNG\r\n\x1a\n'
        ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
        # 简单扫描线
        raw = b''
        for y in range(h):
            raw += b'\x00' + bytes([r, g, b] * w)
        idat_data = zlib.compress(raw)
        
        return header + png_chunk(b'IHDR', ihdr) + png_chunk(b'IDAT', idat_data) + png_chunk(b'IEND', b'')
    
    # 莫兰迪蓝色封面
    png_data = create_png(200, 200, 163, 177, 189)  # 莫兰迪蓝灰色
    files = {'media': ('thumb.png', png_data, 'image/png')}
    upload_url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    resp = requests.post(upload_url, files=files)
    result = resp.json()
    print(f'上传封面图: {result}')
    if 'media_id' in result:
        return result['media_id']
    # 尝试临时素材
    upload_url2 = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image'
    resp2 = requests.post(upload_url2, files=files)
    result2 = resp2.json()
    print(f'上传临时封面图: {result2}')
    return result2.get('media_id')

def add_draft(token, title, content, thumb_media_id):
    url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
    payload = {
        'articles': [
            {
                'title': title,
                'author': 'AI Daily',
                'digest': title,
                'content': content,
                'thumb_media_id': thumb_media_id,
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

# 上传封面图
thumb_media_id = upload_thumb_image(token)
if not thumb_media_id:
    print('上传封面图失败，无法创建文章')
    sys.exit(1)

# 创建草稿
now = datetime.now()
is_pm = now.hour >= 12
report_type = '晚间版' if is_pm else '早间版'
title = f'【AI日报】{now.strftime("%m/%d")} {report_type}'

result = add_draft(token, title, content, thumb_media_id)
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
