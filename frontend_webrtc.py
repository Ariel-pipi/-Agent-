import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import base64
import requests
import time

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.prev_frame = None
        self.last_send_time = 0
        self.ai_reply = "等待分析..."

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # 缩小尺寸，降低带宽
        img = cv2.resize(img, (480, 360))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_frame is None:
            self.prev_frame = gray
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        # 帧差法计算变化
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        change_ratio = cv2.countNonZero(thresh) / (480 * 360)

        current_time = time.time()
        # 变化超过10% 且 距离上次发送超过3秒，才自动触发
        if change_ratio > 0.1 and (current_time - self.last_send_time) > 3.0:
            print(f"画面变化 {change_ratio:.2%}，自动触发分析！")
            self.last_send_time = current_time
            self.prev_frame = gray

            # 自动发送给后端（不需要用户点击按钮！）
            _, buffer = cv2.imencode('.jpg', img)
            bytes_data = buffer.tobytes()
            files = {"file": ("frame.jpg", bytes_data, "image/jpeg")}
            try:
                response = requests.post("http://127.0.0.1:8000/upload_frame", files=files)
                result = response.json()
                self.ai_reply = result.get("reply", "无回复")
            except Exception as e:
                print(f"发送失败: {e}")
        
        # 把 AI 回复实时叠加在视频画面上
        cv2.putText(img, "AI: " + self.ai_reply[:20], (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("🎮 实时视频流互动Agent（免点击版）")
st.write("摄像头已开启，画面发生变化时自动分析并显示AI点评。")
webrtc_streamer(key="example", video_processor_factory=VideoProcessor)