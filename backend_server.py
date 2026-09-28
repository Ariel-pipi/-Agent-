# backend_server.py
from fastapi import FastAPI, UploadFile, File
import uvicorn
import cv2
import numpy as np
import base64
import os
import httpx
from dotenv import load_dotenv
from ultralytics import YOLO

# 加载环境变量
load_dotenv()

# ⚠️ 这里直接复用之前的配置名称
API_KEY = os.getenv("ALIYUN_API_KEY")
BASE_URL = os.getenv("ALIYUN_BASE_URL")
MODEL_NAME = "glm-4v-flash"

# 调试打印，确认读到值了
print("=" * 30)
print(f"当前读取到的Key是: {API_KEY[:10]}...（已隐藏）" if API_KEY else "❌ 没读到 API_KEY！")
print(f"当前读取到的URL是: {BASE_URL}")
print("=" * 30)

app = FastAPI(title="端云协同实时系统")

# 全局加载 YOLO11n 模型
model = YOLO("yolo11n.pt")

async def call_glm4v(image_base64: str, prompt: str):
    """异步调用云端多模态大模型"""
    # 兼容处理：如果 BASE_URL 结尾带有斜杠，就去除，防止出现双斜杠
    clean_base_url = BASE_URL.rstrip('/') if BASE_URL else ""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{clean_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": MODEL_NAME,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_base64}}
                    ]
                }]
            }
        )
        return response.json()

@app.post("/upload_frame")
async def upload_frame(file: UploadFile = File(...)):
    # 1. 读取上传的图片数据
    image_bytes = await file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 2. 运行 YOLO 推理
    results = model(frame, verbose=False)
    
    detected_objects = []
    cropped_image_base64 = None
    
    # 3. 提取检测到的物体，并裁剪第一个物体
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            detected_objects.append(model.names[cls_id])
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
            cropped = frame[y1:y2, x1:x2]
            if cropped.size == 0:
                continue
                
            _, buffer = cv2.imencode('.jpg', cropped)
            cropped_image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
            break
            
    if not cropped_image_base64:
        return {"status": "success", "objects": [], "reply": "画面里什么都没看到哦~"}
    
    # 4. 构造提示词，调用云端大模型
    prompt = "你是一个娱乐互动助手。请用幽默夸张的语气评价这个物体，不超过20个字。"
    try:
        glm_response = await call_glm4v(cropped_image_base64, prompt)
        
        # 打印大模型返回的原始数据，排查错误
        print("=" * 30)
        print("云端API返回的原始数据：")
        print(glm_response)
        print("=" * 30)
        
        reply = glm_response['choices'][0]['message']['content']
    except Exception as e:
        reply = f"大模型调用失败: {str(e)}"
        
    return {"status": "success", "objects": list(set(detected_objects)), "reply": reply}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)