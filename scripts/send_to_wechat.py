import os, sys, requests, json, base64, re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

APPID = 'wx11daf1af1c4ccb4d'
APPSECRET = '7b0772bdb2cd6f6b22d17f1b186537bf'

# 动态封面主题库
COVER_THEMES = {
    'default': {
        'name': '森林雾绿',
        'colors': ['#6B8E6B', '#8DAF83', '#A8C8A0'],
        'accent': '#C5D4B8',
        'icon': 'AI',
        'desc': '每日 AI 行业洞察'
    },
    'funding': {
        'name': '深海蓝金',
        'colors': ['#2C5F7C', '#4A8BB8', '#6B9EBD'],
        'accent': '#A8C5D8',
        'icon': '$',
        'desc': '资本涌动，暗流之下见真章'
    },
    'robot': {
        'name': '机械橙灰',
        'colors': ['#8B6F47', '#B8956A', '#D4B896'],
        'accent': '#E8D5C0',
        'icon': '⚙',
        'desc': '具身智能，让机器拥有温度'
    },
    'model': {
        'name': '极光紫蓝',
        'colors': ['#5B4B8A', '#7B6BAA', '#9B8BCA'],
        'accent': '#C0B4E0',
        'icon': '◈',
        'desc': '大模型进化，重新定义智能边界'
    },
    'coding': {
        'name': '代码青柠',
        'colors': ['#4A7C59', '#6B9E7B', '#8CBE9B'],
        'accent': '#B0D4C0',
        'icon': '</>',
        'desc': '代码新生，AI重构创造力'
    },
    'policy': {
        'name': '政务靛青',
        'colors': ['#3A5A6A', '#5A7A8A', '#7A9AAA'],
        'accent': '#A0C0D0',
        'icon': '§',
        'desc': '政策风向，把握时代脉搏'
    }
}

def analyze_content_theme(html_content):
    """分析内容主题，返回对应的封面主题"""
    content_lower = html_content.lower()
    
    # 检查关键词
    if any(k in content_lower for k in ['融资', '轮', '估值', '投资', '资本', '收购']):
        return 'funding'
    elif any(k in content_lower for k in ['机器人', '具身', '人形', 'booster', 'optimus']):
        return 'robot'
    elif any(k in content_lower for k in ['gpt', 'claude', '模型', '大模型', 'llm', 'gemini']):
        return 'model'
    elif any(k in content_lower for k in ['代码', '编程', 'cursor', 'coding', 'vibe', 'github']):
        return 'coding'
    elif any(k in content_lower for k in ['政策', '统计', '国家', '监管', '法案']):
        return 'policy'
    
    return 'default'

def create_dynamic_cover(theme_key, date_str):
    """创建动态主题封面"""
    theme = COVER_THEMES.get(theme_key, COVER_THEMES['default'])
    colors = theme['colors']
    
    w, h = 900, 500
    img = Image.new('RGB', (w, h), colors[0])
    draw = ImageDraw.Draw(img)
    
    # 渐变背景
    for y in range(h):
        ratio = y / h
        if ratio < 0.5:
            r = int(int(colors[0][1:3], 16) + (int(colors[1][1:3], 16) - int(colors[0][1:3], 16)) * (ratio * 2))
            g = int(int(colors[0][3:5], 16) + (int(colors[1][3:5], 16) - int(colors[0][3:5], 16)) * (ratio * 2))
            b = int(int(colors[0][5:7], 16) + (int(colors[1][5:7], 16) - int(colors[0][5:7], 16)) * (ratio * 2))
        else:
            r = int(int(colors[1][1:3], 16) + (int(colors[2][1:3], 16) - int(colors[1][1:3], 16)) * ((ratio - 0.5) * 2))
            g = int(int(colors[1][3:5], 16) + (int(colors[2][3:5], 16) - int(colors[1][3:5], 16)) * ((ratio - 0.5) * 2))
            b = int(int(colors[1][5:7], 16) + (int(colors[2][5:7], 16) - int(colors[1][5:7], 16)) * ((ratio - 0.5) * 2))
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    # 装饰元素 - 根据主题变化
    if theme_key == 'funding':
        # 金币/投资主题装饰
        draw.ellipse([700, 50, 850, 200], fill=(255, 255, 255, 30))
        draw.ellipse([50, 300, 200, 450], fill=(255, 255, 255, 20))
    elif theme_key == 'robot':
        # 机械齿轮装饰
        draw.rectangle([720, 80, 820, 180], fill=(255, 255, 255, 25), outline=(255, 255, 255, 40))
        draw.rectangle([80, 320, 180, 420], fill=(255, 255, 255, 15), outline=(255, 255, 255, 30))
    elif theme_key == 'model':
        # 神经网络节点装饰
        for pos in [(750, 100), (800, 150), (700, 180)]:
            draw.ellipse([pos[0]-20, pos[1]-20, pos[0]+20, pos[1]+20], fill=(255, 255, 255, 35))
    else:
        # 默认圆形装饰
        draw.ellipse([680, 30, 880, 230], fill=(255, 255, 255, 25))
        draw.ellipse([30, 320, 180, 470], fill=(255, 255, 255, 15))
    
    # 文字 - 尝试加载中文字体
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
        "C:/Windows/Fonts/simhei.ttf",  # Windows
        "C:/Windows/Fonts/simsun.ttc",  # Windows
    ]
    
    fn_bold = fn_reg = fn_small = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                fn_bold = ImageFont.truetype(fp, 68)
                fn_reg = ImageFont.truetype(fp, 32)
                fn_small = ImageFont.truetype(fp, 24)
                break
            except:
                continue
    
    if not fn_bold:
        fn_bold = fn_reg = fn_small = ImageFont.load_default()
    
    # 主题图标
    bbox = draw.textbbox((0, 0), theme['icon'], font=fn_bold)
    iw = bbox[2] - bbox[0]
    draw.text(((w - iw) // 2, 120), theme['icon'], fill='white', font=fn_bold)
    
    # 标题
    bbox = draw.textbbox((0, 0), "AI DAILY", font=fn_reg)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, 200), "AI DAILY", fill='white', font=fn_reg)
    
    # 描述
    bbox = draw.textbbox((0, 0), theme['desc'], font=fn_small)
    dw = bbox[2] - bbox[0]
    draw.text(((w - dw) // 2, 260), theme['desc'], fill='#F0F4F8', font=fn_small)
    
    # 日期
    bbox = draw.textbbox((0, 0), date_str, font=fn_small)
    dtw = bbox[2] - bbox[0]
    draw.text(((w - dtw) // 2, 310), date_str, fill='#E8EDF2', font=fn_small)
    
    img.save('cover_dynamic.jpg', quality=95)
    return 'cover_dynamic.jpg'

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    resp = requests.get(url)
    data = resp.json()
    if 'access_token' in data:
        return data['access_token']
    print(f"Token error: {data}")
    return None

def upload_image(access_token, image_path):
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'
    with open(image_path, 'rb') as f:
        resp = requests.post(url, files={'media': f})
    data = resp.json()
    if 'media_id' in data:
        return data['media_id']
    print(f"Upload error: {data}")
    return None

def create_draft(access_token, html_content, thumb_media_id, title_suffix=""):
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
            "title": f"我的AI小管家 | {title_suffix or datetime.now().strftime('%Y年%m月%d日')}",
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
    
    # 分析内容主题
    theme_key = analyze_content_theme(html_content)
    theme = COVER_THEMES.get(theme_key, COVER_THEMES['default'])
    print(f"🎨 检测到主题: {theme['name']} ({theme_key})")
    
    # 生成动态封面
    date_str = datetime.now().strftime("%Y.%m.%d")
    print(f"🖼️ 生成动态封面: {theme['name']}...")
    cover_path = create_dynamic_cover(theme_key, date_str)
    
    print("📤 上传封面图...")
    thumb_media_id = upload_image(access_token, cover_path)
    if not thumb_media_id:
        print("❌ 封面上传失败")
        return
    
    # 创建草稿
    print("📝 创建草稿...")
    media_id = create_draft(access_token, html_content, thumb_media_id, date_str)
    
    if media_id:
        print(f"\n🎉 成功！请去公众号草稿箱查看")
        print(f"   标题: 我的AI小管家 | {date_str}")
        print(f"   主题: {theme['name']}")
        print(f"   草稿ID: {media_id}")
    else:
        print("\n❌ 创建失败")
    
    # 清理
    if os.path.exists(cover_path):
        os.remove(cover_path)

if __name__ == '__main__':
    main()
