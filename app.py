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

    st.subheader("Step 2: Choose What You Want to Do")
    mode_choice = st.radio(
        "Select processing mode:",
        (
            "🛠️ 1. AI Video Repair (Remove Noise & Grain)",
            "🔎 2. Ultra HD Sharpening (Remove Blur & Enhance Details)",
            "⚡ 3. FPS Boost (Make Video Smoother)"
        ),
        index=1
    )

    st.write("---")
    st.subheader("Step 3: Settings & Processing")

    if "1. AI Video Repair" in mode_choice:
        st.info("🛠️ **AI Video Repair Active:** Removes noise, grain, and pixelation artifacts.")
        denoise_strength = st.slider("Denoise Strength", 1, 20, 5)
        
        if st.button("🚀 Start Repairing Video", type="primary"):
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
                processed_frame = cv2.fastNlMeansDenoisingColored(frame, None, denoise_strength, denoise_strength, 7, 21)
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

            st.success("🎉 Video Repair Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Repaired Video", data=file, file_name="repaired_video.mp4", mime="video/mp4")

    elif "2. Ultra HD Sharpening" in mode_choice:
        st.info("🔎 **Ultra HD Sharpening (Wink Style) Active:** Enhancing clarity, edges, and textures like pro mobile editors.")
        sharpness_boost = st.slider("Edge & Detail Intensity", 1.0, 4.0, 2.8)
        
        if st.button("🚀 Apply Ultra HD Sharpening", type="primary"):
            st.write("⏳ Video Processing Started (High Quality Mode)...")
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
                
                smooth_frame = cv2.bilateralFilter(frame, 9, 75, 75)
                gaussian = cv2.GaussianBlur(smooth_frame, (0, 0), 2.0)
                unsharp = cv2.addWeighted(smooth_frame, sharpness_boost, gaussian, 1.0 - sharpness_boost, 0)
                
                lab = cv2.cvtColor(unsharp, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                cl = clahe.apply(l)
                limg = cv2.merge((cl, a, b))
                processed_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

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
                
