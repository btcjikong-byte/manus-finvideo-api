import re
import os
import asyncio
from openai import OpenAI

client = OpenAI()

def parse_script_to_scenes(script_text):
    """
    将脚本解析为场景。
    逻辑：按段落拆分，并尝试提取配图建议。
    """
    scenes = []
    # 移除标题矩阵部分，只保留正文
    print(f"[DEBUG] parse_script_to_scenes received script_text length: {len(script_text)}")
    # 移除标题矩阵部分，只保留正文
    # 查找“### 标题矩阵”和“### 正文”之间的内容，并将其移除
    title_matrix_match = re.search(r'(### 标题矩阵.*?)(#+ 正文|#+ 脚本正文)', script_text, re.DOTALL | re.IGNORECASE)
    if title_matrix_match:
        script_text_cleaned = script_text[:title_matrix_match.start(1)] + script_text[title_matrix_match.end(1):]
        print("[DEBUG] Removed title matrix section.")
    else:
        script_text_cleaned = script_text
        print("[DEBUG] No title matrix section found.")

    body = re.split(r'#+ 正文|#+ 脚本正文', script_text_cleaned, flags=re.I)[-1]
    print(f"[DEBUG] Script body length after splitting: {len(body)}")
    
    # 按段落拆分
    paragraphs = [p.strip() for p in body.split('\n') if p.strip()]
    
    for i, p in enumerate(paragraphs):
        # 提取配图建议（如果有）
        image_suggestion = ""
        suggestion_match = re.search(r'\(配图建议[：:](.*?)\)', p)
        if suggestion_match:
            image_suggestion = suggestion_match.group(1).strip()
            # 清洗文案，移除配图建议
            p = re.sub(r'\(配图建议[：:].*?\)', '', p).strip()
        
        if p:
            scenes.append({
                "id": i + 1,
                "content": p,
                "image_suggestion": image_suggestion or f"财经视频场景：{p[:30]}",
                "image_url": None,
                "audio_path": None
            })
    return scenes

def generate_audio(text, voice_sample_path=None):
    """
    模拟配音生成。
    由于环境限制，此处仅返回模拟路径。
    """
    return f"/home/ubuntu/finance_video_gen/temp_video/audio_{hash(text)}.mp3"

def generate_image(prompt):
    """
    调用 DALL-E 3 生成配图。
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Professional financial news illustration, 16:9 aspect ratio, high quality, modern style: {prompt}",
            n=1,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        print(f"[ERROR] Error generating image: {e}")
        return "https://via.placeholder.com/1024x576.png?text=Image+Generation+Failed"

def assemble_video(scenes, bgm_style="激昂"):
    """
    模拟视频合成。
    """
    print("[DEBUG] Assembling video (simulated).")
    return "/home/ubuntu/finance_video_gen/temp_video/final_video.mp4"
