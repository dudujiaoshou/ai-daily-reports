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

def create_dynamic_cover(theme_key, date_str):
    """创建动态主题封面 - 增强视觉设计"""
    theme = COVER_THEMES.get(theme_key, COVER_THEMES['default'])
    colors = theme['colors']
    
    w, h = 900, 500
    img = Image.new('RGB', (w, h), colors[0])
    draw = ImageDraw.Draw(img)
    
    # 创建更丰富的渐变背景
    for y in range(h):
        ratio = y / h
        if ratio < 0.3:
            r, g, b = interpolate_color(colors[0], colors[1], ratio / 0.3)
        elif ratio < 0.7:
            r, g, b = interpolate_color(colors[1], colors[2], (ratio - 0.3) / 0.4)
        else:
            r, g, b = interpolate_color(colors[2], colors[0], (ratio - 0.7) / 0.3)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    # 添加几何图案装饰 - 更有设计感
    # 大圆形装饰
    draw.ellipse([-100, -100, 300, 300], fill=(255, 255, 255, 8))
    draw.ellipse([600, 200, 1000, 600], fill=(255, 255, 255, 5))
    
    # 网格线装饰
    for i in range(0, w, 60):
        draw.line([(i, 0), (i, h)], fill=(255, 255, 255, 3), width=1)
    for i in range(0, h, 60):
        draw.line([(0, i), (w, i)], fill=(255, 255, 255, 3), width=1)
    
    # 主题特定装饰元素
    if theme_key == 'funding':
        # 金币/投资主题 - 添加圆形和线条
        for i in range(5):
            x = 700 + i * 30
            y = 80 + i * 20
            draw.ellipse([x, y, x+40, y+40], fill=(255, 215, 0, 40), outline=(255, 255, 255, 60))
        # 上升箭头
        draw.polygon([(100, 400), (130, 350), (160, 400)], fill=(255, 255, 255, 20))
        draw.line([(130, 350), (130, 450)], fill=(255, 255, 255, 30), width=3)
        
    elif theme_key == 'robot':
        # 机械/机器人主题 - 齿轮状装饰
        for i in range(6):
            angle = i * 60
            import math
            cx, cy = 800, 150
            x1 = cx + 60 * math.cos(math.radians(angle))
            y1 = cy + 60 * math.sin(math.radians(angle))
            x2 = cx + 80 * math.cos(math.radians(angle))
            y2 = cy + 80 * math.sin(math.radians(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 40), width=8)
        draw.ellipse([cx-50, cy-50, cx+50, cy+50], fill=(255, 255, 255, 15), outline=(255, 255, 255, 30))
        
    elif theme_key == 'model':
        # AI模型主题 - 神经网络节点
        nodes = [(750, 100), (820, 150), (780, 220), (720, 180), (850, 200)]
        for node in nodes:
            draw.ellipse([node[0]-15, node[1]-15, node[0]+15, node[1]+15], 
                        fill=(255, 255, 255, 30), outline=(255, 255, 255, 50))
        # 连接线
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                draw.line([nodes[i], nodes[j]], fill=(255, 255, 255, 15), width=2)
                
    elif theme_key == 'coding':
        # 代码主题 - 代码块装饰
        for i in range(4):
            y = 100 + i * 40
            draw.rectangle([50, y, 200, y+20], fill=(255, 255, 255, 10))
            draw.rectangle([50, y, 100 + i*30, y+20], fill=(255, 255, 255, 20))
        # 光标
        draw.rectangle([220, 100, 225, 180], fill=(255, 255, 255, 40))
        
    elif theme_key == 'policy':
        # 政策主题 - 建筑/文件装饰
        draw.rectangle([700, 100, 750, 250], fill=(255, 255, 255, 10), outline=(255, 255, 255, 20))
        draw.rectangle([760, 150, 810, 250], fill=(255, 255, 255, 15), outline=(255, 255, 255, 25))
        draw.rectangle([820, 80, 870, 250], fill=(255, 255, 255, 8), outline=(255, 255, 255, 15))
        # 顶部三角形
        draw.polygon([(725, 80), (700, 100), (750, 100)], fill=(255, 255, 255, 20))
        draw.polygon([(785, 130), (760, 150), (810, 150)], fill=(255, 255, 255, 25))
        draw.polygon([(845, 60), (820, 80), (870, 80)], fill=(255, 255, 255, 15))
    else:
        # 默认主题 - 抽象圆形和线条
        draw.ellipse([650, 50, 850, 250], fill=(255, 255, 255, 8))
        draw.ellipse([50, 300, 250, 500], fill=(255, 255, 255, 5))
        # 装饰线
        draw.arc([100, 100, 300, 300], 0, 90, fill=(255, 255, 255, 20), width=2)
        draw.arc([600, 200, 800, 400], 180, 270, fill=(255, 255, 255, 15), width=2)
    
    # 文字 - 尝试加载中文字体
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    
    fn_bold = fn_reg = fn_small = fn_title = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                fn_title = ImageFont.truetype(fp, 80)
                fn_bold = ImageFont.truetype(fp, 60)
                fn_reg = ImageFont.truetype(fp, 36)
                fn_small = ImageFont.truetype(fp, 26)
                break
            except:
                continue
    
    if not fn_bold:
        fn_bold = fn_reg = fn_small = fn_title = ImageFont.load_default()
    
    # 顶部标签
    label = "AI INSIDER"
    bbox = draw.textbbox((0, 0), label, font=fn_small)
    lw = bbox[2] - bbox[0]
    draw.text(((w - lw) // 2, 50), label, fill=(255, 255, 255, 180), font=fn_small)
    
    # 分隔线
    draw.line([(350, 90), (550, 90)], fill=(255, 255, 255, 100), width=2)
    
    # 主题大标题
    title = "我的AI小管家"
    bbox = draw.textbbox((0, 0), title, font=fn_title)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, 120), title, fill='white', font=fn_title)
    
    # 主题描述
    bbox = draw.textbbox((0, 0), theme['desc'], font=fn_reg)
    dw = bbox[2] - bbox[0]
    draw.text(((w - dw) // 2, 230), theme['desc'], fill='#F0F4F8', font=fn_reg)
    
    # 分隔线
    draw.line([(400, 290), (500, 290)], fill=(255, 255, 255, 80), width=2)
    
    # 日期
    bbox = draw.textbbox((0, 0), date_str, font=fn_small)
    dtw = bbox[2] - bbox[0]
    draw.text(((w - dtw) // 2, 320), date_str, fill='#E8EDF2', font=fn_small)
    
    # 底部主题标签
    bbox = draw.textbbox((0, 0), theme['name'], font=fn_small)
    nw = bbox[2] - bbox[0]
    # 标签背景
    padding = 15
    draw.rounded_rectangle(
        [((w - nw) // 2 - padding, 380), ((w + nw) // 2 + padding, 420)],
        radius=20,
        fill=(255, 255, 255, 30),
        outline=(255, 255, 255, 50)
    )
    draw.text(((w - nw) // 2, 388), theme['name'], fill='white', font=fn_small)
    
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
