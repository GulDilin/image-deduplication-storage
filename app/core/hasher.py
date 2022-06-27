import hashlib
import numpy as np
import cv2


def get_image_hash(bytes_file_data: bytes) -> str:
    return hashlib.md5(
        np.array(cv2.imdecode(np.frombuffer(bytes_file_data, dtype=np.uint8), cv2.IMREAD_COLOR))
    ).hexdigest()
