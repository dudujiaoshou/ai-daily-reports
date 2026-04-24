#!/usr/bin/env python3
import requests
from datetime import datetime
import glob
import sys
import struct
import zlib
import markdown

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
    """上传封面图（永久素材，莫兰迪蓝色）"""
    def create_png(w, h, r, g, b):
        def png_chunk(chunk_type, data):
            c = chunk_type + data
            crc = zlib.crc32(c) & 0xffffffff
            return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)
        
        header = b'\x89PNG\r\n\x1a\n'
        ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
        raw = b''
        for y in range(h):
            raw += b'\x00' + bytes([r, g, b] * w)
        idat_data = zlib.compress(raw)
        
        return header + png_chunk(b'IHDR', ihdr) + png_chunk(b'IDAT', idat_data) + png_chunk(b'IEND', b'')
    
    # 莫兰迪蓝灰色封面 - 微信封面图建议尺寸 2:1 或 900x383
    png_data = create_png(400, 200, 163, 177, 189)
    
    # 使用永久素材接口
    files = {'media': ('thumb.png', png_data, 'image/png')}
    upload_url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    resp = requests.post(upload_url, files=files)
    result = resp.json()
    print(f'上传封面图(永久素材): {result}')
    if 'media_id' in result:
        return result['media_id']
    
    # 如果永久素材接口失败，尝试临时素材
    print('永久素材失败，尝试临时素材...')
    upload_url2 = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image'
    resp2 = requests.post(upload_url2, files=files)
    result2 = resp2.json()
    print(f'上传封面图(临时素材): {result2}')
    if 'media_id' in result2:
        return result2['media_id']
    
    return None

def md_to_html(md_content):
    """将 Markdown 转换为适合微信的 HTML"""
    html = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite']
    )
    
    styled_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    padding: 15px;
    max-width: 100%;
    word-wrap: break-word;
}}
h1 {{
    font-size: 22px;
    color: #1a1a1a;
    border-bottom: 2px solid #a3b1c4;
    padding-bottom: 8px;
    margin-top: 15px;
}}
h2 {{
    font-size: 18px;
    color: #2d3748;
    border-left: 4px solid #a3b1c4;
    padding-left: 10px;
    margin-top: 18px;
}}
h3 {{
    font-size: 16px;
    color: #4a5568;
    margin-top: 12px;
}}
p {{
    margin: 8px 0;
    text-align: justify;
}}
ul, ol {{
    padding-left: 20px;
    margin: 8px 0;
}}
li {{
    margin: 4px 0;
}}
blockquote {{
    border-left: 3px solid #a3b1c4;
    background: #f7f9fb;
    padding: 8px 12px;
    margin: 8px 0;
    color: #555;
}}
strong {{
    color: #2d3748;
}}
code {{
    background: #f1f3f5;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 14px;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}
th {{
    background: #a3b1c4;
    color: white;
}}
hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 12px 0;
}}
</style>
</head>
<body>
{html}
</body>
</html>'''
    return styled_html

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

print('微信发布 - AI 日报推送')
print(f'AppID: {APPID[:10]}***')

# 获取报告
files = sorted(glob.glob('AI-Report_*.md'))
if files:
    latest = files[-1]
    with open(latest, 'r', encoding='utf-8') as f:
        md_content = f.read()
else:
    print('未找到报告文件')
    sys.exit(1)

print(f'找到报告: {latest}, 长度: {len(md_content)} 字符')

# 获取 access_token
token = get_access_token()
if not token:
    sys.exit(1)
print(f'获取 access_token 成功')

# 上传封面图
thumb_media_id = upload_thumb_image(token)
if not thumb_media_id:
    print('上传封面图失败')
    sys.exit(1)

# 转换 Markdown → HTML
html_content = md_to_html(md_content)
print(f'转换为 HTML 成功, 长度: {len(html_content)} 字符')

# 创建草稿
now = datetime.now()
is_pm = now.hour >= 12
report_type = '晚间版' if is_pm else '早间版'
title = f'【AI日报】{now.strftime("%m/%d")} {report_type}'

result = add_draft(token, title, html_content, thumb_media_id)
print(f'创建草稿: {result}')

if 'media_id' in result:
    print(f'草稿 media_id: {result["media_id"]}')
    print('草稿创建成功！请在公众号后台手动发布。')
else:
    print(f'创建草稿失败: {result}')
