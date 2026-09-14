# frontend_app.py
import streamlit as st
import requests

st.title("🎮 娱乐场景AI互动助手")
st.write("点击下方拍照，AI 将为你实时解读！")

# 调用浏览器摄像头
img_file = st.camera_input("拍一张照片")

if img_file is not None:
    # 显示照片
    st.image(img_file, caption="你拍的照片", use_container_width=True)
    
    with st.spinner("AI 正在思考..."):
        # 将图片转为字节流
        bytes_data = img_file.getvalue()
        files = {"file": ("frame.jpg", bytes_data, "image/jpeg")}
        
        try:
            # 发送给后端
            response = requests.post("http://127.0.0.1:8000/upload_frame", files=files)
            result = response.json()
            
            # 展示结果
            st.success(f"检测到的物体: {result.get('objects', [])}")
            st.info(f"🤖 AI点评: {result.get('reply', '无回复')}")
            
        except Exception as e:
            st.error(f"连接后端失败: {e}")