from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# 从环境变量读取
SENDKEY = os.environ.get('SENDKEY', '')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN', 'default123')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 验证密码
        if request.args.get('token') != SECRET_TOKEN:
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json() or {}
        symbol = data.get('symbol', 'Unknown')
        message = data.get('message', 'No content')
        level = data.get('level', 'INFO')
        
        # 发送到 Server酱
        title = f"{symbol} [{level}]"
        content = f"级别: {level}\n内容: {message}\n时间: {datetime.now().strftime('%H:%M:%S')}"
        
        requests.post(
            "https://sctapi.ftqq.com/" + SENDKEY + ".send",
            data={"title": title, "desp": content},
            timeout=10
        )
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# 健康检查
@app.route('/')
def home():
    return jsonify({"status": "running", "service": "webhook"})

# Vercel 需要这个
if __name__ == '__main__':
    app.run(debug=True)
