import cv2
import tempfile
import streamlit as st

st.set_page_config(page_title="Mjrsweb - Video Tools", layout="centered")

# Sidebar navigation to switch between features cleanly
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose a Feature", [
    "Video Enhancer", 
    "FPS Converter", 
    "Coming Soon Feature"
])

if app_mode == "Video Enhancer":
    st.title("Mjrsweb - Video Enhancer")
    st.write("This interface is only for enhancing video quality.")
    
    uploaded_file = st.file_uploader("Upload video for enhancement", type=["mp4", "mov", "avi"], key="enhancer")
    if uploaded_file is not None:
        st.info("Enhancement logic goes here...")

elif app_mode == "FPS Converter":
    st.title("Mjrsweb - FPS Converter")
    st.write("This interface is only for automatic FPS processing.")

    uploaded_file = st.file_uploader("Upload video for FPS processing", type=["mp4", "mov", "avi"], key="fps_tool")
    
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
        
        st.write(f"Detected FPS: {original_fps}")
        st.write(f"Resolution: {width}x{height}")
        
        if st.button("Start Processing"):
            with st.spinner("Processing video automatically, please wait..."):
                output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_file.name, fourcc, float(original_fps), (width, height))
                
                progress_bar = st.progress(0)
                frame_count = 0
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
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

elif app_mode == "Coming Soon Feature":
    st.title("Mjrsweb - Future Tool")
    st.write("Another separate feature interface will appear here.")
    
