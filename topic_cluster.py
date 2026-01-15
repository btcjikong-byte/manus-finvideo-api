import json
import os
import re
import streamlit as st
from openai import OpenAI
from datetime import datetime

# 优先从 Streamlit Secrets 或环境变量中读取 API 密钥
try:
    openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    client = OpenAI()

# 使用相对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "raw_news.json")
DAILY_TOPICS_PATH = os.path.join(BASE_DIR, "daily_topics.json")
HISTORY_TOPICS_PATH = os.path.join(BASE_DIR, "history_topics.json")

def cluster_topics(news_items):
    """
    使用 LLM 对新闻进行聚类并生成选题。
    """
    if not news_items:
        return []
    
    # 简化输入，只取前 50 条新闻以节省 token
    news_summary = "\n".join([f"- {item['title']} ({item['source']})" for item in news_items[:50]])
    
    prompt = f"""
    你是一个资深的财经短视频编导。请根据以下最新的新闻资讯，聚类出 8-10 个最适合做短视频的选题大方向。请确保至少一半的选题与金融、股市、宏观经济等财经领域强相关。
    
    要求：
    1. 每个大方向要有一个核心主题（Topic）。
    2. 每个大方向下要包含 3-4 个具体的子选题/视频标题。
    3. 为每个大方向预估一个热力值（10000-99999）。
    4. 严格按照以下 JSON 格式输出：
    [
        {{
            "topic": "大方向名称",
            "heat": 98500,
            "news_items": [
                {{"title": "子选题1", "url": "原文链接"}},
                {{"title": "子选题2", "url": "原文链接"}}
            ]
        }}
    ]
    
    新闻资讯：
    {news_summary}
    """
    
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        # 尝试提取 JSON
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            result = json.loads(content)
        if isinstance(result, dict) and "topics" in result:
            return result["topics"]
        elif isinstance(result, dict):
            # 有些模型可能直接返回列表作为值的字典
            for key in result:
                if isinstance(result[key], list):
                    return result[key]
        return result if isinstance(result, list) else []
    except Exception as e:
        print(f"Error clustering topics: {e}")
        return []

def main():
    if not os.path.exists(RAW_DATA_PATH):
        print("Raw news data not found.")
        return
        
    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        news_items = json.load(f)
        
    new_topics = cluster_topics(news_items)
    
    if new_topics:
        # 1. 更新今日选题
        with open(DAILY_TOPICS_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_topics, f, ensure_ascii=False, indent=4)
            
        # 2. 归档到历史选题
        today = datetime.now().strftime("%Y-%m-%d")
        history = {}
        if os.path.exists(HISTORY_TOPICS_PATH):
            try:
                with open(HISTORY_TOPICS_PATH, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = {}
        
        history[today] = new_topics
        with open(HISTORY_TOPICS_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully clustered {len(new_topics)} topics.")
    else:
        print("No topics generated.")

if __name__ == "__main__":
    main()
