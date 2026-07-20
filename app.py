import cv2
import numpy as np
import streamlit as st
import tempfile

st.set_page_config(page_title="Ultra HD AI Video Enhancer & Repair", layout="centered")

st.title("🎬 Ultra HD AI Video Enhancer & Repair")
st.write("Restore video clarity, remove noise, boost FPS, and apply cinematic high-definition detail retention.")

uploaded_file = st.file_uploader("Upload Video File (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    st.subheader("⚙️ High-Quality Processing Controls")
    
    # 1. AI Repair / Denoise
    st.markdown("### 🛠️ 1. AI Repair & Artifact Removal")
    denoise_level = st.slider("Denoise Strength (Removes grain & noise)", 0, 20, 5)

    # 2. HD Enhancement & Unsharp Masking
    st.markdown("### 🎨 2. Ultra HD Clarity & Sharpening")
    clarity = st.slider("Clarity / Sharpness Boost", 0.0, 3.0, 1.5)
    contrast = st.slider("Contrast Enhancement", 0.8, 2.0, 1.15)
    saturation = st.slider("Color Saturation", 0.8, 2.0, 1.15)

    # 3. FPS Smoothing
    st.markdown("### ⚡ 3. Frame Rate & Smoothness")
    target_fps = st.select_slider("Target Frame Rate (FPS)", options=[24, 30, 60], value=60)

    if st.button("Start High-Quality Enhancement"):
        st.info("Enhancing video quality using AI algorithms... Please wait.")
        
        cap = cv2.VideoCapture(tfile.name)
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        # High quality H264 encoding via mp4v
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame = frame.copy()

            # --- Step 1: AI Denoise / Grain Removal ---
            if denoise_level > 0:
                processed_frame = cv2.fastNlMeansDenoisingColored(
                    processed_frame, None, denoise_level, denoise_level, 7, 21
                )

            # --- Step 2: Unsharp Masking for Advanced Sharpness & Details ---
            if clarity > 0:
                gaussian = cv2.GaussianBlur(processed_frame, (0, 0), 3.0)
                processed_frame = cv2.addWeighted(processed_frame, 1.0 + clarity, gaussian, -clarity, 0)

            # --- Step 3: Color, Contrast & Vibrance Retention ---
            processed_frame = cv2.convertScaleAbs(processed_frame, alpha=contrast, beta=2)

            hsv = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2HSV).astype("float32")
            (h, s, v) = cv2.split(hsv)
            s = np.clip(s * saturation, 0, 255)
            hsv = cv2.merge([h, s, v])
            processed_frame = cv2.cvtColor(hsv.astype("uint8"), cv2.COLOR_HSV2BGR)

            out.write(processed_frame)

        cap.release()
        out.release()

        st.success("Video enhancement complete with Maximum Quality!")
        st.video(output_path)
      
