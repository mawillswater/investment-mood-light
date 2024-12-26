import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
import requests
import random
import time
from datetime import datetime

load_dotenv()  # 加载 .env 文件
API_KEY = os.getenv('COINGECKO_API_KEY')

app = Flask(__name__)

# 投资名言列表
INVESTMENT_QUOTES = [
    "不要因为短期波动失去长期视角。 - 巴菲特",
    "市场先生时而理性，时而疯狂。 - 本杰明·格雷厄姆",
    "投资最重要的是控制风险。 - 彼得·林奇",
    "耐心是投资者最重要的美德。 - 查理·芒格",
    "市场总是周期性的，保持冷静很重要。 - 约翰·博格"
]

# 缓存机制
last_update = None
cached_data = None
CACHE_DURATION = 110  # 缓存110秒

def get_btc_price():
    """获取BTC价格数据的函数"""
    response = requests.get(
        'https://api.coingecko.com/api/v3/simple/price',
        params={
            'ids': 'bitcoin',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'x_cg_demo_api_key': API_KEY
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.text}")
        
    data = response.json()
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] 获取新数据: {data}")  # 调试信息
    
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_btc_mood')
def get_btc_mood():
    global last_update, cached_data
    
    try:
        current_time = time.time()
        force_refresh = request.args.get('force', '0') == '1'
        
        # 检查缓存状态
        cache_age = current_time - last_update if last_update else float('inf')
        print(f"缓存年龄: {cache_age:.1f}秒")  # 调试信息
        
        # 如果强制刷新或缓存过期，获取新数据
        if force_refresh or not cached_data or cache_age >= CACHE_DURATION:
            print("获取新数据...")  # 调试信息
            data = get_btc_price()
            
            if 'bitcoin' not in data:
                raise Exception("未能获取到比特币数据")
                
            current_price = data['bitcoin']['usd']
            price_change_24h = data['bitcoin']['usd_24h_change']
            
            # 根据24小时涨跌幅决定颜色和消息
            if price_change_24h >= 5:
                color = "#FF3333"  # 更鲜艳的红色
                message = f"BTC大幅上涨 {price_change_24h:.2f}%，保持冷静，避免FOMO"
            elif price_change_24h >= 2:
                color = "#FF8C69"  # 更鲜艳的浅红色
                message = f"BTC上涨 {price_change_24h:.2f}%，适度谨慎，注意风险"
            elif price_change_24h <= -5:
                color = "#32CD32"  # 更鲜艳的绿色
                message = f"BTC大跌 {price_change_24h:.2f}%，市场恐慌，可能是机会"
            elif price_change_24h <= -2:
                color = "#98FB98"  # 更鲜艳的浅绿色
                message = f"BTC下跌 {price_change_24h:.2f}%，保持关注，理性评估"
            else:
                color = "#87CEFA"  # 更鲜艳的淡蓝色
                message = f"BTC波动 {price_change_24h:.2f}%，市场平稳，保持正常操作"
            
            # 随机选择一句投资名言
            quote = random.choice(INVESTMENT_QUOTES)
            
            # 更新缓存
            cached_data = {
                'color': color,
                'message': message,
                'quote': quote,
                'price': f"当前BTC价格: ${current_price:,.2f}",
                'change': f"24小时涨跌幅: {price_change_24h:.2f}%",
                'timestamp': current_time,
                'cache_info': '新数据'
            }
            last_update = current_time
            print("缓存已更新")  # 调试信息
        else:
            print("使用缓存数据")  # 调试信息
            cached_data['cache_info'] = '缓存数据'
        
        return jsonify(cached_data)
    
    except Exception as e:
        print(f"错误详情: {str(e)}")  # 在服务器端打印错误信息
        return jsonify({
            'error': str(e),
            'color': "#F0F8FF",
            'message': f"获取数据失败: {str(e)}",
            'quote': random.choice(INVESTMENT_QUOTES)
        })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
