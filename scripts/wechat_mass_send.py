#!/usr/bin/env python3
import requests
from datetime import datetime
import glob
import sys
import struct
import zlib
import markdown
import json
import qrcode
import io
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

def create_qr_base64(url, color=(163, 177, 189)):
    """生成 QR 码并返回 base64"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(color[0], color[1], color[2]), back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('ascii')

def upload_thumb_image(token):
    """上传封面图（渐变艺术风格，莫兰迪色调）"""
    def create_gradient_png(w, h, r1, g1, b1, r2, g2, b2):
        """创建渐变色 PNG"""
        def png_chunk(chunk_type, data):
            c = chunk_type + data
            crc = zlib.crc32(c) & 0xffffffff
            return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)
        
        header = b'\x89PNG\r\n\x1a\n'
        ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
        
        raw = b''
        for y in range(h):
            ratio = y / max(h - 1, 1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            raw += b'\x00' + bytes([r, g, b] * w)
        
        idat_data = zlib.compress(raw)
        return header + png_chunk(b'IHDR', ihdr) + png_chunk(b'IDAT', idat_data) + png_chunk(b'IEND', b'')
    
    # 莫兰迪渐变封面：雾霾蓝到淡紫灰
    png_data = create_gradient_png(900, 383, 163, 177, 189, 189, 183, 199)
    
    files = {'media': ('cover.png', png_data, 'image/png')}
    upload_url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    resp = requests.post(upload_url, files=files)
    result = resp.json()
    print(f'上传封面图: {result}')
    if 'media_id' in result:
        return result['media_id']
    return None

def md_to_wechat_html(md_content, report_date):
    """将 Markdown 转换为精美的微信公众号 HTML"""
    
    # 解析 Markdown
    html_body = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'nl2br']
    )
    
    # 生成 QR 码
    xhs_qr = create_qr_base64('小红书搜索: AI日报')
    gh_qr = create_qr_base64('https://mp.weixin.qq.com')
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
</head>
<body>

<!-- ==================== 封面横幅 ==================== -->
<div style="
    width: 100%;
    height: 200px;
    background: linear-gradient(135deg, #a3b1c4 0%, #bdc8d6 50%, #bdb7c9 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 30px 20px;
    box-sizing: border-box;
    position: relative;
">
    <div style="
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><circle cx=\"20\" cy=\"20\" r=\"30\" fill=\"rgba(255,255,255,0.05)\"/><circle cx=\"80\" cy=\"60\" r=\"40\" fill=\"rgba(255,255,255,0.05)\"/><circle cx=\"50\" cy=\"80\" r=\"20\" fill=\"rgba(255,255,255,0.03)\"/></svg>');
        background-size: 200px;
    "></div>
    <div style="
        background: rgba(255,255,255,0.25);
        backdrop-filter: blur(10px);
        border-radius: 50px;
        padding: 8px 24px;
        font-size: 13px;
        color: #fff;
        letter-spacing: 2px;
        margin-bottom: 15px;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    ">AI DAILY REPORT</div>
    <h1 style="
        font-size: 28px;
        font-weight: 700;
        color: #fff;
        margin: 0 0 8px 0;
        font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
        text-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">AI 科技日报</h1>
    <p style="
        font-size: 14px;
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: 1px;
    ">{report_date} · 每日AI前沿动态</p>
</div>

<!-- ==================== 内容区域 ==================== -->
<div style="
    max-width: 680px;
    margin: 0 auto;
    padding: 20px 16px 40px;
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    color: #2c2c2c;
    font-size: 15px;
    line-height: 1.9;
">

{html_body}

<!-- ==================== 分隔装饰 ==================== -->
<div style="
    text-align: center;
    margin: 30px 0 25px;
    position: relative;
">
    <div style="
        height: 1px;
        background: linear-gradient(to right, transparent, #d0d8e0, transparent);
        margin-bottom: 12px;
    "></div>
    <span style="
        background: #f5f7fa;
        padding: 0 16px;
        color: #a0a8b0;
        font-size: 12px;
        letter-spacing: 3px;
        text-transform: uppercase;
    ">FOLLOW ME</span>
</div>

<!-- ==================== 关注我们 ==================== -->
<div style="
    background: linear-gradient(135deg, #f8f9fb 0%, #f0f2f5 100%);
    border-radius: 16px;
    padding: 24px 20px;
    margin-bottom: 20px;
    border: 1px solid #e8ecf0;
">

    <div style="
        text-align: center;
        margin-bottom: 18px;
    ">
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #a3b1c4, #bdb7c9);
            color: white;
            font-size: 13px;
            font-weight: 600;
            padding: 6px 20px;
            border-radius: 20px;
            letter-spacing: 1px;
        ">JOIN US</div>
        <p style="
            margin: 10px 0 0;
            color: #666;
            font-size: 13px;
        ">关注获取更多 AI 前沿洞察</p>
    </div>

    <div style="
        display: flex;
        gap: 16px;
        justify-content: center;
        flex-wrap: wrap;
    ">
        <!-- 小红书 -->
        <div style="
            text-align: center;
            flex: 1;
            min-width: 120px;
        ">
            <div style="
                width: 80px;
                height: 80px;
                margin: 0 auto 8px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.06);
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #f0f0f0;
                overflow: hidden;
            ">
                <img src="data:image/png;base64,{xhs_qr}" style="width:68px;height:68px;border-radius:8px;" alt="小红书" />
            </div>
            <div style="
                font-size: 12px;
                color: #e85d75;
                font-weight: 600;
                margin-bottom: 2px;
            ">小红书</div>
            <div style="font-size: 11px; color: #999;">AI日报官方账号</div>
        </div>

        <!-- 微信公众号 -->
        <div style="
            text-align: center;
            flex: 1;
            min-width: 120px;
        ">
            <div style="
                width: 80px;
                height: 80px;
                margin: 0 auto 8px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.06);
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #f0f0f0;
                overflow: hidden;
            ">
                <img src="data:image/png;base64,{gh_qr}" style="width:68px;height:68px;border-radius:8px;" alt="公众号" />
            </div>
            <div style="
                font-size: 12px;
                color: #07c160;
                font-weight: 600;
                margin-bottom: 2px;
            ">微信公众号</div>
            <div style="font-size: 11px; color: #999;">AI日报</div>
        </div>
    </div>
</div>

<!-- ==================== 底部版权 ==================== -->
<div style="
    text-align: center;
    padding: 16px 0 8px;
    color: #c0c8d0;
    font-size: 11px;
    border-top: 1px solid #eef0f3;
    margin-top: 10px;
">
    <p style="margin: 0 0 4px;">由 AI 自动生成 · 每日更新</p>
    <p style="margin: 0; color: #d0d8e0;">AI Daily Report © 2024-2026</p>
</div>

</div>

</body>
</html>'''

    # 添加内容样式
    styled_html = f'''
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f5f7fa;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
}}

/* 标题样式 */
body h1 {{
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #1a1a2e !important;
    margin: 28px 0 12px !important;
    padding: 12px 16px !important;
    background: linear-gradient(135deg, rgba(163,177,196,0.12) 0%, rgba(189,183,201,0.12) 100%) !important;
    border-left: 4px solid #a3b1c4 !important;
    border-radius: 0 8px 8px 0 !important;
    line-height: 1.5 !important;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif !important;
}}

body h2 {{
    font-size: 17px !important;
    font-weight: 600 !important;
    color: #2d3748 !important;
    margin: 22px 0 10px !important;
    padding: 8px 14px !important;
    background: rgba(163,177,196,0.08) !important;
    border-left: 3px solid #bdc8d6 !important;
    border-radius: 0 6px 6px 0 !important;
    line-height: 1.5 !important;
}}

body h3 {{
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #4a5568 !important;
    margin: 14px 0 8px !important;
    padding-left: 10px !important;
    border-left: 2px solid #c8d0d8 !important;
}}

/* 段落 */
body p {{
    font-size: 15px !important;
    line-height: 1.95 !important;
    color: #3d3d3d !important;
    margin: 8px 0 !important;
    text-align: justify !important;
}}

/* 列表 */
body ul, body ol {{
    padding-left: 22px !important;
    margin: 8px 0 !important;
    color: #3d3d3d !important;
}}

body li {{
    font-size: 15px !important;
    line-height: 1.9 !important;
    margin: 4px 0 !important;
    color: #3d3d3d !important;
}}

/* 引用 */
body blockquote {{
    margin: 12px 0 !important;
    padding: 12px 16px !important;
    background: linear-gradient(135deg, rgba(163,177,196,0.08) 0%, rgba(189,183,201,0.08) 100%) !important;
    border-left: 3px solid #a3b1c4 !important;
    border-radius: 0 8px 8px 0 !important;
    color: #5a6270 !important;
    font-style: italic !important;
}}

body blockquote p {{
    color: #5a6270 !important;
    margin: 0 !important;
    font-size: 14px !important;
}}

/* 表格 */
body table {{
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 14px 0 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}}

body th {{
    background: linear-gradient(135deg, #a3b1c4, #bdc8d6) !important;
    color: white !important;
    padding: 10px 12px !important;
    font-weight: 600 !important;
    text-align: left !important;
    font-size: 13px !important;
}}

body td {{
    padding: 8px 12px !important;
    border-bottom: 1px solid #eef0f3 !important;
    color: #3d3d3d !important;
    font-size: 13px !important;
}}

body tr:last-child td {{
    border-bottom: none !important;
}}

body tr:nth-child(even) td {{
    background: #f8f9fb !important;
}}

/* 代码 */
body code {{
    background: #f0f2f5 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    color: #6a7a8a !important;
    font-family: 'SF Mono', 'Menlo', monospace !important;
}}

body pre {{
    background: #f8f9fb !important;
    padding: 14px !important;
    border-radius: 8px !important;
    overflow-x: auto !important;
    border: 1px solid #eef0f3 !important;
    margin: 12px 0 !important;
}}

body pre code {{
    background: none !important;
    padding: 0 !important;
}}

/* 分割线 */
body hr {{
    border: none !important;
    height: 1px !important;
    background: linear-gradient(to right, transparent, #d0d8e0, transparent) !important;
    margin: 20px 0 !important;
}}

/* 链接 */
body a {{
    color: #7a8fa8 !important;
    text-decoration: none !important;
    border-bottom: 1px solid #c8d0d8 !important;
}}

/* 加粗 */
body strong {{
    color: #2d3748 !important;
    font-weight: 600 !important;
}}

/* 图片 */
body img {{
    max-width: 100% !important;
    height: auto !important;
    border-radius: 8px !important;
    margin: 10px 0 !important;
    display: block !important;
}}
</style>

{html}
'''
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

print('=== 微信发布 - AI 日报推送（精美版）===')
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
print('获取 access_token 成功')

# 上传封面图
thumb_media_id = upload_thumb_image(token)
if not thumb_media_id:
    print('上传封面图失败')
    sys.exit(1)

# 转换 Markdown → 精美 HTML
now = datetime.now()
report_date = now.strftime('%Y年%m月%d日')
html_content = md_to_wechat_html(md_content, report_date)
print(f'转换为精美 HTML 成功, 长度: {len(html_content)} 字符')

# 创建草稿
is_pm = now.hour >= 12
report_type = '晚间版' if is_pm else '早间版'
title = f'【AI日报】{report_date} {report_type}'

result = add_draft(token, title, html_content, thumb_media_id)
print(f'创建草稿: {result}')

if 'media_id' in result:
    print('=' * 40)
    print('草稿创建成功！请在公众号后台手动发布。')
    print('=' * 40)
else:
    print(f'创建草稿失败: {result}')
