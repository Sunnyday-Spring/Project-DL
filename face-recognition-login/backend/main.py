# backend/main.py
import cv2 
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io
import traceback

# เพิ่มส่วน import สำหรับ liveness และ head pose
from liveness_detection import liveness_detector, head_pose_detector

from face_utils import face_system
import config

# สร้าง FastAPI app
app = FastAPI(
    title="Face Recognition API",
    description="API สำหรับระบบ Face Recognition Login",
    version="1.0.0"
)

# ตั้งค่า CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Helper Functions =====

def read_image(file_content: bytes) -> np.ndarray:
    """แปลงไฟล์เป็น numpy array (RGB)"""
    image = Image.open(io.BytesIO(file_content))
    return np.array(image.convert('RGB'))


# ===== API Endpoints =====

@app.get("/")
async def root():
    """หน้าแรก"""
    return {
        "message": "🎭 Face Recognition API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "detect": "POST /detect",
            "register": "POST /register",
            "verify": "POST /verify",
            "identify": "POST /identify",
            "detect-blink": "POST /detect-blink",
            "detect-head-pose": "POST /detect-head-pose",
            "users": "GET /users",
            "delete": "DELETE /user/{user_id}"
        }
    }


@app.get("/health")
async def health_check():
    """ตรวจสอบสถานะ API"""
    return {"status": "healthy", "service": "Face Recognition API"}


@app.post("/detect")
async def detect_face(file: UploadFile = File(...)):
    """ตรวจจับใบหน้าในภาพ"""
    try:
        contents = await file.read()
        image_array = read_image(contents)
        has_face, face_count = face_system.detect_face(image_array)
        return {
            "success": True,
            "has_face": has_face,
            "face_count": face_count,
            "message": f"พบใบหน้า {face_count} คน" if has_face else "ไม่พบใบหน้า"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@app.post("/register")
async def register_face(
    user_id: str = Form(..., description="รหัสผู้ใช้"),
    file: UploadFile = File(..., description="รูปภาพใบหน้า")
):
    """ลงทะเบียนใบหน้า"""
    try:
        contents = await file.read()
        image_array = read_image(contents)
        has_face, face_count = face_system.detect_face(image_array)
        
        if not has_face:
            raise HTTPException(status_code=400, detail="❌ ไม่พบใบหน้าในภาพ")
        if face_count > 1:
            raise HTTPException(status_code=400, detail=f"❌ พบใบหน้ามากกว่า 1 คน")
            
        encoding = face_system.create_encoding(image_array)
        if encoding is None:
            raise HTTPException(status_code=400, detail="❌ ไม่สามารถประมวลผลใบหน้าได้")
        
        face_system.save_encoding(user_id, encoding)
        return {"success": True, "user_id": user_id, "message": f"✅ ลงทะเบียนสำเร็จ"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


@app.post("/identify")
async def identify_face(file: UploadFile = File(...)):
    """ระบุตัวตนจากใบหน้า (Login)"""
    try:
        contents = await file.read()
        image_array = read_image(contents)
        has_face, _ = face_system.detect_face(image_array)
        
        if not has_face:
            return {"success": True, "identified": False, "message": "ไม่พบใบหน้า"}
            
        user_id, confidence, all_matches = face_system.identify(image_array)
        return {
            "success": True,
            "identified": user_id is not None,
            "user_id": user_id,
            "confidence": confidence,
            "message": f"✅ ตรวจพบ: {user_id}" if user_id else "ไม่พบผู้ใช้ที่ตรงกัน"
        }
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-blink")
async def detect_blink(file: UploadFile = File(...)):
    """ตรวจจับการกระพริบตา"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="ไม่สามารถอ่านภาพได้")
            
        is_blinking, avg_ear, details = liveness_detector.detect_blink(image)
        return {
            "success": True,
            "is_blinking": is_blinking,
            "avg_ear": avg_ear,
            "details": details
        }
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


# ===== NEW ENDPOINT: Detect Head Pose =====

@app.post("/detect-head-pose")
async def detect_head_pose_endpoint(file: UploadFile = File(...)):
    """
    ตรวจจับการหันหน้า (Head Pose Detection)
    """
    try:
        if head_pose_detector is None:
            raise HTTPException(status_code=503, detail="Head Pose Detection ไม่พร้อมใช้งาน")
            
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="ไม่สามารถอ่านภาพได้")
            
        success, pose_info = head_pose_detector.get_head_pose(image)
        return {
            "success": success,
            "pose": pose_info
        }
    except HTTPException: raise
    except Exception as e:
        print(f"❌ Error in detect_head_pose_endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@app.get("/users")
async def list_users():
    return {"success": True, "users": face_system.list_users()}


@app.delete("/user/{user_id}")
async def delete_user(user_id: str):
    success = face_system.delete_encoding(user_id)
    if success: return {"success": True, "message": "ลบข้อมูลสำเร็จ"}
    raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้ใช้")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)