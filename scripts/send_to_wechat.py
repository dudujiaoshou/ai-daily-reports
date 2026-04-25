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

def hex_to_rgb(hex_color):
    """十六进制转RGB"""
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def interpolate_color(color1, color2, ratio):
    """插值两个颜色"""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    return (
        int(r1 + (r2 - r1) * ratio),
        int(g1 + (g2 - g1) * ratio),
        int(b1 + (b2 - b1) * ratio)
    )

def create_creative_cover(theme_key, date_str):
    """创建创意封面 - 10种风格轮换"""
    # 导入创意风格
    import importlib.util
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cover_path = os.path.join(script_dir, "cover_designs.py")
    if not os.path.exists(cover_path):
        cover_path = "cover_designs.py"
    spec = importlib.util.spec_from_file_location("cover_designs", cover_path)
    cover_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cover_module)
    
    # 获取今天的风格
    style_key, style = cover_module.get_daily_style()
    
    # 也可以根据内容主题调整
    content_style = cover_module.get_theme_style(theme_key)
    if content_style != style_key:
        # 内容主题和日期主题不同，混合使用
        style_key = content_style
        style = cover_module.COVER_STYLES[style_key]
    
    colors = style['colors']
    accent = style['accent']
    
    w, h = 900, 500
    img = Image.new('RGB', (w, h), colors[0])
    draw = ImageDraw.Draw(img)
    
    # 创建渐变背景
    for y in range(h):
        ratio = y / h
        if ratio < 0.5:
            r, g, b = interpolate_color(colors[0], colors[1], ratio * 2)
        else:
            r, g, b = interpolate_color(colors[1], colors[2], (ratio - 0.5) * 2)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    # 根据风格类型绘制装饰
    bg_type = style['bg_type']
    
    if bg_type == 'neural':
        # 神经网络 - 节点和连线
        nodes = []
        for _ in range(8):
            x = random.randint(100, 800)
            y = random.randint(50, 450)
            nodes.append((x, y))
            draw.ellipse([x-8, y-8, x+8, y+8], fill=accent)
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                if abs(n1[0]-n2[0]) + abs(n1[1]-n2[1]) < 300:
                    draw.line([n1, n2], fill=(255,255,255,30), width=1)
    
    elif bg_type == 'mesh':
        # 渐变网格 - 波浪线
        for i in range(5):
            y_base = 100 + i * 80
            points = []
            for x in range(0, w, 20):
                y = y_base + 30 * ((x % 100) / 100)
                points.append((x, int(y)))
            if len(points) > 1:
                for j in range(len(points)-1):
                    draw.line([points[j], points[j+1]], fill=(255,255,255,40), width=2)
    
    elif bg_type == 'particles':
        # 粒子星空
        for _ in range(50):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(1, 4)
            brightness = random.randint(100, 255)
            draw.ellipse([x, y, x+size, y+size], fill=(brightness, brightness, brightness))
    
    elif bg_type == 'glass':
        # 玻璃拟态 - 半透明卡片
        for _ in range(3):
            x = random.randint(50, 700)
            y = random.randint(50, 350)
            ww = random.randint(100, 200)
            hh = random.randint(80, 150)
            draw.rounded_rectangle([x, y, x+ww, y+hh], radius=15, 
                                  fill=(255,255,255,20), outline=(255,255,255,40))
    
    elif bg_type == 'circuit':
        # 电路板 - 线条和节点
        for _ in range(10):
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            if random.random() > 0.5:
                x2 = x1 + random.randint(50, 150)
                y2 = y1
            else:
                x2 = x1
                y2 = y1 + random.randint(50, 150)
            draw.line([(x1, y1), (x2, y2)], fill=accent, width=2)
            draw.ellipse([x2-4, y2-4, x2+4, y2+4], fill=accent)
    
    elif bg_type == 'aurora':
        # 极光 - 飘逸的色带
        for i in range(3):
            y_base = 150 + i * 100
            for x in range(0, w, 10):
                y = y_base + 50 * ((x % 200) / 200)
                draw.ellipse([x, int(y), x+30, int(y)+10], fill=(255,255,255,15))
    
    elif bg_type == 'matrix':
        # 矩阵代码雨
        for _ in range(20):
            x = random.randint(0, w)
            y = random.randint(0, h)
            for j in range(random.randint(3, 8)):
                draw.text((x, y + j*15), random.choice(['0','1']), fill=(0, 255, 65, 100))
    
    elif bg_type == 'hologram':
        # 全息 - 网格地面
        for i in range(0, h, 40):
            draw.line([(0, i), (w, i)], fill=(255,255,255,10), width=1)
        for i in range(0, w, 40):
            draw.line([(i, 0), (i, h)], fill=(255,255,255,10), width=1)
        # 中心发光
        draw.ellipse([w//2-100, h//2-100, w//2+100, h//2+100], fill=(255,255,255,10))
    
    elif bg_type == 'dataviz':
        # 数据可视化 - 柱状图
        for i in range(8):
            x = 100 + i * 90
            bar_h = random.randint(50, 200)
            draw.rectangle([x, h-100-bar_h, x+60, h-100], fill=(255,255,255,30))
    
    elif bg_type == 'isometric':
        # 等距方块
        for _ in range(5):
            x = random.randint(100, 700)
            y = random.randint(100, 300)
            size = random.randint(40, 80)
            # 顶面
            draw.polygon([(x, y), (x+size, y-size//2), (x+size*2, y)], fill=(255,255,255,25))
            # 右面
            draw.polygon([(x+size*2, y), (x+size*2, y+size), (x+size, y+size//2)], fill=(255,255,255,15))
            # 左面
            draw.polygon([(x, y), (x+size, y+size//2), (x+size, y+size), (x, y+size//2)], fill=(255,255,255,20))
    
    # 文字
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    
    fn_title = fn_reg = fn_small = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                fn_title = ImageFont.truetype(fp, 72)
                fn_reg = ImageFont.truetype(fp, 32)
                fn_small = ImageFont.truetype(fp, 24)
                break
            except:
                continue
    
    if not fn_title:
        fn_title = fn_reg = fn_small = ImageFont.load_default()
    
    # 顶部品牌
    label = "AI INSIDER"
    bbox = draw.textbbox((0, 0), label, font=fn_small)
    lw = bbox[2] - bbox[0]
    draw.text(((w - lw) // 2, 40), label, fill=(255, 255, 255, 200), font=fn_small)
    
    # 主标题
    title = "我的AI小管家"
    bbox = draw.textbbox((0, 0), title, font=fn_title)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, 130), title, fill='white', font=fn_title)
    
    # 风格描述
    bbox = draw.textbbox((0, 0), style['desc'], font=fn_reg)
    dw = bbox[2] - bbox[0]
    draw.text(((w - dw) // 2, 230), style['desc'], fill='#F0F4F8', font=fn_reg)
    
    # 日期
    bbox = draw.textbbox((0, 0), date_str, font=fn_small)
    dtw = bbox[2] - bbox[0]
    draw.text(((w - dtw) // 2, 300), date_str, fill='#E8EDF2', font=fn_small)
    
    # 风格标签
    bbox = draw.textbbox((0, 0), style['name'], font=fn_small)
    nw = bbox[2] - bbox[0]
    padding = 12
    draw.rounded_rectangle(
        [((w - nw) // 2 - padding, 360), ((w + nw) // 2 + padding, 395)],
        radius=15,
        fill=(255, 255, 255, 25),
        outline=(255, 255, 255, 40)
    )
    draw.text(((w - nw) // 2, 368), style['name'], fill='white', font=fn_small)
    
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
    
    # 生成创意封面
    date_str = datetime.now().strftime("%Y.%m.%d")
    print(f"🖼️ 生成创意封面...")
    cover_path = create_creative_cover(theme_key, date_str)
    
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
