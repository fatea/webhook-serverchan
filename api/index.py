from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# 从环境变量读取配置
SENDKEY = os.environ.get('SENDKEY')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN', 'default-token')  # 访问密码

@app.route('/webhook', methods=['POST'])
def webhook():
    """接收原系统推送，转发到 Server酱"""
    try:
        # 1. 验证 Token（安全必需）
        token = request.args.get('token')
        if token != SECRET_TOKEN:
            return jsonify({"error": "Unauthorized"}), 403
        
        # 2. 获取 JSON 数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data"}), 400
            
        symbol = data.get('symbol', 'Unknown')
        message = data.get('message', 'No message')
        level = data.get('level', 'INFO')
        
        # 3. 推送到 Server酱
        title = f"{symbol} [{level}]"
        desp = f"""**告警级别**: {level}
**详细信息**: {message}
**推送时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**来源**: Webhook Service"""
        
        resp = requests.post(
            f"https://sctapi.ftqq.com/{SENDKEY}.send",
            data={"title": title, "desp": desp},
            timeout=10
        )
        
        return jsonify({
            "status": "success", 
            "message": "Pushed to WeChat",
            "symbol": symbol
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['GET'])
def test():
    """测试接口是否在线"""
    return jsonify({
        "status": "running", 
        "service": "webhook-to-wechat",
        "timestamp": datetime.now().isoformat()
    })

# Vercel 需要这个 handler
def handler(request):
    return app(request.environ, lambda status, headers: None)
