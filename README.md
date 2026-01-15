# 财经Alpha - 智能短视频脚本生成系统

本项目是一个基于 Streamlit 的智能短视频脚本生成应用，专为财经内容创作者设计。它集成了新闻抓取、AI 选题聚类、深度脚本生成和视频素材预处理等功能。

## 部署指南 (推荐使用 Streamlit Cloud)

本项目推荐使用 [Streamlit Cloud](https://streamlit.io/cloud) 或 [Hugging Face Spaces](https://huggingface.co/spaces) 进行部署，以实现永久在线运行。

### 步骤一：准备 GitHub 仓库

1.  在您的 GitHub 账号下创建一个新的**公开**仓库（例如：`finance-alpha-video-gen`）。
2.  将本项目中的所有文件上传到该仓库的根目录。

### 步骤二：配置 Streamlit Secrets

由于 Streamlit Cloud 无法访问本地文件系统，您需要通过其 Secrets 管理界面配置 API 密钥。

1.  登录 Streamlit Cloud，点击右上角的 **"New app"**。
2.  选择您刚刚创建的 GitHub 仓库和 `app.py` 文件作为主文件。
3.  在部署设置中，找到 **"Advanced settings"** -> **"Secrets"**。
4.  将 `secrets.toml` 中的内容以 TOML 格式粘贴到 Secrets 文本框中。

**Secrets 内容示例：**
```toml
[api_keys]
tianapi_key = "YOUR_TIANAPI_KEY"
# 部署时，您还需要在此处添加您的 OpenAI/Gemini 密钥
# openai_api_key = "YOUR_OPENAI_API_KEY"
# google_api_key = "YOUR_GOOGLE_API_KEY"
```
**注意**：您需要将 `YOUR_TIANAPI_KEY` 替换为您的实际密钥。

### 步骤三：部署应用

1.  确认 `requirements.txt` 文件已上传。
2.  点击 **"Deploy"** 按钮。Streamlit Cloud 将自动安装依赖并启动应用。

### 核心文件说明

| 文件名 | 描述 |
| :--- | :--- |
| `app.py` | Streamlit 主应用文件，包含所有 UI 逻辑和模块调用。 |
| `requirements.txt` | Python 依赖清单，用于托管平台安装环境。 |
| `news_fetcher.py` | 负责从 TianAPI 抓取新闻数据并保存到 `raw_news.json`。 |
| `topic_cluster.py` | 负责调用 AI 模型对新闻进行聚类，生成每日选题。 |
| `editor_generate.py` | 负责调用 AI 模型生成深度视频脚本。 |
| `video_utils.py` | 视频工厂的工具函数，用于脚本解析、场景拆分等。 |
| `.streamlit/secrets.toml` | 密钥配置模板，用于 Streamlit Cloud Secrets。 |

---
**致谢**：本项目由 Manus AI 协助开发和优化。
