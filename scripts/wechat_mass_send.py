#!/usr/bin/env python3
"""
微信公众号发布脚本 - 适配订阅号权限
使用简单干净的 HTML，避免复杂 CSS
"""
import os
import requests
import json
import glob
from datetime import datetime
import base64
import qrcode
from io import BytesIO

APPID = 'wx11daf1af1c4ccb4d'
APPSECRET = '7b0772bdb2cd6f6b22d17f1b186537bf'

def get_access_token():
    """获取微信 access_token"""
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    resp = requests.get(url)
    data = resp.json()
    if 'access_token' in data:
        return data['access_token']
    print(f"Token error: {data}")
    return None

def generate_qr_code(text, filename):
    """生成二维码"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#4A5568", back_color="white")
    img.save(filename)
    return filename

def upload_image(access_token, image_path):
    """上传图片到微信素材库"""
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'
    with open(image_path, 'rb') as f:
        files = {'media': f}
        resp = requests.post(url, files=files)
    data = resp.json()
    if 'media_id' in data:
        return data['media_id']
    print(f"Upload image error: {data}")
    return None

def create_cover_image():
    """创建简洁的封面图"""
    from PIL import Image, ImageDraw, ImageFont
    
    # 莫兰迪色系背景
    width, height = 900, 500
    img = Image.new('RGB', (width, height), '#8B9DC3')
    draw = ImageDraw.Draw(img)
    
    # 添加装饰圆
    draw.ellipse([650, 50, 850, 250], fill='#B8C5D6')
    draw.ellipse([50, 350, 200, 500], fill='#A8B8CC')
    
    # 尝试加载字体
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        date_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = date_font = title_font
    
    # 标题
    title = "AI DAILY"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = bbox[2] - bbox[0]
    draw.text(((width - title_w) // 2, 180), title, fill='white', font=title_font)
    
    # 副标题
    subtitle = "每日 AI 行业洞察"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    sub_w = bbox[2] - bbox[0]
    draw.text(((width - sub_w) // 2, 260), subtitle, fill='#F0F0F0', font=subtitle_font)
    
    # 日期
    now = datetime.now()
    date_str = now.strftime("%Y.%m.%d")
    bbox = draw.textbbox((0, 0), date_str, font=date_font)
    date_w = bbox[2] - bbox[0]
    draw.text(((width - date_w) // 2, 320), date_str, fill='#E0E0E0', font=date_font)
    
    img.save('cover.jpg', quality=95)
    return 'cover.jpg'

def markdown_to_simple_html(md_content):
    """将 Markdown 转换为微信公众号友好的简单 HTML"""
    import re
    
    html = md_content
    
    # 提取标题
    title_match = re.search(r'# (.+)', html)
    main_title = title_match.group(1) if title_match else "AI日报"
    
    # 移除标题行
    html = re.sub(r'# .+\n', '', html)
    
    # 转换二级标题为加粗段落（不用 h2，避免样式问题）
    html = re.sub(r'## (.+)', r'<p style="margin:25px 0 15px 0;font-size:18px;font-weight:bold;color:#2D3748;border-left:4px solid #8B9DC3;padding-left:12px;">\1</p>', html)
    
    # 转换三级标题
    html = re.sub(r'### (.+)', r'<p style="margin:20px 0 10px 0;font-size:16px;font-weight:bold;color:#4A5568;">\1</p>', html)
    
    # 转换加粗
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # 处理列表项 - 去掉黑点，改用自定义符号
    lines = html.split('\n')
    result_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # 检查是否是列表项
        if stripped.startswith('- ') or stripped.startswith('* '):
            content = stripped[2:]
            # 移除内容中的 ** 标记（已经转换过了）
            content = content.replace('**', '')
            # 使用自定义符号代替黑点
            result_lines.append(f'<p style="margin:8px 0;padding-left:20px;text-indent:-15px;"><span style="color:#8B9DC3;margin-right:8px;">▸</span>{content}</p>')
        elif stripped.startswith('1. ') or stripped.startswith('2. ') or stripped.startswith('3. '):
            content = stripped[3:]
            num = stripped[0]
            result_lines.append(f'<p style="margin:8px 0;padding-left:20px;"><span style="color:#8B9DC3;font-weight:bold;">{num}.</span> {content}</p>')
        elif stripped == '':
            continue
        else:
            # 普通段落
            if stripped and not stripped.startswith('<p'):
                result_lines.append(f'<p style="margin:12px 0;line-height:1.8;color:#2D3748;">{stripped}</p>')
            else:
                result_lines.append(line)
    
    html = '\n'.join(result_lines)
    
    # 转换分隔线
    html = re.sub(r'\n---\n', '<hr style="border:none;border-top:1px solid #E2E8F0;margin:20px 0;">', html)
    
    # 转换引用
    html = re.sub(r'&gt; (.+)', r'<p style="margin:15px 0;padding:12px 15px;background:#F7FAFC;border-left:3px solid #8B9DC3;color:#4A5568;font-style:italic;">\1</p>', html)
    
    return html, main_title

def create_draft(access_token, html_content, title, thumb_media_id):
    """创建图文消息草稿"""
    url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'
    
    # 构建完整文章内容 - 使用简单干净的样式
    full_html = f"""<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:15px;line-height:1.8;color:#2D3748;padding:10px;">
<div style="max-width:100%;">
{html_content}
</div>
</body>
</html>"""
    
    data = {
        "articles": [{
            "title": title,
            "thumb_media_id": thumb_media_id,
            "author": "AI小管家",
            "digest": "每日精选全球AI行业重要动态、深度解读与独家观点",
            "content": full_html,
            "content_source_url": "",
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]
    }
    
    resp = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
    result = resp.json()
    
    if 'media_id' in result:
        print(f"✅ Draft created: {result['media_id']}")
        return result['media_id']
    else:
        print(f"❌ Draft error: {result}")
        return None

def main():
    print("="*60)
    print("微信公众号发布脚本")
    print("="*60)
    
    # 获取 access_token
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取 access_token")
        return
    print("✅ Access token obtained")
    
    # 读取最新报告
    files = sorted(glob.glob('AI-Report_*.md'))
    if not files:
        print("❌ 未找到报告文件")
        return
    
    latest = files[-1]
    print(f"📄 使用报告: {latest}")
    
    with open(latest, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 转换 Markdown 为简单 HTML
    html_content, title = markdown_to_simple_html(md_content)
    print(f"📰 文章标题: {title}")
    
    # 创建封面图
    print("🎨 生成封面图...")
    cover_path = create_cover_image()
    
    # 上传封面图
    print("📤 上传封面图...")
    thumb_media_id = upload_image(access_token, cover_path)
    if not thumb_media_id:
        print("❌ 封面上传失败")
        return
    print(f"✅ 封面上传成功: {thumb_media_id}")
    
    # 创建草稿
    print("📝 创建草稿...")
    media_id = create_draft(access_token, html_content, title, thumb_media_id)
    
    if media_id:
        print(f"\n🎉 成功！文章已进入草稿箱")
        print(f"   Media ID: {media_id}")
        print(f"   请登录公众号后台手动发布")
    else:
        print("\n❌ 创建草稿失败")
    
    # 清理临时文件
    if os.path.exists(cover_path):
        os.remove(cover_path)

if __name__ == '__main__':
    main()
