import streamlit as st
import cv2
import numpy as np
import tempfile
import subprocess
import os

st.set_page_config(page_title="Mjrsweb", layout="centered", page_icon="🎬")

st.title("Mjrsweb")

query_params = st.query_params
try:
    default_fps_from_url = int(query_params.get("fps", 60))
except ValueError:
    default_fps_from_url = 60

st.subheader("Step 1: Upload Your Video File")
uploaded_file = st.file_uploader(
    "Upload only video files (MP4, MOV, AVI)", 
    type=["mp4", "mov", "avi"],
    help="Other file formats are not allowed. Please upload a valid video."
)

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    st.success("✅ Video Uploaded Successfully!")
    st.write("---")

    # Smart Video Type Detection (Game vs Camera)
    cap_detect = cv2.VideoCapture(video_path)
    saturation_scores = []
    edge_scores = []
    
    for _ in range(15):
        ret, frame = cap_detect.read()
        if not ret:
            break
        # Convert to HSV to check color saturation (Games usually have higher saturation)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        saturation_scores.append(np.mean(hsv[:, :, 1]))
        
        # Check edge sharpness using Laplacian
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edge_scores.append(cv2.Laplacian(gray, cv2.CV_64F).var())
        
    cap_detect.release()
    
    avg_saturation = np.mean(saturation_scores) if saturation_scores else 100
    avg_edges = np.mean(edge_scores) if edge_scores else 100
    
    # Classification Logic
    if avg_saturation > 90 and avg_edges > 200:
        detected_type = "🎮 Gaming Video (High Saturation & Sharp Edges)"
    else:
        detected_type = "📸 Camera / Real-Life Video (Natural Tones & Soft Textures)"

    st.info(f"🧠 **AI Self-Analysis Result:** Detected as **{detected_type}**")
    st.write("---")

    st.subheader("Step 2: Choose What You Want to Do")
    mode_choice = st.radio(
        "Select processing mode:",
        (
            "🛠️ 1. AI Video Repair (Self-Adapts to Game/Camera)",
            "🔎 2. Ultra HD Sharpening (Adaptive Game & Camera Enhancer)",
            "⚡ 3. FPS Boost (Link / URL Controlled)"
        ),
        index=1
    )

    st.write("---")
    st.subheader("Step 3: Settings & Processing")

    # Mode 1: AI Video Repair (Automatically adjusts based on Game or Camera)
    if "1. AI Video Repair" in mode_choice:
        if "Gaming" in detected_type:
            st.info("🛠️ **AI Repair Active (Gaming Mode):** Optimizing graphics clarity, clearing compression artifacts, and locking vibrant colors.")
            denoise_val = 5
            ai_boost = 1.8
        else:
            st.info("🛠️ **AI Repair Active (Camera Mode):** Enhancing skin textures, removing sensor grain, and preserving realistic lighting.")
            denoise_val = 8
            ai_boost = 1.4

        if st.button("🚀 Start Smart AI Video Repair", type="primary"):
            st.write("⏳ Video Processing Started (Smart AI Mode)...")
            progress_bar = st.progress(0)
            
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100

            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.avi').name
            final_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Smart Denoise & Artifact Removal
                denoised = cv2.fastNlMeansDenoisingColored(frame, None, denoise_val, denoise_val, 7, 21)
                
                # Color Safe Processing using YUV
                yuv = cv2.cvtColor(denoised, cv2.COLOR_BGR2YUV)
                y, u, v = cv2.split(yuv)
                
                smooth_y = cv2.bilateralFilter(y, 9, 60, 60)
                gaussian = cv2.GaussianBlur(smooth_y, (0, 0), 1.5)
                enhanced_y = cv2.addWeighted(smooth_y, ai_boost, gaussian, 1.0 - ai_boost, 0)
                
                merged_yuv = cv2.merge((enhanced_y, u, v))
                processed_frame = cv2.cvtColor(merged_yuv, cv2.COLOR_YUV2BGR)

                out.write(processed_frame)
                frame_count += 1
                progress_bar.progress(min(frame_count / total_frames, 1.0))

            cap.release()
            out.release()

            subprocess.run([
                'ffmpeg', '-y', '-i', temp_output, '-i', video_path, 
                '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-pix_fmt', 'yuv420p', 
                '-c:a', 'aac', '-b:a', '192k', '-shortest', final_output
            ])

            st.success("🎉 Smart AI Video Repair Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Repaired Video", data=file, file_name="smart_ai_repaired.mp4", mime="video/mp4")

    # Mode 2: Ultra HD Sharpening
    elif "2. Ultra HD Sharpening" in mode_choice:
        if "Gaming" in detected_type:
            st.info("🔎 **Ultra HD Sharpening Active (Gaming Mode):** Maximizing edge clarity for gameplay action.")
            sharpness_val = 2.4
        else:
            st.info("🔎 **Ultra HD Sharpening Active (Camera Mode):** Enhancing fine details smoothly without artificial harshness.")
            sharpness_val = 1.7

        if st.button("🚀 Apply Ultra HD Sharpening", type="primary"):
            st.write("⏳ Video Processing Started...")
            progress_bar = st.progress(0)
            
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100

            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.avi').name
            final_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
                y, u, v = cv2.split(yuv)
                
                smooth_y = cv2.bilateralFilter(y, 9, 75, 75)
                gaussian = cv2.GaussianBlur(smooth_y, (0, 0), 2.0)
                unsharp_y = cv2.addWeighted(smooth_y, sharpness_val, gaussian, 1.0 - sharpness_val, 0)
                
                merged_yuv = cv2.merge((unsharp_y, u, v))
                processed_frame = cv2.cvtColor(merged_yuv, cv2.COLOR_YUV2BGR)

                out.write(processed_frame)
                frame_count += 1
                progress_bar.progress(min(frame_count / total_frames, 1.0))

            cap.release()
            out.release()

            subprocess.run([
                'ffmpeg', '-y', '-i', temp_output, '-i', video_path, 
                '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-pix_fmt', 'yuv420p', 
                '-c:a', 'aac', '-b:a', '192k', '-shortest', final_output
            ])

            st.success("🎉 Ultra HD Sharpening Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Ultra HD Video", data=file, file_name="wink_style_video.mp4", mime="video/mp4")

    # Mode 3: FPS Boost (Link / URL Controlled)
    elif "3. FPS Boost" in mode_choice:
        st.info("⚡ **FPS Boost Active:** Controlled via URL link (e.g., `?fps=60`).")
        
        target_fps = st.number_input(
            "Target FPS (You can also change this directly via link like ?fps=90)", 
            min_value=10, 
            max_value=240, 
            value=default_fps_from_url, 
            step=1
        )
        
        if st.button("🚀 Start FPS Conversion", type="primary"):
            st.write("⏳ Video Processing Started...")
            progress_bar = st.progress(50)
            
            final_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path, 
                '-filter:v', f'fps={target_fps}', 
                '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-pix_fmt', 'yuv420p', 
                '-c:a', 'aac', '-b:a', '192k', final_output
            ])
            
            progress_bar.progress(100)
            st.success("🎉 FPS Conversion Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Smooth Video", data=file, file_name="smooth_fps_video.mp4", mime="video/mp4")
else:
    st.info("👆 Please upload a video file (MP4, MOV, AVI) to start.")
            
