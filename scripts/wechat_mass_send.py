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
import re

# 微信配置
APPID = 'wx11daf1af1c4ccb4d'
APPSECRET = '7b0772bdb2cd6f6b22d17f1b186537bf'

# V2 莫兰迪调色板（更温暖、更有质感）
C = {
    'bg': '#FAFAF8',
    'warm_bg': '#F5F2ED',
    'primary': '#8B7355',
    'secondary': '#9B8EA0',
    'accent': '#7A9E9F',
    'accent_warm': '#C4A882',
    'text': '#2C2C2C',
    'text_light': '#777777',
    'text_lighter': '#AAAAAA',
    'border': '#E5E0D8',
    'border_light': '#EDE9E3',
    'white': '#FFFFFF',
}

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    resp = requests.get(url)
    data = resp.json()
    if 'access_token' not in data:
        print(f'获取 access_token 失败: {data}')
        return None
    return data['access_token']

def create_qr_base64(url, color=(139, 115, 85)):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(color[0], color[1], color[2]), back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('ascii')

def upload_thumb_image(token):
    def create_gradient_png(w, h, r1, g1, b1, r2, g2, b2, r3, g3, b3):
        def png_chunk(chunk_type, data):
            c = chunk_type + data
            crc = zlib.crc32(c) & 0xffffffff
            return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)
        header = b'\x89PNG\r\n\x1a\n'
        ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
        raw = b''
        for y in range(h):
            t = y / max(h - 1, 1)
            if t < 0.5:
                rt = t * 2
                r = int(r1 + (r2 - r1) * rt)
                g = int(g1 + (g2 - g1) * rt)
                b = int(b1 + (b2 - b1) * rt)
            else:
                rt = (t - 0.5) * 2
                r = int(r2 + (r3 - r2) * rt)
                g = int(g2 + (g3 - g2) * rt)
                b = int(b2 + (b3 - b2) * rt)
            raw += b'\x00' + bytes([r, g, b] * w)
        idat_data = zlib.compress(raw)
        return header + png_chunk(b'IHDR', ihdr) + png_chunk(b'IDAT', idat_data) + png_chunk(b'IEND', b'')

    # 三段渐变：暖米 -> 暖棕金 -> 柔紫灰
    png_data = create_gradient_png(900, 500,
        245, 242, 237,
        196, 168, 130,
        189, 183, 199
    )

    files = {'media': ('cover.png', png_data, 'image/png')}
    upload_url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    resp = requests.post(upload_url, files=files)
    result = resp.json()
    print(f'上传封面图: {result}')
    if 'media_id' in result:
        return result['media_id']
    return None

def md_to_wechat_html_v2(md_content, report_date, weekday):
    """V2：高端杂志风格，纯内联，无 style 标签"""

    md = md_content.strip()

    # 生成 QR 码
    xhs_qr = create_qr_base64('小红书搜索: AI日报')
    gh_qr = create_qr_base64('https://mp.weixin.qq.com')

    # ---- 封面 ----
    cover = f'''
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:linear-gradient(135deg,#F5F2ED 0%,#C4A882 50%,#9B8EA0 100%);">
<tr><td style="padding:52px 32px 48px;text-align:center;">
  <div style="display:inline-block;background:rgba(255,255,255,0.22);backdrop-filter:blur(8px);border-radius:30px;padding:8px 22px;margin-bottom:18px;">
    <span style="color:rgba(255,255,255,0.9);font-size:11px;letter-spacing:4px;font-family:-apple-system,BlinkMacSystemFont,sans-serif;">AI DAILY REPORT</span>
  </div>
  <br/>
  <span style="font-size:36px;font-weight:700;color:#fff;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;letter-spacing:2px;text-shadow:0 2px 12px rgba(0,0,0,0.12);">AI 前线日报</span>
  <br/><br/>
  <span style="font-size:14px;color:rgba(255,255,255,0.85);font-family:-apple-system,BlinkMacSystemFont,sans-serif;letter-spacing:1px;">{report_date} · {weekday} · 每日AI前沿洞察</span>
  <br/><br/>
  <div style="display:inline-block;height:1px;width:60px;background:rgba(255,255,255,0.4);"></div>
</td></tr>
</table>'''

    # ---- 今日洞察卡 ----
    insight_match = re.search(r'>\s*[✦◆]\s*\*\*(今日洞察|今日核心判断)\*\*.*?\n(.*?)(?=\n---|\Z)', md, re.DOTALL)
    insight_text = ''
    if insight_match:
        raw = insight_match.group(2).strip()
        raw = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#8B7355;">\1</strong>', raw)
        raw = raw.replace('\n', '<br/>')
        insight_text = f'''
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:20px 0;">
<tr><td style="padding:0 16px;">
  <div style="background:linear-gradient(135deg,#F5F2ED,#EDE9E3);border-radius:12px;padding:18px 20px;border-left:4px solid #8B7355;">
    <div style="font-size:11px;color:#8B7355;letter-spacing:2px;margin-bottom:8px;font-family:-apple-system,sans-serif;">✦ TODAY'S INSIGHT</div>
    <p style="font-size:15px;color:#2C2C2C;line-height:1.8;margin:0;font-family:-apple-system,'PingFang SC',sans-serif;">{raw}</p>
  </div>
</td></tr>
</table>'''

    # ---- Markdown 解析 ----
    html_body = markdown.markdown(
        md,
        extensions=['tables', 'fenced_code', 'nl2br']
    )

    # 去除 style 标签残留
    html_body = re.sub(r'<style.*?</style>', '', html_body, flags=re.DOTALL | re.IGNORECASE)

    # 替换 ul/ol 为段落
    html_body = re.sub(r'<ul>(.*?)</ul>',
        lambda m: m.group(1).replace('<li>', '<p style="padding-left:16px;margin:4px 0;font-size:15px;color:#3d3d3d;line-height:1.9;">▸ ').replace('</li>', '</p>'),
        html_body, flags=re.DOTALL)
    html_body = re.sub(r'<ol>(.*?)</ol>',
        lambda m: m.group(1).replace('<li>', '<p style="padding-left:16px;margin:4px 0;font-size:15px;color:#3d3d3d;line-height:1.9;">· ').replace('</li>', '</p>'),
        html_body, flags=re.DOTALL)
    html_body = re.sub(r'</?li[^>]*>', '', html_body)

    # ---- 引用块 ----
    def process_blockquote(m):
        inner = m.group(1).strip()
        inner = re.sub(r'<br\s*/?>', '', inner)
        lines = inner.split('\n')
        processed = []
        for line in lines:
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#8B7355;">\1</strong>', line)
            line = re.sub(r'\*(.*?)\*', r'<em style="color:#777;">\1</em>', line)
            processed.append(f'<p style="margin:4px 0;font-size:13px;color:#777;line-height:1.8;">{line}</p>')
        return '<div style="margin:16px 0;padding:14px 18px;background:#FAFAF8;border-left:3px solid #8B7355;border-radius:0 10px 10px 0;">' + ''.join(processed) + '</div>'

    html_body = re.sub(r'<blockquote>(.*?)</blockquote>', process_blockquote, html_body, flags=re.DOTALL)

    # ---- H1 ----
    def style_h1(m):
        text = m.group(1)
        return f'''
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:32px 0 16px;">
<tr><td style="padding:0 4px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:3px;height:22px;background:linear-gradient(to bottom,#8B7355,#9B8EA0);border-radius:2px;"></div>
    <span style="font-size:17px;font-weight:700;color:#2C2C2C;font-family:-apple-system,'PingFang SC',sans-serif;letter-spacing:1px;">{text}</span>
  </div>
</td></tr>
</table>'''
    html_body = re.sub(r'<h1[^>]*>(.*?)</h1>', style_h1, html_body, flags=re.IGNORECASE)

    # ---- H2 ----
    def style_h2(m):
        text = m.group(1)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#8B7355;">\1</strong>', text)
        return f'''
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:20px 0 12px;">
<tr><td style="padding:0 4px;">
  <div style="background:linear-gradient(90deg,#F5F2ED,#FAFAF8);border-radius:8px;padding:10px 14px;border-left:3px solid #C4A882;">
    <span style="font-size:15px;font-weight:600;color:#2C2C2C;line-height:1.6;font-family:-apple-system,'PingFang SC',sans-serif;">{text}</span>
  </div>
</td></tr>
</table>'''
    html_body = re.sub(r'<h2[^>]*>(.*?)</h2>', style_h2, html_body, flags=re.IGNORECASE)

    # ---- H3 ----
    def style_h3(m):
        text = m.group(1)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#8B7355;">\1</strong>', text)
        return f'<div style="margin:14px 0 8px;font-size:14px;font-weight:600;color:#2C2C2C;font-family:-apple-system,\'PingFang SC\',sans-serif;border-left:2px solid #9B8EA0;padding-left:10px;line-height:1.5;">{text}</div>'
    html_body = re.sub(r'<h3[^>]*>(.*?)</h3>', style_h3, html_body, flags=re.IGNORECASE)

    # ---- P ----
    def style_p(m):
        text = m.group(0)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#2C2C2C;font-weight:600;">\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em style="color:#777;">\1</em>', text)
        return text
    html_body = re.sub(r'<p[^>]*>(.*?)</p>', style_p, html_body, flags=re.DOTALL)

    # ---- HR ----
    html_body = re.sub(r'<hr\s*/?>', '<div style="height:1px;background:linear-gradient(to right,transparent,#E5E0D8,transparent);margin:24px 0;"></div>', html_body)

    # ---- TABLE ----
    def style_table(m):
        inner = m.group(1)
        thead_m = re.search(r'<thead>(.*?)</thead>', inner, re.DOTALL)
        tbody_m = re.search(r'<tbody>(.*?)</tbody>', inner, re.DOTALL)
        thead = thead_m.group(1) if thead_m else ''
        tbody = tbody_m.group(1) if tbody_m else ''

        def fix_th(td):
            t = td.group(0)
            return t.replace('<th', '<td style="background:#8B7355;color:#fff;padding:10px 14px;font-weight:600;font-size:13px;border-bottom:1px solid #7A6350;"').replace('</th>', '</td>')
        thead = re.sub(r'<th[^>]*>.*?</th>', fix_th, thead, flags=re.DOTALL)

        def fix_td(td):
            t = td.group(0)
            return t.replace('<td', '<td style="padding:9px 14px;border-bottom:1px solid #EDE9E3;font-size:13px;color:#2C2C2C;line-height:1.7;"')
        tbody = re.sub(r'<td[^>]*>.*?</td>', fix_td, tbody, flags=re.DOTALL)

        return f'<table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.06);margin:12px 0;"><thead>{thead}</thead><tbody>{tbody}</tbody></table>'
    html_body = re.sub(r'<table>(.*?)</table>', style_table, html_body, flags=re.DOTALL)

    # ---- CODE ----
    html_body = re.sub(r'<code>(.*?)</code>', r'<span style="background:#F0EDE8;color:#8B7355;padding:2px 7px;border-radius:4px;font-size:12px;font-family:monospace;">\1</span>', html_body)

    # ---- STRONG ----
    html_body = re.sub(r'<strong>(.*?)</strong>', r'<strong style="color:#2C2C2C;font-weight:600;">\1</strong>', html_body)

    # ---- 分隔线 ----
    follow_divider = f'''
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:8px 16px;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="flex:1;height:1px;background:linear-gradient(to right,transparent,#E5E0D8);"></div>
    <span style="color:#AAAAAA;font-size:11px;letter-spacing:3px;font-family:-apple-system,sans-serif;">CONNECT</span>
    <div style="flex:1;height:1px;background:linear-gradient(to left,transparent,#E5E0D8);"></div>
  </div>
</td></tr>
</table>'''

    # ---- 底部关注卡 ----
    follow_card = f'''
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:20px 16px;">
  <div style="background:linear-gradient(145deg,#F5F2ED,#FAFAF8);border-radius:16px;padding:24px 20px;border:1px solid #E5E0D8;">
    <div style="text-align:center;margin-bottom:16px;">
      <div style="display:inline-block;background:linear-gradient(135deg,#8B7355,#9B8EA0);color:#fff;font-size:11px;font-weight:600;padding:5px 18px;border-radius:20px;letter-spacing:2px;font-family:-apple-system,sans-serif;">STAY CONNECTED</div>
      <p style="margin:10px 0 0;font-size:13px;color:#777;font-family:-apple-system,sans-serif;">关注我们，获取更多 AI 前沿洞察</p>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td width="50%" style="text-align:center;padding:8px;">
        <div style="display:inline-block;background:#fff;border-radius:12px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05);border:1px solid #EDE9E3;">
          <img src="data:image/png;base64,{xhs_qr}" style="width:72px;height:72px;border-radius:6px;display:block;margin:0 auto;" alt="小红书"/>
        </div>
        <div style="margin-top:8px;">
          <span style="font-size:13px;font-weight:600;color:#E85D75;font-family:-apple-system,sans-serif;">小红书</span>
          <br/><span style="font-size:11px;color:#AAA;">AI日报官方账号</span>
        </div>
      </td>
      <td width="50%" style="text-align:center;padding:8px;">
        <div style="display:inline-block;background:#fff;border-radius:12px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,0.05);border:1px solid #EDE9E3;">
          <img src="data:image/png;base64,{gh_qr}" style="width:72px;height:72px;border-radius:6px;display:block;margin:0 auto;" alt="公众号"/>
        </div>
        <div style="margin-top:8px;">
          <span style="font-size:13px;font-weight:600;color:#8B7355;font-family:-apple-system,sans-serif;">微信公众号</span>
          <br/><span style="font-size:11px;color:#AAA;">AI日报</span>
        </div>
      </td>
    </tr>
    </table>
  </div>
</td></tr>
</table>'''

    # ---- 底部版权 ----
    footer = f'''
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:16px;text-align:center;">
  <div style="height:1px;background:linear-gradient(to right,transparent,#E5E0D8,transparent);margin-bottom:14px;"></div>
  <p style="margin:0 0 4px;font-size:11px;color:#AAAAAA;font-family:-apple-system,sans-serif;">由 AI 深度搜索与整理 · 每日 10:00 / 18:00 自动更新</p>
  <p style="margin:0;font-size:11px;color:#CCCCCC;font-family:-apple-system,sans-serif;">AI Daily Report © 2024-2026 · 数据已交叉验证，如有疏漏欢迎指正</p>
</td></tr>
</table>'''

    # ---- 组装 ----
    full_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#FAFAF8;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;-webkit-font-smoothing:antialiased;">
{cover}
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="padding:0 16px 20px;max-width:680px;margin:0 auto;display:block;">
{insight_text}
{html_body}
{follow_divider}
{follow_card}
{footer}
</td>
</tr>
</table>
</body>
</html>'''

    return full_html


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


print('=== 微信发布 V2 - AI 前线日报（高端杂志版）===')
print(f'AppID: {APPID[:10]}***')

files = sorted(glob.glob('AI-Report_*.md'))
if files:
    latest = files[-1]
    with open(latest, 'r', encoding='utf-8') as f:
        md_content = f.read()
else:
    print('未找到报告文件')
    sys.exit(1)

print(f'找到报告: {latest}, 长度: {len(md_content)} 字符')

token = get_access_token()
if not token:
    sys.exit(1)
print('获取 access_token 成功')

thumb_media_id = upload_thumb_image(token)
if not thumb_media_id:
    print('上传封面图失败')
    sys.exit(1)

now = datetime.now()
report_date = now.strftime('%Y年%m月%d日')
weekday = ['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]
html_content = md_to_wechat_html_v2(md_content, report_date, weekday)
print(f'转换为 V2 HTML 成功, 长度: {len(html_content)} 字符')

is_pm = now.hour >= 12
report_type = '晚间版' if is_pm else '早间版'
title = f'【AI前线日报】{report_date} {report_type}'

result = add_draft(token, title, html_content, thumb_media_id)
print(f'创建草稿: {result}')

if 'media_id' in result:
    print('=' * 40)
    print('V2 草稿创建成功！请在公众号后台手动发布。')
    print('=' * 40)
else:
    print(f'创建草稿失败: {result}')
