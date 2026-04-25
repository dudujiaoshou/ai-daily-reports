import requests, sys, os
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

def check_recent_run():
    """检查最近24小时内是否有成功运行"""
    token = os.environ.get('GH_TOKEN', '')
    if not token:
        print("❌ 未设置 GH_TOKEN")
        return False
    
    headers = {'Authorization': f'token {token}'}
    url = 'https://api.github.com/repos/dudujiaoshou/ai-daily-reports/actions/runs?per_page=5'
    
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ API请求失败: {resp.status_code}")
        return False
    
    data = resp.json()
    runs = data.get('workflow_runs', [])
    
    if not runs:
        print("⚠️ 没有找到最近的运行记录")
        return False
    
    latest = runs[0]
    status = latest.get('status')
    conclusion = latest.get('conclusion')
    created_at = latest.get('created_at', '')
    
    # 检查是否是24小时内的
    run_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    now = datetime.now(run_time.tzinfo)
    
    if (now - run_time) > timedelta(hours=24):
        print(f"⚠️ 最近运行超过24小时: {created_at}")
        return False
    
    if conclusion == 'success':
        print(f"✅ 最近运行成功: {created_at}")
        return True
    else:
        print(f"❌ 最近运行失败: {conclusion} ({created_at})")
        print(f"   运行URL: {latest.get('html_url', '')}")
        return False

if __name__ == '__main__':
    success = check_recent_run()
    sys.exit(0 if success else 1)
