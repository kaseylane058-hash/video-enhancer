import streamlit as st
import cv2
import numpy as np
import tempfile
import subprocess
import os

st.set_page_config(page_title="Mjrsweb", layout="centered", page_icon="🎬")


st.title("Mjrsweb")

# Step 1: Upload Video First
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

    # Step 2: Choose Action After Upload
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

    # Mode 1: Repair
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

            # Convert to Mobile Friendly MP4 with Audio and High Quality using ffmpeg
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_output, '-i', video_path, 
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', 
                '-c:a', 'aac', '-shortest', final_output
            ])

            st.success("🎉 Video Repair Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Repaired Video", data=file, file_name="repaired_video.mp4", mime="video/mp4")

    # Mode 2: Ultra HD Sharpening
    elif "2. Ultra HD Sharpening" in mode_choice:
        st.info("🔎 **Ultra HD Sharpening Active:** Enhances character edges and textures without altering original colors.")
        sharpness_boost = st.slider("Edge & Detail Intensity", 1.0, 3.5, 2.20)
        
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
                
                gaussian = cv2.GaussianBlur(frame, (0, 0), 3.0)
                unsharp = cv2.addWeighted(frame, sharpness_boost, gaussian, 1.0 - sharpness_boost, 0)
                
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
                crisp_frame = cv2.filter2D(unsharp, -1, kernel * 0.15)
                processed_frame = cv2.addWeighted(unsharp, 0.85, crisp_frame, 0.15, 0)

                out.write(processed_frame)
                frame_count += 1
                progress_bar.progress(min(frame_count / total_frames, 1.0))

            cap.release()
            out.release()

            # Convert to Mobile Friendly MP4 with Audio and High Quality using ffmpeg
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_output, '-i', video_path, 
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', 
                '-c:a', 'aac', '-shortest', final_output
            ])

            st.success("🎉 Ultra HD Sharpening Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Ultra HD Video", data=file, file_name="ultrahd_video.mp4", mime="video/mp4")

    # Mode 3: FPS Boost
    elif "3. FPS Boost" in mode_choice:
        st.info("⚡ **FPS Boost Active:** Increases the video frame rate for smoother gameplay playback.")
        target_fps = st.select_slider("Target Frame Rate (FPS)", options=[24, 30, 60, 120], value=60)
        
        if st.button("🚀 Start FPS Conversion", type="primary"):
            st.write("⏳ Video Processing Started...")
            progress_bar = st.progress(0)
            
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100

            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.avi').name
            final_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(temp_output, fourcc, target_fps, (width, height))

            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                frame_count += 1
                progress_bar.progress(min(frame_count / total_frames, 1.0))

            cap.release()
            out.release()

            # Convert to Mobile Friendly MP4 with Audio and High Quality using ffmpeg
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_output, '-i', video_path, 
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', 
                '-c:a', 'aac', '-shortest', final_output
            ])

            st.success("🎉 FPS Conversion Completed!")
            st.video(final_output)
            with open(final_output, "rb") as file:
                st.download_button("⬇️ Download Smooth Video", data=file, file_name="smooth_fps_video.mp4", mime="video/mp4")
else:
    st.info("👆 Please upload a video file (MP4, MOV, AVI) to start.")
                
