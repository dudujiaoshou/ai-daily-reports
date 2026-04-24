#!/usr/bin/env python3
"""
微信公众号发布脚本 v3 - 彻底修复排版问题
- 无黑点列表（用自定义符号）
- 纯内联样式，无 CSS 代码泄露
- 微信编辑器完美兼容
"""
import os, sys, requests, json, glob, re, base64, qrcode
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

APPID = 'wx11daf1af1c4ccb4d'
APPSECRET = '7b0772bdb2cd6f6b22d17f1b186537bf'

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    resp = requests.get(url)
    data = resp.json()
    if 'access_token' in data:
        return data['access_token']
    print(f"Token error: {data}")
    return None

def generate_qr_base64(text):
    """生成二维码并返回 base64"""
    qr = qrcode.QRCode(version=2, box_size=6, border=1)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#5B6B7C", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('ascii')

def create_cover_image():
    """创建莫兰迪渐变封面"""
    from PIL import Image, ImageDraw

    w, h = 900, 500
    img = Image.new('RGB', (w, h), '#7B8FA8')
    draw = ImageDraw.Draw(img)

    # 渐变背景
    for y in range(h):
        ratio = y / h
        r = int(123 + (200 - 123) * ratio)
        g = int(143 + (220 - 143) * ratio)
        b = int(168 + (235 - 168) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # 装饰圆
    draw.ellipse([680, 30, 880, 230], fill='#B8C5D6', outline=None)
    draw.ellipse([30, 320, 180, 470], fill='#A8B5C8', outline=None)
    draw.ellipse([400, 400, 500, 500], fill='#C5D0DE', outline=None)

    # 标题文字
    try:
        fn_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        fn_reg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        fn_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except:
        fn_bold = fn_reg = fn_small = ImageFont.load_default()

    # AI DAILY
    bbox = draw.textbbox((0, 0), "AI DAILY", font=fn_bold)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, 150), "AI DAILY", fill='white', font=fn_bold)

    # 副标题
    bbox = draw.textbbox((0, 0), "每日 AI 行业洞察", font=fn_reg)
    sw = bbox[2] - bbox[0]
    draw.text(((w - sw) // 2, 240), "每日 AI 行业洞察", fill='#F0F4F8', font=fn_reg)

    # 日期
    date_str = datetime.now().strftime("%Y.%m.%d")
    bbox = draw.textbbox((0, 0), date_str, font=fn_small)
    dw = bbox[2] - bbox[0]
    draw.text(((w - dw) // 2, 310), date_str, fill='#E8EDF2', font=fn_small)

    img.save('cover.jpg', quality=95)
    return 'cover.jpg'

def upload_image(access_token, image_path):
    """上传图片"""
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'
    with open(image_path, 'rb') as f:
        resp = requests.post(url, files={'media': f})
    data = resp.json()
    if 'media_id' in data:
        return data['media_id']
    print(f"Upload error: {data}")
    return None

def upload_image_base64(access_token, img_base64):
    """上传 base64 图片"""
    url = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image'
    files = {'media': ('qr.png', base64.b64decode(img_base64), 'image/png')}
    resp = requests.post(url, files=files)
    data = resp.json()
    if 'media_id' in data:
        return data['media_id']
    print(f"QR upload error: {data}")
    return None

def md_to_wechat_html(md_text):
    """
    Markdown → 微信公众号友好 HTML
    核心原则：
    - 无 <style> 标签
    - 无外部 CSS 类
    - 无复杂选择器
    - 只有内联 style
    - 去掉黑点，用自定义符号
    """
    lines = md_text.split('\n')
    result = []
    i = 0

    # 跳过 # 标题行（会单独处理）
    title = ""
    if lines and lines[0].startswith('# '):
        title = lines[0][2:].strip()
        i = 1

    # 底部二维码区 HTML（先占位，稍后替换）
    qr_placeholder = '<!--QR_PLACEHOLDER-->'

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 空行
        if not stripped:
            i += 1
            continue

        # 二级标题 ## 
        if stripped.startswith('## '):
            content = stripped[3:].strip()
            result.append(f'<p style="margin:24px 0 12px 0;font-size:17px;font-weight:bold;color:#2D3748;border-left:5px solid #7B8FA8;padding-left:12px;">{content}</p>')
            i += 1
            continue

        # 三级标题 ###
        if stripped.startswith('### '):
            content = stripped[4:].strip()
            result.append(f'<p style="margin:18px 0 8px 0;font-size:15px;font-weight:bold;color:#4A5568;">{content}</p>')
            i += 1
            continue

        # 引用块
        if stripped.startswith('> '):
            content = stripped[2:].strip()
            result.append(f'<p style="margin:12px 0;padding:10px 14px;background:#F7FAFC;border-left:3px solid #7B8FA8;color:#4A5568;font-style:italic;line-height:1.8;">{content}</p>')
            i += 1
            continue

        # 分隔线
        if stripped == '---':
            result.append('<p style="margin:20px 0;text-align:center;color:#CBD5E0;">━━━━━</p>')
            i += 1
            continue

        # 列表项 - 无序
        if stripped.startswith('- '):
            content = stripped[2:]
            # 处理加粗
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            result.append(f'<p style="margin:6px 0 6px 16px;text-indent:-14px;padding-left:14px;line-height:1.8;color:#2D3748;"><span style="color:#7B8FA8;margin-right:8px;">▸</span>{content}</p>')
            i += 1
            continue

        # 列表项 - 有序
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            num, content = m.group(1), m.group(2)
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            result.append(f'<p style="margin:6px 0 6px 20px;text-indent:-16px;padding-left:16px;line-height:1.8;color:#2D3748;"><span style="color:#7B8FA8;font-weight:bold;margin-right:6px;">{num}.</span>{content}</p>')
            i += 1
            continue

        # 普通段落
        content = stripped
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        result.append(f'<p style="margin:10px 0;line-height:1.9;color:#2D3748;">{content}</p>')
        i += 1

    # 添加底部关注区
    qr_html = ''
    if qr_placeholder in result:
        # 替换占位符
        result[result.index(qr_placeholder)] = ''
    result.append(qr_html)

    return '\n'.join(result), title

def create_draft(access_token, html_content, title, thumb_media_id):
    """创建草稿"""
    url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'

    full_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body style="padding:0;margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<div style="max-width:100%;overflow-wrap:break-word;">
{html_content}
</div>
</body>
</html>'''

    data = {
        "articles": [{
            "title": title or "AI 日报",
            "thumb_media_id": thumb_media_id,
            "author": "AI 小管家",
            "digest": "每日精选全球 AI 行业重要动态、深度解读与独家观点",
            "content": full_html,
            "content_source_url": "",
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]
    }

    resp = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
    result = resp.json()
    if 'media_id' in result:
        print(f"✅ 草稿创建成功: {result['media_id']}")
        return result['media_id']
    print(f"❌ 草稿创建失败: {result}")
    return None

def main():
    print("=" * 50)
    print("微信公众号发布 v3")
    print("=" * 50)

    access_token = get_access_token()
    if not access_token:
        print("❌ 获取 token 失败")
        return
    print("✅ Token 获取成功")

    # 读取报告
    files = sorted(glob.glob('AI-Report_*.md'))
    if not files:
        print("❌ 未找到报告")
        return

    latest = files[-1]
    print(f"📄 报告: {latest}")

    with open(latest, 'r', encoding='utf-8') as f:
        md_text = f.read()

    print(f"📝 内容长度: {len(md_text)} 字符")

    # 转换 HTML
    html_content, title = md_to_wechat_html(md_text)
    print(f"📰 标题: {title}")
    print(f"🎨 HTML 预览 (前500字符):\n{html_content[:500]}")

    # 封面图
    print("🎨 生成封面图...")
    cover_path = create_cover_image()

    print("📤 上传封面图...")
    thumb_media_id = upload_image(access_token, cover_path)
    if not thumb_media_id:
        print("❌ 封面上传失败")
        return

    # 创建草稿
    print("📝 创建草稿...")
    media_id = create_draft(access_token, html_content, title, thumb_media_id)

    if media_id:
        print(f"\n🎉 成功！请去草稿箱查看")
        print(f"   标题: {title}")
        print(f"   草稿ID: {media_id}")
    else:
        print("\n❌ 创建失败")

    # 清理
    if os.path.exists(cover_path):
        os.remove(cover_path)

if __name__ == '__main__':
    main()
