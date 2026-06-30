import requests
import os
from datetime import datetime

# 从环境变量读取密钥（在GitHub Secrets里设置）
SERVERCHAN_KEY = os.environ.get('SERVERCHAN_KEY', '')

# 监控的股票
STOCKS = [
    "sh600519",  # 贵州茅台
    "sh000001",  # 上证指数
    "sz000001",  # 平安银行
    "sz300750",  # 宁德时代
]

def fetch_data():
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    code_str = ",".join(STOCKS)
    
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f2,f3,f10,f12,f14,f22",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "secids": code_str,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("data") and data["data"].get("diff"):
            alerts = []
            for item in data["data"]["diff"]:
                name = item.get("f14", "")
                price = round(item.get("f2", 0) / 100, 2) if item.get("f2") else 0
                change = round(item.get("f3", 0) / 100, 2) if item.get("f3") else 0
                speed = round(item.get("f22", 0) / 100, 2) if item.get("f22") else 0
                vr = round(item.get("f10", 0) / 100, 2) if item.get("f10") else 0
                
                # 检查异常
                if abs(speed) >= 2.0:
                    alerts.append(f"🚀 {name} 涨速 {speed:+.2f}% (现价{price})")
                if vr >= 3.0:
                    alerts.append(f"📊 {name} 量比 {vr:.2f} (放量)")
                if change <= -5:
                    alerts.append(f"🔴 {name} 大跌 {change:.2f}%")
            
            if alerts:
                content = "\n".join(alerts)
                content += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                send_alert("⚠️ 股票异动", content)
            else:
                print("无异常")
                
    except Exception as e:
        print(f"错误: {e}")

def send_alert(title, content):
    if not SERVERCHAN_KEY:
        print("⚠️ 未配置密钥")
        return
    
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    try:
        requests.post(url, data={"title": title, "desp": content}, timeout=10)
        print(f"✅ 已推送: {title}")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

if __name__ == "__main__":
    fetch_data()
