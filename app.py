import streamlit as st
import cv2
import numpy as np
import tempfile
import os

st.set_page_config(page_title="Ultra HD AI Video Tool", layout="centered", page_icon="🎬")

st.title("🎬 AI Video Repair, Enhancer & FPS Control")
st.write("Select a mode below to process your video:")

uploaded_file = st.file_uploader("Upload Video File (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    # Create Tabs for 3 Separate Features
    tab1, tab2, tab3 = st.tabs(["🛠️ 1. AI Video Repair", "🎨 2. Video Enhancer", "⚡ 3. FPS Boost"])

    mode = None
    
    with tab1:
        st.subheader("🛠️ AI Video Repair (Denoise & Grain Removal)")
        st.caption("Remove noise, grain, and artifacts from your video.")
        denoise_strength = st.slider("Denoise Strength", 1, 20, 5, key="repair_denoise")
        if st.button("Start Repairing Video", type="primary"):
            mode = "repair"

    with tab2:
        st.subheader("🎨 Ultra HD Clarity & Color Enhancer")
        st.caption("Enhance clarity, sharpness, contrast, and color saturation.")
        clarity = st.slider("Clarity / Sharpness Boost", 1.0, 3.0, 1.5, key="enhancer_clarity")
        contrast = st.slider("Contrast Enhancement", 0.8, 2.0, 1.2, key="enhancer_contrast")
        saturation = st.slider("Color Saturation", 0.8, 2.0, 1.3, key="enhancer_sat")
        if st.button("Start Enhancing Video", type="primary"):
            mode = "enhance"

    with tab3:
        st.subheader("⚡ Frame Rate & Smoothness (FPS)")
        st.caption("Change video frame rate (FPS) for smoother playback.")
        target_fps = st.select_slider("Target Frame Rate (FPS)", options=[24, 30, 60, 120], value=60, key="fps_target")
        if st.button("Start FPS Conversion", type="primary"):
            mode = "fps"

    # Processing Logic
    if mode is not None:
        st.write("---")
        st.write("⏳ Video Processing Started...")
        progress_bar = st.progress(0)
        
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100

        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        out_fps = target_fps if mode == "fps" else fps
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, out_fps, (width, height))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame = frame
            if mode == "repair":
                processed_frame = cv2.fastNlMeansDenoisingColored(frame, None, denoise_strength, denoise_strength, 7, 21)
            
            elif mode == "enhance":
                gaussian = cv2.GaussianBlur(frame, (0, 0), 3)
                sharpened = cv2.addWeighted(frame, clarity, gaussian, 1 - clarity, 0)
                
                hsv = cv2.cvtColor(sharpened, cv2.COLOR_BGR2HSV).astype(np.float32)
                hsv[:, :, 1] *= saturation
                hsv[:, :, 2] *= contrast
                hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
                hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
                processed_frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

            out.write(processed_frame)
            frame_count += 1
            progress_bar.progress(min(frame_count / total_frames, 1.0))

        cap.release()
        out.release()

        st.success("🎉 Processing Completed!")
        st.video(output_path)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="⬇️ Download Processed Video",
                data=file,
                file_name="processed_video.mp4",
                mime="video/mp4"
        )
                                            
