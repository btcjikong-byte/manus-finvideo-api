import os
from openai import OpenAI

client = OpenAI()

def analyze_multi_styles(samples):
    """
    使用 GPT-4o 对多个样本文稿进行交叉分析，提取共性基因
    """
    samples_text = ""
    for i, s in enumerate(samples):
        if s.strip():
            samples_text += f"--- 样本 {i+1} ---\n{s}\n\n"
    
    prompt = f"""
    你是一位顶级的自媒体内容分析专家。请深度分析以下多份样本文稿，并提取该博主的“核心风格基因”。
    
    【样本文稿集】：
    {samples_text}
    
    请通过交叉比对，提取出该博主最本质的共性特征（总字数 300 字以内）：
    1. 核心语感（如：激进、专业、亲和、毒舌等）
    2. 常用句式（如：爱用反问、多用短句、喜欢列举数据等）
    3. 叙事逻辑（如：先抑后扬、剥洋葱式拆解、故事驱动等）
    4. 标志性口头禅或固定开场/结尾方式
    
    【负面约束】
    明确禁止提取和鼓励任何低俗、套路化的口癖（如：老铁、扒拉、干货等）。
    
    请直接输出风格描述，确保描述精准且具有可操作性。
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini", # 路由至 GPT-4o
            messages=[
                {"role": "system", "content": "你是一个专业的自媒体风格分析师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"风格分析失败: {str(e)}"

def generate_script(topic_name, subtopic_name, style_name, style_desc, context_news, sop_template=""):
    """
    使用 Gemini 2.5 Flash 生成深度长文稿，支持 SOP 约束
    """
    news_context = ""
    for idx, news in enumerate(context_news):
        news_context += f"素材{idx+1}: {news.get('title')}\n内容摘要: {news.get('summary', '暂无摘要')}\n\n"

    sop_instruction = f"\n### 强制 SOP 结构约束\n请严格按照以下结构进行创作：\n{sop_template}" if sop_template else ""

    prompt = f"""
    你是一位拥有百万粉丝的资深财经/科技短视频博主。请直接切入主题，基于以下素材，创作一份时长为 3-5 分钟（约 1500-2500 字）的深度视频脚本。严禁任何形式的开场寒暄，如“好的”、“没问题”等。
    
    ### 核心选题
    - 大方向：{topic_name}
    - 具体子选题：{subtopic_name}
    - 创作风格：{style_name}
    - 风格基因描述：{style_desc}
    {sop_instruction}
    
    ### 背景素材
    {news_context}
    
    ### 创作要求
    1. **标题矩阵（必须包含以下五种风格，且每种风格都要有[长标题]和[短标题]）**：
       - 深度追问风、全球视野风、利益相关风、情绪共鸣风、犀利吐槽风。
       - 格式必须严格为：风格名: [长标题] xxx [短标题] xxx
    2. **文稿结构**：
       - 黄金 3 秒开场：爆点、数据或反直觉观点。
       - 多维深度拆解：底层逻辑、行业趋势、全球影响。
       - 口语化表达：模仿风格基因中的句式和语感。
    3. **标准化结尾**：
       - 必须包含【本视频文稿特点】模块，总结创作逻辑、情绪钩子、核心价值点。
    4. **绝对禁令**：
       - 严禁出现“各位老铁”、“扒拉点硬核干货”、“小爆姐”等低俗、套路化的开场白。
       - 严禁出现任何 AI 痕迹明显的套话。
    
    请直接输出 Markdown 格式，确保字数充足，逻辑严密。
    """

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "你是一个擅长长视频创作的财经视频编导。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"文稿生成失败: {str(e)}"
