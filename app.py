import streamlit as st
import json
import os
import asyncio
import re
from datetime import datetime
from docx import Document
from editor_generate import generate_script, analyze_multi_styles
from video_utils import parse_script_to_scenes, generate_audio, generate_image, assemble_video

# 配置 - 使用相对路径以兼容云端部署
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DAILY_TOPICS_PATH = os.path.join(BASE_DIR, "daily_topics.json")
HISTORY_TOPICS_PATH = os.path.join(BASE_DIR, "history_topics.json")
EDITOR_OUTPUT_PATH = os.path.join(BASE_DIR, "editor_output.json")
STYLES_PATH = os.path.join(BASE_DIR, "blogger_styles.json")
VIDEO_TEMP_DIR = os.path.join(BASE_DIR, "temp_video")
VIDEO_FACTORY_STATE_PATH = os.path.join(BASE_DIR, "video_factory_state.json")

os.makedirs(VIDEO_TEMP_DIR, exist_ok=True)

st.set_page_config(page_title="财经Alpha - 智能视频工厂", layout="wide", initial_sidebar_state="expanded")

# 自定义 CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #eee; }
    .logo-container { display: flex; align-items: center; margin-bottom: 20px; }
    .logo-icon { background-color: #e63946; color: white; width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.1rem; margin-right: 10px; }
    .logo-text { font-size: 1.3rem; font-weight: bold; color: #1a1a1a; }
    .style-card { background: white; border: 1px solid #eee; border-radius: 12px; padding: 20px; margin-bottom: 15px; transition: all 0.3s; }
    .style-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: #e63946; }
    .style-badge { background: #fff5f5; color: #e63946; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
    .video-step { background: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 5px solid #e63946; }
    .script-card { background: white; border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    .scene-card { background: white; border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    .annotation-badge { background: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 5px; }
    </style>
""", unsafe_allow_html=True)

def load_json(path, default={}):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content: return default
                return json.loads(content)
        except: return default
    return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def parse_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# 初始化状态
if 'generated_script' not in st.session_state: st.session_state.generated_script = ""
if 'temp_style_desc' not in st.session_state: st.session_state.temp_style_desc = ""
if 'sample_count' not in st.session_state: st.session_state.sample_count = 3
if 'video_scenes' not in st.session_state: st.session_state.video_scenes = []
if 'selected_title' not in st.session_state: st.session_state.selected_title = ""
if 'video_factory_scripts' not in st.session_state: st.session_state.video_factory_scripts = {}
if 'current_video_factory_script_id' not in st.session_state: st.session_state.current_video_factory_script_id = None

# 侧边栏
with st.sidebar:
    st.markdown('<div class="logo-container"><div class="logo-icon">α</div><div class="logo-text">财经Alpha</div></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#e63946; font-size:1.1rem;'>今日热榜</h3>", unsafe_allow_html=True)
    raw_topics = load_json(DAILY_TOPICS_PATH, default=[])
    topics_data = [t for t in raw_topics if t.get('topic') and str(t.get('topic')).strip().lower() != 'none']
    for i, t in enumerate(topics_data[:10]):
        st.markdown(f'<div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #f0f0f0; font-size:0.9rem;"><span style="color:#e63946; font-weight:bold; margin-right:10px;">{i+1}</span><span style="flex:1;">{t.get("topic")}</span><span style="color:#999;">🔥{t.get("heat")}</span></div>', unsafe_allow_html=True)
    if st.button("🔄 刷新全网数据", use_container_width=True):
        with st.spinner("正在抓取全网热点..."):
            os.system("cd /home/ubuntu/finance_video_gen && venv/bin/python3 news_fetcher.py && venv/bin/python3 topic_cluster.py")
            st.rerun()

# 主界面
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔴 今日热榜", "📜 历史选题", "✍️ 脚本生成", "🧪 风格实验室", "🎬 视频工厂", "📂 文稿库"])

with tab1:
    if topics_data:
        for i in range(0, len(topics_data), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(topics_data):
                    t = topics_data[i + j]
                    letter_id = chr(65 + (i + j))
                    with cols[j]:
                        sub_html = "".join([f'<div style="padding:5px 0; border-bottom:1px dashed #eee; font-size:0.85rem;"><a href="{s.get("url","#")}" target="_blank" style="text-decoration:none; color:#444;">{idx+1}. {s.get("title")[:25]}...</a></div>' for idx, s in enumerate(t.get('news_items', [])[:4])])
                        st.markdown(f'<div style="background:white; border:1px solid #eee; border-radius:8px; padding:15px; min-height:280px;"><div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#e63946; font-weight:bold;">{letter_id}</span><span style="color:#e63946; font-size:0.8rem;">🔥{t.get("heat")}</span></div><div style="font-weight:bold; margin-bottom:10px; font-size:0.95rem;">{t.get("topic")}</div>{sub_html}</div>', unsafe_allow_html=True)

with tab2:
    history = load_json(HISTORY_TOPICS_PATH, default={})
    if not history:
        st.info("暂无历史选题数据。")
    else:
        for date, day_topics in sorted(history.items(), reverse=True):
            with st.expander(f"📅 {date}"):
                if isinstance(day_topics, list):
                    for t in day_topics: 
                        if isinstance(t, dict) and t.get('topic') and str(t.get('topic')).lower() != 'none':
                            st.markdown(f"- **{t.get('topic')}** (🔥 {t.get('heat')})")

with tab3:
    if not topics_data: st.warning("请先刷新数据。")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("创作配置")
            sel_topic = st.selectbox("选择大方向", [t.get('topic') for t in topics_data])
            t_data = next((t for t in topics_data if t.get('topic') == sel_topic), None)
            sel_sub = st.selectbox("选择具体子选题", [n.get('title') for n in t_data.get('news_items', [])] if t_data else [])
            styles = load_json(STYLES_PATH, default={})
            style_names = ["专业分析风", "快节奏口播风", "幽默吐槽风"] + list(styles.keys())
            sel_style = st.selectbox("选择创作风格", style_names)
            sop_template = styles.get(sel_style, {}).get('sop_template', "") if isinstance(styles.get(sel_style), dict) else ""
            
            if st.button("🚀 立即生成深度脚本", use_container_width=True):
                with st.spinner("Gemini 2.5 Flash 正在深度创作..."):
                    s_desc = styles.get(sel_style, {}).get('description', "口语化、深度分析") if isinstance(styles.get(sel_style), dict) else "口语化、深度分析"
                    script = generate_script(sel_topic, sel_sub, sel_style, s_desc, t_data.get('news_items', []), sop_template)
                    st.session_state.generated_script = script
                    lib = load_json(EDITOR_OUTPUT_PATH, default=[])
                    if not isinstance(lib, list): lib = []
                    lib.append({
                        "id": len(lib) + 1,
                        "topic": sel_topic,
                        "subtopic": sel_sub,
                        "style": sel_style,
                        "content": script,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    save_json(EDITOR_OUTPUT_PATH, lib)
                    st.rerun()
            
            if st.session_state.generated_script:
                st.markdown("---")
                st.subheader("🎬 同步至视频工厂")
                
                # 增强的标题解析逻辑
                titles = []
                script_content = st.session_state.generated_script
                if "### 标题矩阵" in script_content:
                    title_section = script_content.split("### 标题矩阵")[1].split("###")[0]
                    # 匹配包含"标题"字样的行，或者匹配 [长标题] [短标题] 格式
                    lines = [l.strip() for l in title_section.split("\n") if l.strip()]
                    for line in lines:
                        if any(keyword in line for keyword in ["标题", "风", "：", ":"]):
                            # 清理 Markdown 符号
                            clean_line = re.sub(r'^[\*\-\d\.\s]+', '', line).strip()
                            if clean_line: titles.append(clean_line)
                
                # 兜底逻辑：如果解析失败，尝试从全文匹配标题格式
                if not titles:
                    titles = re.findall(r'.*标题.*[:：].+', script_content)
                
                if titles:
                    st.session_state.selected_title = st.selectbox("请先选择一个视频标题", titles)
                    if st.button("确认并同步到视频工厂", use_container_width=True):
                        with st.spinner("正在深度解析脚本并构建视频场景..."):
                            st.session_state.video_scenes = parse_script_to_scenes(st.session_state.generated_script)
                            # 保存到视频工厂状态
                            factory_state = load_json(VIDEO_FACTORY_STATE_PATH, default={})
                            script_id = str(datetime.now().timestamp())
                            factory_state[script_id] = {
                                "title": st.session_state.selected_title,
                                "scenes": st.session_state.video_scenes,
                                "original_script": st.session_state.generated_script,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_json(VIDEO_FACTORY_STATE_PATH, factory_state)
                            st.session_state.current_video_factory_script_id = script_id
                            st.success("同步成功！请前往【视频工厂】。")
                else:
                    st.warning("未在脚本中检测到标准标题矩阵。")
                    # 允许用户在没有标题矩阵时也同步，但使用默认标题
                    if st.button("强制同步 (使用默认标题)", use_container_width=True):
                        st.session_state.selected_title = sel_sub
                        with st.spinner("正在解析脚本并构建视频场景..."):
                            st.session_state.video_scenes = parse_script_to_scenes(st.session_state.generated_script)
                            factory_state = load_json(VIDEO_FACTORY_STATE_PATH, default={})
                            script_id = str(datetime.now().timestamp())
                            factory_state[script_id] = {
                                "title": st.session_state.selected_title,
                                "scenes": st.session_state.video_scenes,
                                "original_script": st.session_state.generated_script,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_json(VIDEO_FACTORY_STATE_PATH, factory_state)
                            st.session_state.current_video_factory_script_id = script_id
                            st.success("同步成功！")
        
        with c2:
            if st.session_state.generated_script:
                st.subheader("生成的脚本内容")
                # 移除可能存在的"脚本预览"字样（如果 AI 输出了的话）
                display_content = st.session_state.generated_script.replace("脚本预览", "").strip()
                st.markdown(display_content)
            else:
                st.info("配置完成后点击生成，脚本内容将在此处展示。")

with tab4:
    st.header("🧪 博主风格克隆中心")
    styles = load_json(STYLES_PATH, default={})
    col_train, col_list = st.columns([3, 2])
    with col_train:
        st.subheader("第一步：海量样本喂料")
        new_style_name = st.text_input("博主/风格名称", placeholder="例如：卢克文、半佛仙人...")
        uploaded_files = st.file_uploader("支持一次性上传多个博主文案文档", type=['docx', 'txt'], accept_multiple_files=True)
        manual_samples = []
        for i in range(st.session_state.sample_count):
            manual_samples.append(st.text_area(f"样本文稿 {i+1}", height=100, key=f"sample_{i}"))
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("➕ 添加更多样本输入框"):
                st.session_state.sample_count += 1
                st.rerun()
        if st.button("🧠 开始全量交叉分析基因", use_container_width=True):
            all_texts = [s for s in manual_samples if s.strip()]
            if uploaded_files:
                for f in uploaded_files:
                    try:
                        if f.name.endswith('.docx'):
                            all_texts.append(parse_docx(f))
                        else:
                            all_texts.append(f.read().decode('utf-8'))
                    except:
                        st.warning(f"无法读取 {f.name}")
            
            if all_texts and new_style_name:
                with st.spinner("正在深度分析风格基因..."):
                    style_desc = analyze_multi_styles(all_texts)
                    styles[new_style_name] = {
                        "description": style_desc,
                        "sop_template": "",
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_json(STYLES_PATH, styles)
                    st.success(f"✅ 风格 '{new_style_name}' 已保存！")
                    st.markdown(f"**风格描述**：{style_desc}")
            else:
                st.warning("请输入风格名称并提供至少一份样本。")
    
    with col_list:
        st.subheader("已训练风格")
        if styles:
            for style_name in styles.keys():
                st.markdown(f"✅ {style_name}")
        else:
            st.info("暂无已训练风格。")

with tab5:
    st.header("🎬 视频全自动生产工厂")
    factory_state = load_json(VIDEO_FACTORY_STATE_PATH, default={})
    
    if not factory_state:
        st.info('请先在【脚本生成】页面生成脚本并点击"同步到视频工厂"。')
    else:
        # 脚本选择器
        script_options = {script_id: f"{data.get('title', '未命名')} ({data.get('created_at', '未知时间')})" for script_id, data in factory_state.items()}
        selected_script_id = st.selectbox("选择要编辑的脚本", list(script_options.keys()), format_func=lambda x: script_options[x])
        
        if selected_script_id and selected_script_id in factory_state:
            current_script_data = factory_state[selected_script_id]
            st.subheader(f"当前视频标题：{current_script_data.get('title', '未命名')}")
            
            col_v1, col_v2 = st.columns([2, 1])
            with col_v1:
                st.subheader("场景预览与配图生成")
                
                # 获取当前脚本的场景数据
                scenes = current_script_data.get('scenes', [])
                
                # 初始化场景编辑状态
                if 'scene_deletions' not in st.session_state:
                    st.session_state.scene_deletions = {}
                
                if not scenes:
                    st.warning("该脚本没有场景数据。")
                else:
                    for idx, scene in enumerate(scenes):
                        scene_key = f"{selected_script_id}_{idx}"
                        
                        # 检查该场景是否被标记为删除
                        if st.session_state.scene_deletions.get(scene_key, False):
                            continue
                        
                        with st.container():
                            st.markdown(f'<div class="scene-card">', unsafe_allow_html=True)
                            
                            # 场景编号和删除按钮
                            col_scene_header = st.columns([3, 1])
                            with col_scene_header[0]:
                                st.markdown(f'<div class="video-step">场景 {idx+1}</div>', unsafe_allow_html=True)
                            with col_scene_header[1]:
                                if st.button("🗑️ 删除此场景", key=f"del_scene_{scene_key}"):
                                    st.session_state.scene_deletions[scene_key] = True
                                    st.rerun()
                            
                            # 提取配音文案和画面标注
                            content = scene.get("content", "")
                            
                            # 检查是否是画面标注（通常包含"配图建议"或"画面"等关键词）
                            is_annotation = "配图建议" in content or "画面" in content or "（" in content
                            
                            if is_annotation:
                                # 这是一个画面标注，只显示为标注，不作为配音文案
                                annotation_text = re.sub(r'\(配图建议[：:].*?\)', '', content).strip()
                                st.markdown(f"**画面标注** <span class='annotation-badge'>仅标注，不配音</span>：{annotation_text}", unsafe_allow_html=True)
                            else:
                                # 这是配音文案
                                clean_text = content.split("（配图建议")[0].split("(配图建议")[0].strip()
                                st.write(f"**配音文案**：{clean_text}")
                            
                            # 视觉描述
                            image_suggestion = scene.get("image_suggestion", "")
                            if image_suggestion:
                                st.caption(f"视觉描述：{image_suggestion}")
                            
                            # 配图生成
                            img_path = os.path.join(VIDEO_TEMP_DIR, f"img_{selected_script_id}_{idx}.png")
                            if os.path.exists(img_path):
                                st.image(img_path, width=400)
                                if st.button(f"🔄 重新生成配图 {idx+1}", key=f"regen_img_{scene_key}"):
                                    with st.spinner(f"正在重新绘制场景 {idx+1}..."):
                                        if generate_image(image_suggestion, img_path):
                                            st.success(f"场景 {idx+1} 配图生成成功！")
                                            st.rerun()
                            else:
                                if st.button(f"🎨 生成配图 {idx+1}", key=f"gen_img_{scene_key}"):
                                    with st.spinner(f"DALL-E 3 正在绘制场景 {idx+1}..."):
                                        if generate_image(image_suggestion, img_path):
                                            st.success(f"场景 {idx+1} 配图生成成功！")
                                            st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                if st.button("🚀 一键合成完整视频", use_container_width=True):
                    with st.spinner("正在合成视频素材，请稍候..."):
                        st.warning("由于当前订阅限制，视频最终渲染功能暂未开启。系统已为您准备好所有素材。")
            
            with col_v2:
                st.subheader("🎙️ 音色克隆中心")
                uploaded_voice = st.file_uploader("上传音色样本 (MP3/WAV)", type=['mp3', 'wav'])
                if uploaded_voice:
                    st.success("音色样本已接收，正在提取特征基因...")
                st.selectbox("选择 BGM 风格", ["激昂财经", "沉稳叙事", "快节奏电子", "无"])

with tab6:
    st.header("📂 文稿库")
    lib_data = load_json(EDITOR_OUTPUT_PATH, default=[])
    search_q = st.text_input("🔍 搜索文稿关键词", placeholder="输入选题、子选题或内容关键词...")
    
    filtered_lib = []
    if isinstance(lib_data, list):
        for item in lib_data:
            if isinstance(item, dict):
                if not search_q or search_q.lower() in str(item).lower():
                    filtered_lib.append(item)
    
    if not filtered_lib:
        st.info("文稿库空空如也，快去生成一份吧！")
    else:
        for item in reversed(filtered_lib):
            with st.container():
                topic_name = item.get('topic', '未知选题')
                created_at = item.get('created_at', '未知时间')
                subtopic = item.get('subtopic', '无子选题')
                style = item.get('style', '默认风格')
                content = item.get('content', '')
                
                st.markdown(f"""
                <div class="script-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:bold; color:#e63946;">{topic_name}</span>
                        <span style="color:#999; font-size:0.8rem;">{created_at}</span>
                    </div>
                    <div style="margin:10px 0; font-weight:500;">{subtopic}</div>
                    <div style="font-size:0.85rem; color:#666;">风格：{style}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col_lib1, col_lib2 = st.columns([2, 1])
                with col_lib1:
                    with st.expander("查看完整文稿"):
                        st.markdown(content)
                
                with col_lib2:
                    if st.button("📂 载入至编辑器", key=f"load_{item.get('id', 0)}"):
                        st.session_state.generated_script = content
                        st.success("文稿已载入【脚本生成】标签页！")
                        st.rerun()
                    
                    if st.button("🎬 同步至视频工厂", key=f"sync_{item.get('id', 0)}"):
                        with st.spinner("正在解析脚本并构建视频场景..."):
                            scenes = parse_script_to_scenes(content)
                            factory_state = load_json(VIDEO_FACTORY_STATE_PATH, default={})
                            script_id = str(datetime.now().timestamp())
                            factory_state[script_id] = {
                                "title": subtopic,
                                "scenes": scenes,
                                "original_script": content,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_json(VIDEO_FACTORY_STATE_PATH, factory_state)
                            st.success("✅ 文稿已同步至视频工厂！")
                            st.rerun()
