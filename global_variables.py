from datetime import datetime, timezone
import os

DEFAULT_IMAGE = "def_img.png"

dir_path = os.path.dirname(os.path.realpath(__file__))

def getCurrentTime():
    return datetime.now().replace(tzinfo=timezone.utc)