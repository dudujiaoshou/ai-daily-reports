#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 AI-Report_*.md 转换为四模块莫兰迪 HTML
"""
import sys, glob, re, markdown
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# ========== 四色莫兰迪主题 ==========
G = {'p':'#6B8E6B','l':'#A8C8A0','bg':'#F4F7F2','tc':'#3A4A3A','ac':'#5A7A5A','mc':'#7A9A7A','r':'#C8DBC4'}
B = {'p':'#6B9EBD','l':'#A8C5D8','bg':'#EEF4F9','tc':'#3A5A7A','ac':'#4A7A9A','mc':'#6A8AAA','r':'#C0D4E4'}
P = {'p':'#C4A0A0','l':'#D4B8B8','bg':'#F9F4F4','tc':'#5A3A3A','ac':'#A08080','mc':'#A08888','r':'#DECECE'}
T = {'p':'#B08060','l':'#D4A574','bg':'#F7F1EB','tc':'#5A3A28','ac':'#8A6040','mc':'#A07850','r':'#E4C8A8'}

def card(t, name, sub, desc):
    return f'''<div style="background:linear-gradient(145deg,{t['p']} 0%,{t['l']} 100%);padding:36px 30px;border-radius:16px;margin-bottom:22px;text-align:center;position:relative;overflow:hidden;">
  <div style="position:absolute;top:-20px;right:-20px;width:100px;height:100px;background:rgba(255,255,255,0.06);border-radius:50%;"></div>
  <div style="position:absolute;bottom:-15px;left:20px;width:60px;height:60px;background:rgba(255,255,255,0.06);border-radius:50%;"></div>
  <p style="font-size:11px;letter-spacing:5px;color:rgba(255,255,255,0.55);margin-bottom:14px;text-transform:uppercase;">AI INSIDER</p>
  <h1 style="color:white;font-size:32px;font-weight:700;margin:0 0 6px 0;letter-spacing:5px;">{name}</h1>
  <p style="color:rgba(255,255,255,0.85);font-size:13px;margin:4px 0;font-weight:300;">{sub}</p>
  <div style="width:32px;height:1.5px;background:rgba(255,255,255,0.35);margin:10px auto;"></div>
  <p style="color:rgba(255,255,255,0.6);font-size:11.5px;margin:4px 0;letter-spacing:0.5px;">{desc}</p>
</div>'''

def div(t, label=''):
    if label:
        return f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 16px 0;"><span style="flex:1;height:1px;background:{t["r"]};"></span><span style="font-size:10px;color:{t["mc"]};letter-spacing:2px;white-space:nowrap;padding:0 8px;">{label}</span><span style="flex:1;height:1px;background:{t["r"]};"></span></div>'
    return f'<div style="height:1px;background:{t["r"]};margin:18px 0;"></div>'

def intro(t, text):
    return f'<div style="padding:14px 18px;background:{t["bg"]};border-radius:10px;margin-bottom:16px;line-height:1.8;font-size:13px;color:{t["tc"]};border-left:3px solid {t["p"]};">{text}</div>'

def item(t, num, title, meta, body_items):
    dot = f'<span style="color:{t["l"]};font-size:10px;margin-right:4px;">·</span>'
    html = f'<div style="margin-bottom:22px;padding-bottom:18px;border-bottom:1px dashed {t["r"]};">'
    html += f'<p style="font-size:11px;color:{t["mc"]};margin:0 0 6px 0;letter-spacing:0.5px;">{num} · {meta}</p>'
    html += f'<h3 style="font-size:15px;font-weight:700;color:{t["tc"]};margin:0 0 10px 0;line-height:1.5;">{title}</h3>'
    for lbl, items in body_items:
        html += f'<p style="margin:8px 0 5px 0;font-weight:600;color:{t["ac"]};font-size:12px;">{dot} {lbl}</p>'
        for it in items:
            html += f'<p style="margin:3px 0 3px 10px;text-indent:-8px;padding-left:8px;line-height:1.75;color:{t["tc"]};font-size:12.5px;">{dot} {it}</p>'
    html += '</div>'
    return html

def reflection(t, text):
    return f'<div style="margin-top:20px;padding:14px 18px;background:{t["bg"]};border-radius:10px;border:1px solid {t["r"]};"><p style="font-size:11px;color:{t["mc"]};margin:0 0 6px 0;letter-spacing:1px;font-weight:600;">💡 人文观察</p><p style="font-size:12.5px;color:{t["tc"]};line-height:1.8;margin:0;font-style:italic;">{text}</p></div>'

def insights(t):
    rows = [
        ('融资趋势', '具身智能+工业AI成资本新宠，国家队基金入场频率提升'),
        ('技术演进', 'AI从"对话助手"升级为"自主执行者"，Vibe Coding加速开发者变革'),
        ('行业格局', 'SpaceX 600亿押注Cursor，AI编程赛道寡头化加速'),
        ('风险提示', '融资泡沫风险累积，"规模繁荣"需警惕商业价值真实性'),
    ]
    html = f'<table style="width:100%;border-collapse:collapse;margin:10px 0;font-size:12.5px;">'
    for i, (dim, finding) in enumerate(rows):
        bg = t["bg"] if i % 2 == 0 else '#fff'
        html += f'<tr><td style="padding:9px 12px;background:{bg};border-left:3px solid {t["p"]};font-weight:bold;color:{t["tc"]};white-space:nowrap;width:28%;">{dim}</td><td style="padding:9px 12px;background:{bg};color:{t["tc"]};line-height:1.6;">{finding}</td></tr>'
    html += '</table>'
    return html

def footer():
    return '''<div style="margin-top:24px;padding:16px 20px;background:#F8F8F8;border-radius:10px;">
  <p style="font-size:11px;color:#999;line-height:1.8;margin:0 0 4px 0;">📅 数据截止：2026年4月24日 19:15 &nbsp;|&nbsp; 🔄 下一期推送：明日 10:00</p>
  <p style="font-size:11px;color:#999;line-height:1.8;margin:0 0 6px 0;">📡 来源：财新 · 36氪 · Reuters · TechCrunch · 福布斯 · AI Product Hub · 国家统计局</p>
  <p style="font-size:10.5px;color:#bbb;line-height:1.6;margin:0;">⚠️ 本日报基于公开信息整理，分析内容仅供参考，不构成投资建议。市场有风险，决策需谨慎。</p>
</div>'''

def parse_md_to_sections(md_content):
    """解析markdown内容为四模块结构"""
    # 简单解析：按标题分割
    sections = []
    current = {'title': '', 'content': []}
    
    for line in md_content.split('\n'):
        if line.startswith('## '):
            if current['title']:
                sections.append(current)
            current = {'title': line[3:].strip(), 'content': []}
        elif line.strip():
            current['content'].append(line)
    
    if current['title']:
        sections.append(current)
    
    return sections

def generate_html(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 解析markdown
    sections = parse_md_to_sections(md_content)
    
    # 分类到四个模块（简化版：根据关键词分类）
    module1 = []  # 星火 - 技术与前沿
    module2 = []  # 深流 - 资本与创业
    module3 = []  # 温渡 - 行业洞察
    module4 = []  # 涟漪 - 活动（如果没有则省略）
    
    for s in sections:
        title = s['title'].lower()
        if any(k in title for k in ['融资', '投资', '收购', '轮', '估值', '资本']):
            module2.append(s)
        elif any(k in title for k in ['活动', '峰会', '大会', '沙龙', '社群']):
            module4.append(s)
        elif any(k in title for k in ['榜单', '数据', '统计', '政策', '洞察', '趋势']):
            module3.append(s)
        else:
            module1.append(s)
    
    # 构建HTML
    html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>我的AI小管家</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif; max-width: 680px; margin: 40px auto; padding: 20px; background: #F5F5F5; }
.content { background: white; padding: 32px 36px; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 20px; }
</style>
</head>
<body>
'''
    
    # 模块一：星火
    if module1:
        html += card(G, '星火', '技术与前沿', '每一条技术的跃进，都在为人类点燃新的可能')
        html += '<div class="content">\n'
        html += intro(G, '🌍 <strong>本期聚焦：</strong>全球AI技术最新突破与产品动态')
        html += div(G)
        for i, s in enumerate(module1[:3], 1):
            content = '\n'.join(s['content'])
            html += item(G, f'{i:02d}', s['title'], '技术动态', [
                ('发生了什么', [content[:200] + '...'] if len(content) > 200 else [content])
            ])
        html += '</div>'
    
    # 模块二：深流
    if module2:
        html += card(B, '深流', '资本与创业', '看懂钱的流向，才能看清未来的方向')
        html += '<div class="content">\n'
        html += intro(B, '💰 <strong>本期聚焦：</strong>AI领域最新融资、收购与资本运作')
        html += div(B)
        for i, s in enumerate(module2[:4], 1):
            content = '\n'.join(s['content'])
            html += item(B, f'{i:02d}', s['title'], '资本运作', [
                ('发生了什么', [content[:200] + '...'] if len(content) > 200 else [content])
            ])
        html += '</div>'
    
    # 模块三：温渡
    if module3:
        html += card(P, '温渡', '行业洞察与社会', '在数据的冷硬之外，看见人的温度')
        html += '<div class="content">\n'
        html += intro(P, '📊 <strong>本期聚焦：</strong>AI行业数据、榜单与深度洞察')
        html += div(P)
        for i, s in enumerate(module3[:3], 1):
            content = '\n'.join(s['content'])
            html += item(P, f'{i:02d}', s['title'], '行业洞察', [
                ('发生了什么', [content[:200] + '...'] if len(content) > 200 else [content])
            ])
        html += div(P)
        html += insights(P)
        html += '</div>'
    
    # 模块四：涟漪（活动）
    if module4:
        html += card(T, '涟漪', '社群与活动', '每一次相遇，都在泛起改变命运的涟漪')
        html += '<div class="content">\n'
        html += intro(T, '🤝 <strong>本期聚焦：</strong>上海AI高质量活动推荐')
        html += div(T, '近期活动')
        for s in module4[:3]:
            content = '\n'.join(s['content'])
            html += f'<div style="margin-bottom:16px;padding:16px 18px;background:{T["bg"]};border-radius:12px;border:1px solid {T["r"]};">'
            html += f'<h4 style="font-size:14px;font-weight:700;color:{T["tc"]};margin:0 0 8px 0;">{s["title"]}</h4>'
            html += f'<p style="font-size:12px;color:{T["ac"]};margin:0;line-height:1.6;">{content[:150]}...</p>'
            html += '</div>'
        html += div(T)
        html += f'<div style="padding:14px 18px;background:{T["bg"]};border-radius:10px;margin-bottom:12px;line-height:1.8;font-size:13px;color:{T["tc"]};border-left:3px solid {T["p"]};">'
        html += '📌 <strong>以上活动详情与报名方式</strong><br>'
        html += '添加下方微信，备注「小管家进群」，获取活动推荐与报名链接'
        html += '</div>'
        html += '</div>'
    
    html += footer()
    html += '''
</body>
</html>'''
    
    return html

def main():
    files = sorted(glob.glob('AI-Report_*.md'))
    if not files:
        print('未找到报告文件')
        sys.exit(1)
    
    latest = files[-1]
    print(f'找到报告: {latest}')
    
    html = generate_html(latest)
    
    with open('preview_draft.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'生成HTML成功: {len(html)} 字符')

if __name__ == '__main__':
    main()
