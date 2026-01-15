import requests
import json
import os
from datetime import datetime
import streamlit as st

# 配置
# API_KEY = "765d0e02b73f9a975c3ce0fac97c4b82" # 部署时从 secrets 中读取
try:
    API_KEY = st.secrets["api_keys"]["tianapi_key"]
except:
    API_KEY = "765d0e02b73f9a975c3ce0fac97c4b82" # 本地调试时使用硬编码或环境变量
RAW_DATA_PATH = "/home/ubuntu/finance_video_gen/raw_news.json"

def fetch_tianapi(endpoint):
    url = f"https://apis.tianapi.com/{endpoint}/index?key={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        res_json = response.json()
        if res_json.get("code") == 200:
            return res_json.get("result", {}).get("list", [])
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
    return []

def main():
    all_news = []
    
    # 1. 国际新闻
    world_news = fetch_tianapi("world")
    for item in world_news:
        all_news.append({
            "title": item.get("title"),
            "description": item.get("description"),
            "source": "国际新闻",
            "url": item.get("url"),
            "ctime": item.get("ctime")
        })
        
    # 2. 全网热搜
    network_hot = fetch_tianapi("networkhot")
    for item in network_hot:
        all_news.append({
            "title": item.get("word") or item.get("title"),
            "description": item.get("digest") or "",
            "source": "全网热搜",
            "url": item.get("url") or "",
            "ctime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    # 3. 今日头条热搜
    toutiao_hot = fetch_tianapi("toutiaohot")
    for item in toutiao_hot:
        all_news.append({
            "title": item.get("word") or item.get("title"),
            "description": "",
            "source": "今日头条",
            "url": item.get("url") or "",
            "ctime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # 保存原始数据
    with open(RAW_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)
    print(f"Successfully fetched {len(all_news)} news items.")

if __name__ == "__main__":
    main()
