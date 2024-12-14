import os
from pathlib import Path
from shutil import copyfileobj
from requests import get
from tqdm.auto import tqdm

def download_video(output_path: str = None) -> str:
    """
    Downloads the video asset if it doesn't already exist.

    Parameters:
        output_path (str): Optional path to save the video file. Defaults to the current directory.

    Returns:
        str: The path to the downloaded video file.

    Example:
        ```python
        from downloader import download_video

        download_video()
        """
    filename = "video_demo.mp4"
    url = "https://github.com/Juank0621/VisDrone_YOLO11/raw/main/assets/video_demo.mp4"

    if output_path:
        folder_path = Path(output_path).expanduser().resolve()
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / filename
    else:
        file_path = Path(filename).expanduser().resolve()

    if not file_path.exists():
        print(f"Downloading {filename}...\n")
        response = get(url, stream=True, allow_redirects=True)
        response.raise_for_status()

        file_size = int(response.headers.get("Content-Length", 0))
        with tqdm.wrapattr(response.raw, "read", total=file_size, desc="", colour="#a351fb") as raw_resp:
            with file_path.open("wb") as file:
                copyfileobj(raw_resp, file)

        print(f"{filename} download complete.\n")
    else:
        print(f"{filename} already exists.\n")

    return str(file_path)