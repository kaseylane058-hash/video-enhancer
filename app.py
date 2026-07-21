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

    # Smart Video Type Detection (Game vs Camera Analysis)
    cap_detect = cv2.VideoCapture(video_path)
    saturation_scores = []
    edge_scores = []
    
    for _ in range(15):
        ret, frame = cap_detect.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        saturation_scores.append(np.mean(hsv[:, :, 1]))
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edge_scores.append(cv2.Laplacian(gray, cv2.CV_64F).var())
        
    cap_detect.release()
    
    avg_saturation = np.mean(saturation_scores) if saturation_scores else 100
    avg_edges = np.mean(edge_scores) if edge_scores else 100
    
    is_game = avg_saturation > 90 and avg_edges > 200

    st.subheader("Step 2: Choose What You Want to Do")
    mode_choice = st.radio(
        "Select processing mode:",
        (
            "🛠️ 1. AI Video Repair (Noise & Grain Removal)",
            "🔎 2. Ultra HD Sharpening (Enhance Details)",
            "🎮 3. Game Restoration (Wink Style Pro)",
            "⚡ 4. FPS Boost (Link / URL Controlled)"
        ),
        index=2
    )

    st.write("---")
    st.subheader("Step 3: Settings & Processing")

    # Option 1: AI Video Repair
    if "1. AI Video Repair" in mode_choice:
        st.info("🛠️ **AI Video Repair Active:** Automatically removing noise and sensor grain while keeping colors safe.")
        
        if st.button("🚀 Start AI Video Repair", type="primary"):
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
                
                processed_frame = cv2.fastNlMeansDenoisingColored(frame, None, 6, 6, 7, 21)
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

            st.success("🎉 AI Video Repair Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Repaired Video", data=file, file_name="repaired_video.mp4", mime="video/mp4")

    # Option 2: Ultra HD Sharpening
    elif "2. Ultra HD Sharpening" in mode_choice:
        st.info("🔎 **Ultra HD Sharpening Active:** Enhancing clarity and details smoothly.")
        
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
                unsharp_y = cv2.addWeighted(smooth_y, 1.8, gaussian, -0.8, 0)
                
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
                st.download_button("⬇️ Download Ultra HD Video", data=file, file_name="ultrahd_video.mp4", mime="video/mp4")

    # Option 3: Game Restoration (Wink Style Pro)
    elif "3. Game Restoration" in mode_choice:
        st.info("🎮 **Game Restoration Active:** Specifically tuned for gaming footage (Free Fire, PUBG etc.) to pop colors and fix pixel blur.")
        
        if st.button("🚀 Start Game Restoration", type="primary"):
            st.write("⏳ Processing Game Restoration...")
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
                
                # Heavy Game Texture Boost & Artifact Cleanup
                denoised = cv2.fastNlMeansDenoisingColored(frame, None, 4, 4, 7, 21)
                yuv = cv2.cvtColor(denoised, cv2.COLOR_BGR2YUV)
                y, u, v = cv2.split(yuv)
                
                smooth_y = cv2.bilateralFilter(y, 9, 50, 50)
                gaussian = cv2.GaussianBlur(smooth_y, (0, 0), 1.2)
                game_enhanced_y = cv2.addWeighted(smooth_y, 2.2, gaussian, -1.2, 0)
                
                merged_yuv = cv2.merge((game_enhanced_y, u, v))
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

            st.success("🎉 Game Restoration Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Restored Game Video", data=file, file_name="game_restored_video.mp4", mime="video/mp4")

    # Option 4: FPS Boost
    elif "4. FPS Boost" in mode_choice:
        st.info("⚡ **FPS Boost Active:** Controlled via URL link (e.g., `?fps=60` or `?fps=90`).")
        
        target_fps = st.number_input(
            "Target FPS", 
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
            
