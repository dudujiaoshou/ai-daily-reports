#!/usr/bin/env python3
import requests
from datetime import datetime
import glob
import sys
import struct
import zlib
import markdown
import json

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
    """上传精美莫兰迪风格封面图"""
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
    
    # 莫兰迪蓝灰色封面
    png_data = create_png(400, 200, 163, 177, 189)
    files = {'media': ('thumb.png', png_data, 'image/png')}
    upload_url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    resp = requests.post(upload_url, files=files)
    result = resp.json()
    print(f'上传封面图: {result}')
    if 'media_id' in result:
        return result['media_id']
    return None

def md_to_html(md_content):
    """将 Markdown 转换为精美的微信 HTML"""
    html_body = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite'],
        extension_config={
            'codehilite': {'css_class': 'highlight'}
        }
    )
    
    styled_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", sans-serif;
    font-size: 16px;
    line-height: 1.9;
    color: #4a4a4a;
    padding: 20px;
    max-width: 100%;
    word-wrap: break-word;
    background: #fafafa;
}}

/* 封面区域 */
.cover-header {{
    text-align: center;
    padding: 20px 0 30px 0;
    border-bottom: 2px solid #e8eef4;
    margin-bottom: 24px;
}}
.cover-header .tag {{
    display: inline-block;
    background: linear-gradient(135deg, #a3b1c4, #8fa5bf);
    color: white;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 13px;
    letter-spacing: 2px;
    margin-bottom: 12px;
}}
.cover-header .title {{
    font-size: 24px;
    font-weight: 700;
    color: #2c3e50;
    letter-spacing: 1px;
    margin: 8px 0;
}}
.cover-header .date {{
    color: #95a5a6;
    font-size: 14px;
    margin-top: 8px;
}}

/* 标题样式 */
h1 {{
    font-size: 19px;
    color: #ffffff;
    background: linear-gradient(135deg, #a3b1c4, #7f8fa6);
    padding: 12px 18px;
    border-radius: 8px;
    margin: 28px 0 16px 0;
    letter-spacing: 1px;
}}

h2 {{
    font-size: 17px;
    color: #34495e;
    border-bottom: 2px solid #d5dfe7;
    padding: 10px 0 8px 0;
    margin: 24px 0 12px 0;
}}

h3 {{
    font-size: 16px;
    color: #2c3e50;
    border-left: 4px solid #a3b1c4;
    padding-left: 12px;
    margin: 16px 0 8px 0;
}}

/* 段落 */
p {{
    margin: 10px 0;
    text-align: justify;
    color: #555;
}}

/* 列表 */
ul, ol {{
    padding-left: 20px;
    margin: 10px 0;
}}
li {{
    margin: 6px 0;
    color: #555;
    line-height: 1.8;
}}

/* 引用块 */
blockquote {{
    border-left: 4px solid #a3b1c4;
    background: linear-gradient(to right, #eef3f7, #f9fbfc);
    padding: 14px 18px;
    margin: 14px 0;
    border-radius: 0 8px 8px 0;
    color: #666;
}}
blockquote p {{
    margin: 4px 0;
    color: #777;
}}

/* 强调 */
strong {{
    color: #2c3e50;
    font-weight: 600;
}}

/* 代码 */
code {{
    background: #f4f6f8;
    color: #c0392b;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 14px;
}}
pre {{
    background: #2d3436;
    color: #dfe6e9;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 14px 0;
}}
pre code {{
    background: none;
    color: #dfe6e9;
    padding: 0;
}}

/* 表格 */
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
th {{
    background: linear-gradient(135deg, #a3b1c4, #8fa5bf);
    color: white;
    padding: 10px 14px;
    text-align: left;
    font-weight: 500;
    font-size: 14px;
}}
td {{
    border-bottom: 1px solid #eef2f5;
    padding: 9px 14px;
    color: #555;
    font-size: 14px;
}}
tr:hover {{
    background: #f7f9fb;
}}

/* 分隔线 */
hr {{
    border: none;
    border-top: 1.5px dashed #d5dfe7;
    margin: 24px 0;
}}

/* 链接 */
a {{
    color: #7f8c8d;
    text-decoration: none;
}}
</style>
</head>
<body>
{html_body}
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
    json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    resp = requests.post(url, data=json_data, headers={'Content-Type': 'application/json; charset=utf-8'})
    return resp.json()

print('微信发布 - AI 日报推送 (精美版)')
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

print(f'找到报告: {latest}')

# 获取 access_token
token = get_access_token()
if not token:
    sys.exit(1)

# 上传封面图
thumb_media_id = upload_thumb_image(token)
if not thumb_media_id:
    print('上传封面图失败')
    sys.exit(1)

# 转换 Markdown → HTML
html_content = md_to_html(md_content)
print(f'转换为 HTML 成功')

# 创建草稿
now = datetime.now()
is_pm = now.hour >= 12
report_type = '晚间版' if is_pm else '早间版'
title = f'【AI日报】{now.strftime("%m/%d")} {report_type} | 时尚科技'

result = add_draft(token, title, html_content, thumb_media_id)
print(f'创建草稿: {result}')

if 'media_id' in result:
    print(f'草稿 media_id: {result["media_id"]}')
    print('草稿创建成功！请在公众号后台手动发布。')
else:
    print(f'创建草稿失败: {result}')
