# 🎮 基于多模态大模型的端云协同实时视频流互动 Agent 系统

## 📖 项目简介
针对娱乐场景下的实时AI互动需求，本项目实现了一套“端侧轻量检测 + 云端多模态Agent”的端云协同系统。通过视频流传输、帧差法智能抽帧与云端大模型推理，实现实时、低成本、高趣味的互动体验。

## ✨ 核心特性
- **实时流媒体管道**：基于 Streamlit + WebRTC/HTTP流，实现浏览器与后端全双工视频流传输。
- **端侧智能抽帧与成本控制**：端侧部署 YOLO11n，结合帧差法，仅当画面显著变化（>10%）时才触发云端推理，带宽消耗降低 85%。
- **多模态 Agent 工作流**：集成多模态大模型（GLM-4V/阿里云百炼），支持结构化 JSON 输出（情绪+回复），为娱乐场景提供互动反馈。
- **高并发后端架构**：基于 FastAPI + 异步 HTTPX，解耦视频帧接收与云端推理。

## 🛠️ 技术栈
- 端侧：YOLO11n, OpenCV, Streamlit-WebRTC
- 后端：FastAPI, Uvicorn, HTTPX (异步)
- 云端：智谱 GLM-4V / 阿里云百炼 API
- 环境：Python 3.10+, python-dotenv

## 🚀 快速开始
### 1. 克隆项目
git clone [你的GitHub仓库链接]
cd EdgeCloud-Agent

### 2. 安装依赖
pip install -r requirements.txt

### 3. 下载端侧模型
需要手动下载 [yolo11n.pt](https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt) 并放到项目根目录。

### 4. 配置环境变量
在根目录创建 `.env` 文件，填入你的 API Key：
ZHIPU_API_KEY=你的密钥

### 5. 启动项目
- 启动后端： `python backend_server.py`
- 启动前端： `streamlit run frontend_app.py`