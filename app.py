import streamlit as st
import tempfile
import subprocess
import os

st.set_page_config(page_title="Mjrsweb", layout="centered", page_icon="🎬")
st.title("Mjrsweb (Super Fast FFmpeg Engine)")

uploaded_file = st.file_uploader("Upload video (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    st.success("✅ Video Uploaded Successfully!")
    
    mode_choice = st.radio(
        "Select processing mode:",
        (
            "🛠️ 1. AI Video Repair (Noise & Grain Removal)",
            "🔎 2. Ultra HD Sharpening (Enhance Details)",
            "🎮 3. Game Restoration (Wink Style Pro)",
            "⚡ 4. Custom FPS Boost Only"
        ),
        index=2
    )

    # FPS input box will appear ONLY when Mode 4 is selected
    target_fps = 60  # Default value
    if "4. Custom FPS Boost Only" in mode_choice:
        st.write("---")
        st.subheader("⚙️ Custom FPS Settings")
        target_fps = st.number_input(
            "Enter Target FPS (e.g., 30, 45, 60):", 
            min_value=10, 
            max_value=240, 
            value=60, 
            step=1,
            help="Type the exact FPS you want for your final video."
        )

    def get_scale_filter(res_choice):
        if "4K" in res_choice:
            return "scale=3840:2160:flags=lanczos"
        elif "2K" in res_choice:
            return "scale=2560:1440:flags=lanczos"
        elif "1080p" in res_choice:
            return "scale=1920:1080:flags=lanczos"
        elif "720p" in res_choice:
            return "scale=1280:720:flags=lanczos"
        else:
            return "scale=trunc(iw/2)*2:trunc(ih/2)*2"

    def render_download_section(processed_video_path, default_filename):
        st.write("---")
        save_resolution = st.selectbox(
            "Select Output Download Resolution:",
            ("4K Ultra HD (3840x2160)", "2K QHD (2560x1440)", "1080p Full HD (1920x1080)", "720p HD", "Original Resolution"),
            index=2
        )

        if st.button("✨ Generate Final Video", type="primary"):
            with st.spinner("⏳ Exporting instantly with FFmpeg..."):
                final_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
                scale_filter = get_scale_filter(save_resolution)

                subprocess.run([
                    'ffmpeg', '-y', '-i', processed_video_path,
                    '-vf', scale_filter,
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
                    '-c:a', 'copy', final_output
                ])
                
                st.success("🎉 Ready!")
                st.video(final_output)
                with open(final_output, "rb") as file:
                    st.download_button("⬇️ Download Video", data=file, file_name=default_filename, mime="video/mp4")

    if st.button("🚀 Start Instant Processing", type="primary"):
        with st.spinner("⏳ Fast Processing with FFmpeg..."):
            final_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            # Apply filters based on the selected mode
            if "1. AI Video Repair" in mode_choice:
                vf_filter = "hqdn3d=4:3:6:4.5"
            elif "2. Ultra HD Sharpening" in mode_choice:
                vf_filter = "unsharp=5:5:1.0:5:5:0.0"
            elif "3. Game Restoration" in mode_choice:
                vf_filter = "hqdn3d=3:2:3:2,eq=contrast=1.2:saturation=1.3,unsharp=3:3:0.8"
            else:
                vf_filter = f"fps={target_fps}"

            subprocess.run([
                'ffmpeg', '-y', '-i', video_path,
                '-vf', vf_filter,
                '-c:v', 'libx264', '-crf', '20', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', final_output
            ])

            st.session_state['processed_video'] = final_output
            st.session_state['filename'] = "enhanced_video.mp4"
            st.success("🎉 Done in seconds!")

    if 'processed_video' in st.session_state:
        render_download_section(st.session_state['processed_video'], st.session_state.get('filename', 'video.mp4'))
        
