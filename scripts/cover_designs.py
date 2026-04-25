"""
AI日报创意封面设计库
每天轮换不同风格，告别千篇一律
"""

import random
from datetime import datetime

# 封面风格库 - 每天随机轮换
COVER_STYLES = {
    'neural_network': {
        'name': '神经网络',
        'desc': '连接未来的每一根神经元',
        'bg_type': 'neural',
        'colors': ['#0a0e27', '#1a1f4b', '#2d3561'],
        'accent': '#00d4ff',
        'elements': 'nodes_lines'
    },
    'gradient_mesh': {
        'name': '渐变网格',
        'desc': '在色彩的流动中看见趋势',
        'bg_type': 'mesh',
        'colors': ['#ff006e', '#8338ec', '#3a86ff'],
        'accent': '#ffbe0b',
        'elements': 'waves'
    },
    'particles': {
        'name': '粒子星空',
        'desc': '每一个数据点都是一颗星',
        'bg_type': 'particles',
        'colors': ['#000428', '#004e92', '#000428'],
        'accent': '#ffffff',
        'elements': 'stars'
    },
    'glassmorphism': {
        'name': '玻璃拟态',
        'desc': '透明背后的无限可能',
        'bg_type': 'glass',
        'colors': ['#667eea', '#764ba2', '#f093fb'],
        'accent': '#ffffff',
        'elements': 'cards'
    },
    'circuit': {
        'name': '电路脉络',
        'desc': '电流涌动，智能觉醒',
        'bg_type': 'circuit',
        'colors': ['#0f2027', '#203a43', '#2c5364'],
        'accent': '#00ff88',
        'elements': 'traces'
    },
    'aurora': {
        'name': '极光幻境',
        'desc': '科技如极光般绚烂',
        'bg_type': 'aurora',
        'colors': ['#1a1a2e', '#16213e', '#0f3460'],
        'accent': '#e94560',
        'elements': 'ribbons'
    },
    'matrix': {
        'name': '矩阵代码',
        'desc': '0和1构建的新世界',
        'bg_type': 'matrix',
        'colors': ['#000000', '#0d2818', '#051f0d'],
        'accent': '#00ff41',
        'elements': 'code_rain'
    },
    'hologram': {
        'name': '全息投影',
        'desc': '虚实交织的智能时代',
        'bg_type': 'hologram',
        'colors': ['#0c0c1d', '#1a1a3e', '#2d2d5a'],
        'accent': '#00ffff',
        'elements': 'grid_floor'
    },
    'data_viz': {
        'name': '数据可视化',
        'desc': '让数据自己说话',
        'bg_type': 'dataviz',
        'colors': ['#1e3c72', '#2a5298', '#7e8ba3'],
        'accent': '#ffd700',
        'elements': 'charts'
    },
    'isometric': {
        'name': '等距世界',
        'desc': '多维视角看AI',
        'bg_type': 'isometric',
        'colors': ['#232526', '#414345', '#232526'],
        'accent': '#ff6b6b',
        'elements': 'cubes'
    }
}

def get_daily_style():
    """获取今天的封面风格 - 基于日期确定，确保每天不同"""
    day_of_year = datetime.now().timetuple().tm_yday
    style_keys = list(COVER_STYLES.keys())
    # 根据一年中的第几天选择风格，确保每天不同
    style_key = style_keys[day_of_year % len(style_keys)]
    return style_key, COVER_STYLES[style_key]

def get_theme_style(content_theme):
    """根据内容主题获取风格"""
    theme_mapping = {
        'funding': ['gradient_mesh', 'data_viz', 'glassmorphism'],
        'robot': ['circuit', 'isometric', 'hologram'],
        'model': ['neural_network', 'aurora', 'particles'],
        'coding': ['matrix', 'circuit', 'data_viz'],
        'policy': ['glassmorphism', 'data_viz', 'isometric'],
        'default': ['neural_network', 'particles', 'aurora', 'gradient_mesh']
    }
    
    candidates = theme_mapping.get(content_theme, theme_mapping['default'])
    # 基于日期选择，确保同一主题也有变化
    day_of_year = datetime.now().timetuple().tm_yday
    return candidates[day_of_year % len(candidates)]
