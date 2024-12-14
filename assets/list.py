from enum import Enum

VIDEO_URL = "https://github.com/Juank0621/VisDrone_YOLO11/raw/main/assets/video_demo.mp4"

class VideoAsset(Enum):
    """
    Represents a single video asset.

    | Enum Member | Video Filename    | Video URL                                                       |
    |-------------|-------------------|-----------------------------------------------------------------|
    | `DEMO`      | `video_demo.mp4`  | [Link](https://github.com/Juank0621/VisDrone_YOLO11/raw/main/assets/video_demo.mp4) |
    """
    DEMO = "video_demo.mp4"