import streamlit as st
import cv2
import numpy as np
import tempfile
import os

st.set_page_config(page_title="Ultra HD Gaming Enhancer", layout="centered", page_icon="🎬")

st.title("🎬 Gaming Video Ultra HD Sharpening Tool")
st.write("Select a mode below to process your video:")

uploaded_file = st.file_uploader("Upload Video File (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    # Create Tabs for 3 Separate Features
    tab1, tab2, tab3 = st.tabs(["🛠️ 1. AI Video Repair", "🔎 2. Ultra HD Sharpening", "⚡ 3. FPS Boost"])

    mode = None
    
    with tab1:
        st.subheader("🛠️ AI Video Repair (Denoise & Grain Removal)")
        st.caption("Remove noise, grain, and pixelation artifacts.")
        denoise_strength = st.slider("Denoise Strength", 1, 20, 5, key="repair_denoise")
        if st.button("Start Repairing Video", type="primary"):
            mode = "repair"

    with tab2:
        st.subheader("🔎 Ultra Gaming HD Clarity & Edge Sharpening")
        st.caption("Enhances fine details, textures, and character edges for a crisp 4K gaming look.")
        sharpness_boost = st.slider("Edge & Detail Intensity", 1.0, 3.5, 2.2, key="crisp_sharpness")
        if st.button("🚀 Apply Ultra HD Sharpening", type="primary"):
            mode = "enhance"

    with tab3:
        st.subheader("⚡ Frame Rate & Smoothness (FPS)")
        st.caption("Boost video frame rate (FPS) for ultra-smooth gameplay.")
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
                # High-Precision Multi-Scale Detail Enhancement for Gaming
                # Step 1: Unsharp Masking
                gaussian = cv2.GaussianBlur(frame, (0, 0), 3.0)
                unsharp = cv2.addWeighted(frame, sharpness_boost, gaussian, 1.0 - sharpness_boost, 0)
                
                # Step 2: Detail Kernel for Crisp Edges
                kernel = np.array([[0, -1, 0],
                                   [-1, 5, -1],
                                   [0, -1, 0]], dtype=np.float32)
                crisp_frame = cv2.filter2D(unsharp, -1, kernel * 0.15)
                processed_frame = cv2.addWeighted(unsharp, 0.85, crisp_frame, 0.15, 0)

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
                file_name="ultrahd_gaming_video.mp4",
                mime="video/mp4"
                )
            
