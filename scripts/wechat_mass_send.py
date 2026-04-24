#!/usr/bin/env python3
"""
微信群发脚本 - AI 日报推送
将 AI 日报以图文消息形式推送到微信公众号
"""
import os
import re
import json
import base64
import requests
import markdown
from datetime import datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMaterial, WeChatMessage
from wechatpy.exceptions import WeChatClientException

# 获取凭证
APP_ID = os.environ.get('WX_APPID')
APP_SECRET = os.environ.get('WX_APPSECRET')
REPORT_PATTERN = 'AI-Report_*.md'

def get_access_token():
    """获取微信 access_token"""
    url = f'https://api.weixin.qq.com/cgi-bin/token'
    params = {
        'grant_type': 'client_credential',
        'appid': APP_ID,
        'secret': APP_SECRET
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if 'access_token' in data:
        return data['access_token']
    else:
        raise Exception(f"获取 access_token 失败: {data}")

def markdown_to_html(md_content, title):
    """将 Markdown 转换为 HTML"""
    # 转换 markdown 为 HTML
    html_body = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'nl2br']
    )
    
    # 构建完整 HTML
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
            color: #333;
        }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #1890ff; padding-bottom: 10px; }}
        h2 {{ color: #1890ff; margin-top: 30px; }}
        h3 {{ color: #333; }}
        p {{ margin: 15px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #f5f5f5; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #1890ff; margin: 15px 0; padding: 10px 15px; background: #f9f9f9; }}
        strong {{ color: #e67e22; }}
        .header {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #eee;
            margin-bottom: 30px;
        }}
        .timestamp {{
            color: #999;
            font-size: 14px;
        }}
        li {{ margin: 8px 0; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    {html_body}
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px; text-align: center;">
        <p>由 AI 日报自动生成系统推送</p>
    </div>
</body>
</html>'''
    return html

def get_latest_report():
    """获取最新的日报文件"""
    import glob
    files = sorted(glob.glob(REPORT_PATTERN))
    if not files:
        return None, None
    latest = files[-1]
    with open(latest, 'r', encoding='utf-8') as f:
        content = f.read()
    return latest, content

def upload_thumb_image(access_token):
    """上传封面图片"""
    # 创建一个简单的蓝色渐变图片作为封面
    import io
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (900, 500), color='#1890ff')
    draw = ImageDraw.Draw(img)
    
    # 添加渐变效果
    for i in range(500):
        alpha = int(255 * (1 - i / 500))
        color = (24, 144, 255, alpha)
    
    # 保存到内存
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'
    files = {'media': ('cover.png', img_bytes, 'image/png')}
    resp = requests.post(url, files=files)
    data = resp.json()
    
    if 'media_id' in data:
        return data['media_id']
    else:
        print(f"上传封面失败: {data}")
        return None

def create_news_article(access_token, title, html_content, thumb_media_id):
    """创建图文消息"""
    url = f'https://api.weixin.qq.com/cgi-bin/media/uploadnews?access_token={access_token}'
    
    articles = [{
        'title': title,
        'thumb_media_id': thumb_media_id,
        'author': 'AI 日报系统',
        'digest': html_content[:100] + '...',
        'show_cover_pic': 1,
        'content': html_content,
        'content_source_url': ''
    }]
    
    data = {'articles': articles}
    resp = requests.post(url, json=data)
    result = resp.json()
    
    if 'media_id' in result:
        return result['media_id']
    else:
        raise Exception(f"创建图文消息失败: {result}")

def mass_send(access_token, media_id):
    """群发消息"""
    url = f'https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}'
    
    data = {
        'filter': {
            'is_to_all': True,  # 发送给所有用户
            'tag_id': 0
        },
        'msgtype': 'mpnews',
        'mpnews': {
            'media_id': media_id
        }
    }
    
    resp = requests.post(url, json=data)
    result = resp.json()
    return result

def main():
    print("=" * 50)
    print("微信群发 - AI 日报推送")
    print("=" * 50)
    
    # 检查凭证
    if not APP_ID or not APP_SECRET:
        print("错误: 未设置 WX_APPID 或 WX_APPSECRET 环境变量")
        return
    
    print(f"AppID: {APP_ID}")
    
    # 1. 获取最新报告
    filename, content = get_latest_report()
    if not filename:
        print("错误: 未找到 AI 日报文件")
        return
    
    print(f"找到报告: {filename}")
    
    # 2. 生成标题
    now = datetime.now()
    is_pm = now.hour >= 12
    report_type = "晚间版" if is_pm else "早间版"
    title = f"🤖 AI 日报 | {report_type} {now.strftime('%m/%d')}"
    
    # 3. 转换为 HTML
    print("转换 Markdown 为 HTML...")
    html_content = markdown_to_html(content, title)
    print(f"HTML 长度: {len(html_content)} 字符")
    
    # 4. 获取 access_token
    print("获取 access_token...")
    try:
        access_token = get_access_token()
        print(f"access_token 获取成功")
    except Exception as e:
        print(f"获取 access_token 失败: {e}")
        return
    
    # 5. 上传封面图片
    print("上传封面图片...")
    thumb_media_id = upload_thumb_image(access_token)
    if not thumb_media_id:
        print("警告: 封面上传失败，使用默认封面")
        thumb_media_id = ""  # 使用空字符串，微信会使用默认封面
    
    # 6. 创建图文消息
    print("创建图文消息...")
    try:
        media_id = create_news_article(access_token, title, html_content, thumb_media_id)
        print(f"图文消息创建成功, media_id: {media_id}")
    except Exception as e:
        print(f"创建图文消息失败: {e}")
        return
    
    # 7. 群发
    print("执行群发...")
    result = mass_send(access_token, media_id)
    
    print("\n" + "=" * 50)
    print("群发结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get('errcode') == 0:
        print("\n✅ 群发成功！")
        print(f"msg_id: {result.get('msg_id')}")
    else:
        print(f"\n❌ 群发失败: {result.get('errmsg')}")
        
        # 常见错误处理
        errcode = result.get('errcode')
        if errcode == 40001:
            print("提示: access_token 无效或已过期")
        elif errcode == 48001:
            print("提示: 你的公众号没有群发权限（个人订阅号可能受限）")
        elif errcode == -1:
            print("提示: 系统繁忙，请稍后重试")
    
    print("=" * 50)

if __name__ == '__main__':
    main()
