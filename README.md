# 财经Alpha - 智能短视频脚本生成系统

本项目是一个基于 Streamlit 的智能短视频脚本生成应用，专为财经内容创作者设计。它集成了新闻抓取、AI 选题聚类、深度脚本生成和视频素材预处理等功能。

## 部署指南 (推荐使用 Streamlit Cloud)

本项目推荐使用 [Streamlit Cloud](https://streamlit.io/cloud) 或 [Hugging Face Spaces](https://huggingface.co/spaces) 进行部署，以实现永久在线运行。

### 步骤一：准备 GitHub 仓库

1.  在您的 GitHub 账号下创建一个新的**公开**仓库（例如：`finance-alpha-video-gen`）。
2.  将本项目中的所有文件上传到该仓库的根目录。

### 步骤二：配置 Streamlit Secrets

由于 Streamlit Cloud 无法访问本地文件系统，您需要通过其 Secrets 管理界面配置 API 密钥。

1.  登录 [Streamlit Cloud](https://streamlit.io/cloud)，点击右上角的 **"New app"**。
2.  选择您刚刚创建的 GitHub 仓库和 `app.py` 文件作为主文件。
3.  在部署设置中，找到 **"Advanced settings"** -> **"Secrets"**。
4.  将以下内容粘贴到 Secrets 文本框中（请替换为您的实际密钥）：

```toml
# OpenAI API 密钥（必须）
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# Google API 密钥（如果使用 Gemini 模型，必须配置）
GOOGLE_API_KEY = "your-google-api-key-here"

# TianAPI 密钥（用于新闻抓取）
[api_keys]
tianapi_key = "765d0e02b73f9a975c3ce0fac97c4b82"
```

**重要提示**：
*   `OPENAI_API_KEY` 是**必须**配置的，否则脚本生成功能将无法工作。
*   如果您使用的是 Gemini 模型（`gemini-2.5-flash`），也需要配置 `GOOGLE_API_KEY`。
*   `tianapi_key` 用于从天聚数行 API 抓取新闻数据。

### 步骤三：部署应用

1.  确认 `requirements.txt` 文件已上传。
2.  点击 **"Deploy"** 按钮。Streamlit Cloud 将自动安装依赖并启动应用。
3.  等待约 2-3 分钟，您的应用将自动上线。

### 常见问题

**Q: 为什么出现 `PermissionError` 或路径错误？**
A: 本项目已将所有路径改为相对路径，以兼容云端部署。如果您仍遇到此问题，请确保您使用的是最新版本的代码包。

**Q: 为什么出现 `OpenAIError: The api_key client option must be set`？**
A: 这表示您没有在 Streamlit Secrets 中配置 `OPENAI_API_KEY`。请按照步骤二进行配置。

**Q: 如何查看详细的错误日志？**
A: 在 Streamlit Cloud 应用页面右下角，点击 **"Manage app"**，然后选择 **"Logs"** 查看完整的错误信息。

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

### 本地运行

如果您希望在本地测试，请执行以下命令：

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export OPENAI_API_KEY="your-openai-api-key"

# 运行应用
streamlit run app.py
```

---
**致谢**：本项目由 Manus AI 协助开发和优化。
