import pandas as pd
import openai
from time import sleep
import os
from dotenv import load_dotenv
import requests
import json

# 加载环境变量
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = "https://api.duckagi.com/v1/chat/completions"

def get_ai_response(query):
    try:
        # 设置请求头和数据
        headers = {
            'Content-Type': 'application/json',
            # 移除 Bearer 前缀，直接使用 API 密钥
            'Authorization': 'sk-er4f1fz6L7RshYw7qWnhP0e9HKlA8fROH1fodG9VA1hk5EgC'
        }
        
        # 添加调试信息
        print("使用的 API 密钥:", API_KEY)
        print("发送请求到:", API_BASE)
        
        # 修改请求数据格式
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "你是一个永远愤怒的怼人狂魔"},
                {"role": "user", "content": f"请你用永远愤怒的怼人狂魔的语气回答这个问题：{query}"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000  # 添加最大令牌数
        }
        
        # 打印完整请求数据用于调试
        print("请求数据:", json.dumps(data, ensure_ascii=False, indent=2))
        
        # 发送请求
        response = requests.post(
            API_BASE,
            headers=headers,
            json=data,
            timeout=30
        )
        
        # 打印响应状态和内容用于调试
        print("响应状态码:", response.status_code)
        print("响应内容:", response.text)
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.Timeout:
        print("请求超时，正在重试...")
        sleep(2)  # 等待2秒后重试
        return get_ai_response(query)  # 递归重试
    except Exception as e:
        print(f"处理查询时出错: {str(e)}")
        return "处理出错"

def main():
    # 读取Excel文件
    try:
        df = pd.read_excel('input.xlsx')  # 替换为你的Excel文件名
        
        # 遍历A列的每一行
        for index, row in df.iterrows():
            query = row['A']  # 假设A列的标题是'A'
            
            # 获取AI回答
            response = get_ai_response(query)
            
            # 将回答写入B列
            df.at[index, 'B'] = response
            
            # 每次请求后暂停1秒，避免超过API限制
            sleep(1)
            
            # 打印进度
            print(f"已处理 {index + 1}/{len(df)} 行")
            
            # 每处理10行保存一次
            if (index + 1) % 10 == 0:
                df.to_excel('output.xlsx', index=False)
                print("已保存进度")
        
        # 最后保存整个文件
        df.to_excel('output.xlsx', index=False)
        print("处理完成！")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main() 