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
            "🛠️ 1. AI Video Repair (Auto Noise & Grain Removal)",
            "🔎 2. Ultra HD Sharpening (Auto & Color Safe)",
            "⚡ 3. FPS Boost (Link / URL Controlled)"
        ),
        index=1
    )

    st.write("---")
    st.subheader("Step 3: Settings & Processing")

    # Mode 1: AI Video Repair with Auto Analysis
    if "1. AI Video Repair" in mode_choice:
        st.info("🛠️ **AI Video Repair Active:** Automatically analyzing video noise levels and applying optimal restoration.")
        
        # Auto-analyze noise/grain level from the video frames
        cap_test = cv2.VideoCapture(video_path)
        noise_samples = []
        for _ in range(15):
            ret, frame = cap_test.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Standard deviation can indicate noise/grain level in uniform areas
            sigma = np.std(gray)
            noise_samples.append(sigma)
        cap_test.release()
        
        avg_noise = np.mean(noise_samples) if noise_samples else 10
        
        # Auto-tune denoise strength based on video characteristics
        if avg_noise > 25:
            auto_denoise = 12
        elif avg_noise > 15:
            auto_denoise = 8
        else:
            auto_denoise = 4
            
        st.write(f"✨ **Auto-Detected Denoise Strength:** `{auto_denoise}` (Optimized for your video)")
        
        if st.button("🚀 Start Auto Repairing Video", type="primary"):
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
                processed_frame = cv2.fastNlMeansDenoisingColored(frame, None, auto_denoise, auto_denoise, 7, 21)
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

    # Mode 2: Ultra HD Sharpening with Auto Analysis & Color Preservation
    elif "2. Ultra HD Sharpening" in mode_choice:
        st.info("🔎 **Ultra HD Sharpening Active:** Automatically analyzing blur/clarity levels and preserving original colors.")
        
        # Auto Intensity Calculation based on video blur/clarity analysis
        cap_test = cv2.VideoCapture(video_path)
        blur_scores = []
        for _ in range(15):
            ret, frame = cap_test.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            score = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_scores.append(score)
        cap_test.release()
        
        avg_blur = np.mean(blur_scores) if blur_scores else 100
        
        # Auto-tune logic based on blur score
        if avg_blur < 50:
            auto_sharpness = 2.8
        elif avg_blur < 150:
            auto_sharpness = 2.0
        else:
            auto_sharpness = 1.5
            
        st.write(f"✨ **Auto-Detected Sharpness Intensity:** `{auto_sharpness}` (Optimized for your video)")

        if st.button("🚀 Apply Auto Ultra HD Sharpening", type="primary"):
            st.write("⏳ Video Processing Started (Auto-Optimized Mode)...")
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
                
                # Convert to YUV color space to protect U and V (color channels) from distortion
                yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
                y, u, v = cv2.split(yuv)
                
                smooth_y = cv2.bilateralFilter(y, 9, 75, 75)
                gaussian = cv2.GaussianBlur(smooth_y, (0, 0), 2.0)
                unsharp_y = cv2.addWeighted(smooth_y, auto_sharpness, gaussian, 1.0 - auto_sharpness, 0)
                
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
            
