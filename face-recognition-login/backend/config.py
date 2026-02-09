# backend/config.py

# Face Recognition Settings
FACE_RECOGNITION_TOLERANCE = 0.6  # ← เปลี่ยนตรงนี้
FACE_ENCODINGS_PATH = "face_data/encodings"

# CORS
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]