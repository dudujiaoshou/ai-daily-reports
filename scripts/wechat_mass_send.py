#!/usr/bin/env python3
"""
微信群发脚本 - AI 前线日报
莫兰迪配色 · 优雅排版 · 国际时尚审美
"""
import os, io, json, base64, requests, glob
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import urllib.request

# 凭证
APP_ID = os.environ.get('WX_APPID')
APP_SECRET = os.environ.get('WX_APPSECRET')

# 莫兰迪配色方案
MORANDI = {
    'sage': '#9CAF88',      # 灰绿色 - 主色调
    'dusty_rose': '#C9A9A6', # 灰粉色
    'warm_gray': '#B8B0A8',  # 暖灰色
    'lavender': '#A8A3B5',   # 灰紫色
    'terracotta': '#C4A484', # 陶土色
    'deep_blue': '#6B7B8C',  # 灰蓝色
    'cream': '#F5F0EB',      # 米白色背景
    'charcoal': '#4A4A4A',   # 深灰色文字
    'soft_blue': '#8FAABE',  # 柔蓝色
}

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token'
    params = {'grant_type': 'client_credential', 'appid': APP_ID, 'secret': APP_SECRET}
    resp = requests.get(url, params=params)
    data = resp.json()
    if 'access_token' in data:
        return data['access_token']
    raise Exception(f"获取 access_token 失败: {data}")

def get_latest_report():
    files = sorted(glob.glob('AI-Report_*.md'))
    if not files:
        return None, None
    latest = files[-1]
    with open(latest, 'r', encoding='utf-8') as f:
        content = f.read()
    return latest, content

def create_elegant_cover():
    """创建优雅的莫兰迪色系封面图"""
    width, height = 900, 500

    # 创建渐变背景
    img = Image.new('RGB', (width, height), MORANDI['cream'])
    draw = ImageDraw.Draw(img)

    # 莫兰迪渐变色块
    for i in range(height):
        ratio = i / height
        r = int(245 - ratio * 30)
        g = int(240 - ratio * 40)
        b = int(235 - ratio * 20)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # 添加装饰性几何元素
    # 左上角圆形
    draw.ellipse([50, 50, 180, 180], fill=MORANDI['sage'] + '40')

    # 右下角圆形
    draw.ellipse([700, 350, 850, 500], fill=MORANDI['dusty_rose'] + '40')

    # 中间装饰线
    draw.line([100, 250, 800, 250], fill=MORANDI['warm_gray'], width=1)

    # AI 图标区域（抽象线条）
    center_x, center_y = 450, 200
    for i in range(3):
        offset = (i - 1) * 80
        draw.arc([center_x - 60 + offset, center_y - 60, center_x + 60 + offset, center_y + 60],
                 start=30, end=150, fill=MORANDI['deep_blue'], width=2)

    # 主标题
    title_text = "AI FRONTLINE"
    subtitle_text = "前沿日报"

    # 保存到内存
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', quality=95)
    return img_bytes.getvalue()

def markdown_to_html(md_content, title, report_date):
    """将 Markdown 转换为优雅的 HTML"""
    import re

    # 解析 markdown
    html_parts = []

    # 标题样式映射
    def convert_header(match):
        level = len(match.group(1))
        text = match.group(2).strip()
        colors = {
            1: MORANDI['charcoal'],
            2: MORANDI['deep_blue'],
            3: MORANDI['sage'],
        }
        sizes = {1: '28px', 2: '22px', 3: '18px'}
        borders = {
            1: f'border-left: 4px solid {MORANDI["sage"]}; padding-left: 15px;',
            2: f'border-left: 3px solid {MORANDI["dusty_rose"]}; padding-left: 12px;',
            3: f'border-bottom: 1px solid {MORANDI["warm_gray"]}; padding-bottom: 5px;',
        }
        return f'<h{level} style="color: {colors.get(level, MORANDI["charcoal"])}; font-size: {sizes.get(level, "16px")}; {borders.get(level, "")} margin-top: 35px; margin-bottom: 15px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, \'PingFang SC\', \'Helvetica Neue\', sans-serif;">{text}</h{level}>'

    content = re.sub(r'^(#{1,3})\s+(.+)$', convert_header, md_content, flags=re.MULTILINE)

    # 处理加粗
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: ' + MORANDI['sage'] + '; font-weight: 600;">\1</strong>', content)

    # 处理列表
    content = re.sub(r'^-\s+(.+)$', r'<li style="margin: 8px 0; padding-left: 5px; color: ' + MORANDI['charcoal'] + r';">\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'(<li.+?</li>\n?)+', lambda m: f'<ul style="margin: 10px 0; padding-left: 20px;">{m.group(0)}</ul>', content)

    # 处理换行
    content = content.replace('\n\n', '</p><p style="margin: 12px 0; line-height: 1.8; color: ' + MORANDI['charcoal'] + ';">').strip()
    content = f'<p style="margin: 12px 0; line-height: 1.8; color: {MORANDI["charcoal"]};">{content}</p>'

    # 完整 HTML
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            color: {MORANDI['charcoal']};
            background: {MORANDI['cream']};
            padding: 0;
            margin: 0;
        }}
        .container {{
            max-width: 680px;
            margin: 0 auto;
            padding: 40px 25px;
        }}
        .header {{
            text-align: center;
            padding: 50px 20px;
            background: linear-gradient(135deg, {MORANDI['cream']} 0%, #EEEAE5 100%);
            border-radius: 0 0 40px 40px;
            margin-bottom: 40px;
        }}
        .header-tag {{
            display: inline-block;
            background: {MORANDI['sage']};
            color: white;
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 12px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 32px;
            font-weight: 700;
            color: {MORANDI['charcoal']};
            margin: 0 0 10px 0;
            letter-spacing: 1px;
        }}
        .header .subtitle {{
            color: {MORANDI['warm_gray']};
            font-size: 16px;
            margin: 0;
        }}
        .header .date {{
            color: {MORANDI['deep_blue']};
            font-size: 14px;
            margin-top: 15px;
        }}
        .divider {{
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, {MORANDI['sage']}, {MORANDI['dusty_rose']});
            margin: 30px auto;
            border-radius: 2px;
        }}
        .content {{
            background: white;
            border-radius: 20px;
            padding: 35px 30px;
            box-shadow: 0 5px 30px rgba(0,0,0,0.05);
        }}
        h1, h2, h3 {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", sans-serif;
        }}
        strong {{
            color: {MORANDI['sage']};
            font-weight: 600;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        li {{
            position: relative;
            padding-left: 18px;
            margin: 10px 0;
        }}
        li::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 10px;
            width: 6px;
            height: 6px;
            background: {MORANDI['sage']};
            border-radius: 50%;
        }}
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: {MORANDI['warm_gray']};
            font-size: 13px;
        }}
        .footer .brand {{
            font-size: 14px;
            color: {MORANDI['deep_blue']};
            margin-bottom: 8px;
        }}
        blockquote {{
            background: {MORANDI['cream']};
            border-left: 4px solid {MORANDI['sage']};
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 12px 12px 0;
            font-style: italic;
            color: {MORANDI['deep_blue']};
        }}
        code {{
            background: {MORANDI['cream']};
            padding: 2px 8px;
            border-radius: 4px;
            font-family: "SF Mono", Consolas, monospace;
            font-size: 14px;
            color: {MORANDI['terracotta']};
        }}
        pre {{
            background: {MORANDI['cream']};
            padding: 15px;
            border-radius: 10px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-tag">AI 前沿日报</div>
            <h1>{title}</h1>
            <p class="subtitle">人工智能行业深度洞察</p>
            <p class="date">{report_date}</p>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <div class="divider"></div>
            <p class="brand">AI Frontline Daily</p>
            <p>由 AI 前沿日报系统自动生成</p>
        </div>
    </div>
</body>
</html>'''
    return html

def upload_cover_image(access_token, img_bytes):
    """上传封面图"""
    url = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image'
    files = {'media': ('cover.png', img_bytes, 'image/png')}
    resp = requests.post(url, files=files)
    data = resp.json()
    if 'media_id' in data:
        return data['media_id']
    print(f"封面上传: {data}")
    return None

def create_news_article(access_token, title, html_content, thumb_media_id, digest):
    """创建图文消息"""
    url = f'https://api.weixin.qq.com/cgi-bin/media/uploadnews?access_token={access_token}'
    articles = [{
        'title': title,
        'thumb_media_id': thumb_media_id,
        'author': 'AI 前沿日报',
        'digest': digest,
        'show_cover_pic': 1,
        'content': html_content,
        'content_source_url': ''
    }]
    resp = requests.post(url, json={'articles': articles})
    result = resp.json()
    if 'media_id' in result:
        return result['media_id']
    raise Exception(f"创建图文消息失败: {result}")

def mass_send(access_token, media_id):
    """群发消息"""
    url = f'https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}'
    data = {
        'filter': {'is_to_all': True, 'tag_id': 0},
        'msgtype': 'mpnews',
        'mpnews': {'media_id': media_id}
    }
    resp = requests.post(url, json=data)
    return resp.json()

def main():
    print("=" * 50)
    print("AI 前沿日报 - 微信群发")
    print("=" * 50)

    if not APP_ID or not APP_SECRET:
        print("错误: 未设置 WX_APPID 或 WX_APPSECRET")
        return

    # 1. 获取报告
    filename, md_content = get_latest_report()
    if not filename:
        print("未找到报告")
        return
    print(f"报告: {filename}")

    # 2. 生成标题
    now = datetime.now()
    is_pm = now.hour >= 12
    report_type = "晚间版" if is_pm else "早间版"
    title = f"AI 前沿日报 {report_type} {now.strftime('%m/%d')}"
    report_date = now.strftime('%Y年%m月%d日 %H:%M')

    # 3. 转换为 HTML
    print("生成优雅排版...")
    digest = md_content[:120] + '...'
    html_content = markdown_to_html(md_content, title, report_date)
    print(f"HTML 长度: {len(html_content)}")

    # 4. 获取 token
    print("获取 access_token...")
    try:
        access_token = get_access_token()
        print("Token 获取成功")
    except Exception as e:
        print(f"Token 获取失败: {e}")
        return

    # 5. 上传封面
    print("上传封面图...")
    img_bytes = create_elegant_cover()
    thumb_id = upload_cover_image(access_token, img_bytes)
    if thumb_id:
        print(f"封面 ID: {thumb_id}")
    else:
        thumb_id = ""

    # 6. 创建图文
    print("创建图文消息...")
    try:
        media_id = create_news_article(access_token, title, html_content, thumb_id, digest)
        print(f"图文 ID: {media_id}")
    except Exception as e:
        print(f"创建失败: {e}")
        return

    # 7. 群发
    print("执行群发...")
    result = mass_send(access_token, media_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result.get('errcode') == 0:
        print(f"\n✅ 群发成功! msg_id: {result.get('msg_id')}")
    else:
        print(f"\n❌ 群发失败: {result.get('errmsg')}")

if __name__ == '__main__':
    main()
