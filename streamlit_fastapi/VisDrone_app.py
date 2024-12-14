import streamlit as st
import requests
import os

# FastAPI server URL
API_URL = "http://127.0.0.1:8000"

# Function to detect objects in an image
def detect_image_api(image):
    url = f"{API_URL}/dataset/image"
    files = {'file': image}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        return response.content  # Return image with annotations
    else:
        st.error("Error detecting objects in the image.")
        return None

# Function to process a video and get the URL of the processed video
def detect_video_api(video):
    url = f"{API_URL}/dataset/video"  # The FastAPI endpoint to process the video
    files = {'file': video}  # The video file to send in the request
    response = requests.post(url, files=files)  # Send the request to FastAPI

    if response.status_code == 200:  # Check if the request was successful
        video_url = response.json().get("video_url")  # Get the video URL from the response
        if video_url:
            # Make sure the URL is correct and accessible from the browser
            full_video_url = f"http://127.0.0.1:8000{video_url}"  # Concatenate the base URL of FastAPI with the relative video path
            print(f"Full Video URL: {full_video_url}")  # Print the full video URL for debugging
            return full_video_url  # Return the full URL for the processed video
    else:
        st.error("Error processing the video.")  # Show an error message if the request fails
        return None  # Return None if there was an error

# Function to add a background image to the Streamlit app
def add_background(image_path):
    css = f"""
    <style>
    .stApp {{
        background: url(data:image/png;base64,{get_base64_of_bin_file(image_path)}) no-repeat center center fixed;
        background-size: contain; /* Adjusts the image to fit the window */
        background-color: #f0f0f0; /* Background color for empty spaces */
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Helper function to convert an image to base64 format
def get_base64_of_bin_file(bin_file):
    import base64
    with open(bin_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    return encoded

# Main Streamlit app function
def main():
    # Add custom CSS for background
    add_background("background.png")

    # Sidebar for file upload
    st.sidebar.title("📤 Upload Files")
    st.title("📸 VisDrone-YOLO Streamlit 🚀")

    # Option to choose between uploading images or videos
    upload_option = st.sidebar.radio("Choose what to upload:", ("Images", "Videos"))

    uploaded_file = None
    if upload_option == "Images":
        uploaded_file = st.sidebar.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])
    elif upload_option == "Videos":
        uploaded_file = st.sidebar.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "m4v", "asf"])

    if uploaded_file is not None:
        file_name = uploaded_file.name

        st.header("🖼️ Uploaded File:")
        if upload_option == "Images" and file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            st.image(uploaded_file, caption="Original Image")  # Display the uploaded image
            annotated_image_bytes = detect_image_api(uploaded_file)
            if annotated_image_bytes:
                st.header("🎯 Detection Results:")
                st.image(annotated_image_bytes, caption="Image with Annotations")

        elif upload_option == "Videos" and file_name.lower().endswith(('.mp4', '.mov', '.avi', '.m4v', '.asf')):
            st.video(uploaded_file)  # Display the original video

            # Process the video and get the URL of the processed video
            video_url = detect_video_api(uploaded_file)
            if video_url:
                st.header("🎯 Detection Results:")
                st.video(video_url)  # Display the processed video using the URL
            else:
                st.error("Processed video URL not found.")

if __name__ == "__main__":
    main()










