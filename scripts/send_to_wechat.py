import os, sys, requests, json, base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

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

def create_cover_image():
    """创建森林雾绿渐变封面"""
    w, h = 900, 500
    img = Image.new('RGB', (w, h), '#6B8E6B')
    draw = ImageDraw.Draw(img)

    # 渐变背景
    for y in range(h):
        ratio = y / h
        r = int(107 + (168 - 107) * ratio)
        g = int(142 + (200 - 142) * ratio)
        b = int(107 + (160 - 107) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # 装饰圆
    draw.ellipse([680, 30, 880, 230], fill='#8BAF8B')
    draw.ellipse([30, 320, 180, 470], fill='#7A9A7A')

    # 标题文字
    try:
        fn_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        fn_reg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        fn_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except:
        fn_bold = fn_reg = fn_small = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), "AI DAILY", font=fn_bold)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, 150), "AI DAILY", fill='white', font=fn_bold)

    bbox = draw.textbbox((0, 0), "每日 AI 行业洞察", font=fn_reg)
    sw = bbox[2] - bbox[0]
    draw.text(((w - sw) // 2, 240), "每日 AI 行业洞察", fill='#F0F4F8', font=fn_reg)

    date_str = datetime.now().strftime("%Y.%m.%d")
    bbox = draw.textbbox((0, 0), date_str, font=fn_small)
    dw = bbox[2] - bbox[0]
    draw.text(((w - dw) // 2, 310), date_str, fill='#E8EDF2', font=fn_small)

    img.save('cover_green.jpg', quality=95)
    return 'cover_green.jpg'

def upload_image(access_token, image_path):
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'
    with open(image_path, 'rb') as f:
        resp = requests.post(url, files={'media': f})
    data = resp.json()
    if 'media_id' in data:
        return data['media_id']
    print(f"Upload error: {data}")
    return None

def create_draft(access_token, html_content, thumb_media_id):
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
            "title": "我的AI小管家 | 2026年4月24日",
            "thumb_media_id": thumb_media_id,
            "author": "我的AI小管家",
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
    print("微信公众号草稿发布")
    print("=" * 50)

    access_token = get_access_token()
    if not access_token:
        print("❌ 获取 token 失败")
        return
    print("✅ Token 获取成功")

    # 读取HTML
    with open('preview_draft.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 提取body内容
    import re
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
    if body_match:
        html_content = body_match.group(1)

    print(f"📄 HTML 内容长度: {len(html_content)} 字符")

    # 封面图
    print("🎨 生成森林雾绿封面图...")
    cover_path = create_cover_image()

    print("📤 上传封面图...")
    thumb_media_id = upload_image(access_token, cover_path)
    if not thumb_media_id:
        print("❌ 封面上传失败")
        return

    # 创建草稿
    print("📝 创建草稿...")
    media_id = create_draft(access_token, html_content, thumb_media_id)

    if media_id:
        print(f"\n🎉 成功！请去公众号草稿箱查看")
        print(f"   标题: 我的AI小管家 | 2026年4月24日")
        print(f"   草稿ID: {media_id}")
    else:
        print("\n❌ 创建失败")

    # 清理
    if os.path.exists(cover_path):
        os.remove(cover_path)

if __name__ == '__main__':
    main()
