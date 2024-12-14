import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import tempfile
import cv2
from ultralytics import YOLO
import numpy as np
from PIL import Image
import io
import subprocess
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="VisDrone-YOLO API")

# Define the static directory to serve video files
static_dir = os.path.join(os.getcwd(), 'static')  # Create the static directory path
os.makedirs(static_dir, exist_ok=True)  # Create the static directory if it doesn't exist

# Mount the static directory to serve video files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Homepage endpoint
@app.get("/")
def homepage():
    html = """
        <html>
        <head><title>VisDrone-YOLO API</title></head>
        <body>
            <h1>Welcome to the VisDrone-YOLO API</h1>
        </body>
        </html>
    """
    return HTMLResponse(content=html, status_code=200)

# Load YOLO model
model = YOLO('model/VisDrone.pt')  # Load the YOLO model from the specified path

# Function to detect objects in an image
def detect_in_image(image: Image.Image):
    image_np = np.array(image)  # Convert PIL image to numpy array
    results = model(image_np)  # Perform object detection
    detections = []

    # Extract detection results
    for result in results:
        for box in result.boxes:
            detections.append({
                "label": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "coordinates": box.xyxy.tolist()
            })

    # Annotate the image with detection results
    annotated_image = results[0].plot()
    annotated_image_pil = Image.fromarray(annotated_image)
    return detections, annotated_image_pil

# Function to detect objects in a video
def detect_in_video(video_path: str, output_path: str):
    cap = cv2.VideoCapture(video_path)  # Open the video file
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Error opening video file.")

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define temporary output path for the annotated video
    temp_output_path = os.path.join(tempfile.gettempdir(), "temp_output.avi")
    out = cv2.VideoWriter(temp_output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    # Process each frame in the video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)  # Perform object detection on the frame
        annotated_frame = results[0].plot()
        out.write(annotated_frame)

    # Release video capture and writer objects
    cap.release()
    out.release()

    # Convert the .avi file to .mp4 using ffmpeg
    subprocess.run(['ffmpeg', '-y', '-i', temp_output_path, output_path])  # '-y' flag overwrites without prompt

    # Remove the temporary .avi file
    os.remove(temp_output_path)

    return output_path

# Endpoint for detecting objects in an image
@app.post("/dataset/image")
async def detect_image(file: UploadFile = File(...)):
    try:
        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name

        # Open the image and perform object detection
        image = Image.open(tmp_file_path)
        detections, annotated_image = detect_in_image(image)

        # Remove the temporary file
        os.remove(tmp_file_path)

        # Save the annotated image to a byte array
        img_byte_arr = io.BytesIO()
        annotated_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Return the annotated image as a streaming response
        return StreamingResponse(img_byte_arr, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# Endpoint for object detection in a video
@app.post("/dataset/video")
async def detect_video(file: UploadFile = File(...)):
    try:
        # Save the uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            input_path = tmp_file.name

        # Define the output path for the annotated video
        output_path = os.path.join(static_dir, f"output_{os.path.splitext(file.filename)[0]}.mp4")

        # Perform object detection on the video
        detect_in_video(input_path, output_path)

        # Remove the temporary input file
        os.remove(input_path)

        # Return the URL to the annotated video
        video_url = f"/static/{os.path.basename(output_path)}"
        return {"video_url": video_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

# Entry point to run the FastAPI app with uvicorn
if __name__ == "__main__":
    uvicorn.run("VisDrone_api:app", host="0.0.0.0", port=8000, reload=True)









