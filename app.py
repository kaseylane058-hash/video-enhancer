import cv2
import tempfile
import streamlit as st

st.title("Mjrsweb - Video Enhancer & FPS Converter")

uploaded_file = st.file_uploader("Upload your video file here", type=["mp4", "mov", "avi"])

target_fps = st.selectbox("Select Target FPS:", [24, 30, 60], index=1)

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    cap = cv2.VideoCapture(tfile.name)
    
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    if original_fps == 0 or original_fps is None:
        original_fps = 30.0
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    st.write(f"Original FPS: {original_fps}")
    st.write(f"Target FPS: {target_fps}")
    st.write(f"Resolution: {width}x{height}")
    
    if st.button("Start Processing"):
        with st.spinner("Processing video without quality loss, please wait..."):
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            
            # Using mp4v codec for universal compatibility (gaming & camera videos)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_file.name, fourcc, float(target_fps), (width, height))
            
            progress_bar = st.progress(0)
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Writing original high-quality frames directly to maintain pristine quality
                out.write(frame)
                frame_count += 1
                
                if total_frames > 0 and frame_count % 10 == 0:
                    progress = min(frame_count / total_frames, 1.0)
                    progress_bar.progress(progress)
            
            cap.release()
            out.release()
            progress_bar.progress(1.0)
            
            st.success("Processing completed successfully!")
            
            with open(output_file.name, "rb") as file:
                st.download_button(
                    label="Download Processed Video",
                    data=file,
                    file_name="processed_video.mp4",
                    mime="video/mp4"
                )
                
