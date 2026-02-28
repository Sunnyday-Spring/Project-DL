# backend/main.py
import cv2 
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io
import traceback

# Import ส่วนประกอบเดิมของระบบ
from liveness_detection import liveness_detector, head_pose_detector
from face_utils import face_system
import config

# สร้าง FastAPI app
app = FastAPI(
    title="Face Recognition & Hat Detection API",
    description="API สำหรับระบบ Login ด้วยใบหน้าและการตรวจสอบการสวมหมวกแบบ Real-time",
    version="1.2.0"
)

# ตั้งค่า CORS เพื่อให้ Frontend (Vue.js) เรียกใช้งานได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # อนุญาตทุก origin ชั่วคราวเพื่อให้เทสได้ง่าย
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Helper Functions =====

def read_image(file_content: bytes) -> np.ndarray:
    """แปลงไบนารีไฟล์ภาพให้เป็น numpy array (RGB) สำหรับประมวลผล"""
    image = Image.open(io.BytesIO(file_content))
    return np.array(image.convert('RGB'))

def check_lighting(image_array: np.ndarray) -> str:
    """ตรวจสอบความสว่างของภาพเพื่อแนะนำผู้ใช้งาน"""
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    brightness = np.mean(gray)
    
    if brightness < 60:
        return "TOO_DARK"    # แสงมืดเกินไป
    elif brightness > 230:
        return "TOO_BRIGHT"  # แสงจ้า/ย้อนแสง
    return "NORMAL"          # แสงปกติ

# ===== API Endpoints =====

@app.get("/")
async def root():
    return {
        "message": "🎭 Face & Hat Recognition API",
        "status": "online",
        "version": "1.2.0"
    }

@app.post("/identify")
async def identify_face(file: UploadFile = File(...)):
    """
    Endpoint สำหรับ Login:
    1. เช็คแสงสว่าง
    2. ตรวจจับหมวกและใบหน้า
    3. ระบุตัวตน (Face Recognition)
    """
    try:
        contents = await file.read()
        image_array = read_image(contents)
        
        # 1. เช็คสภาพแสง
        lighting_status = check_lighting(image_array)
        
        # 2. ตรวจจับหมวกและดึงพิกัดกรอบจาก YOLO
        hat_detected, object_boxes = face_system.detect_objects_and_hat(image_array)
        
        # 3. ตรวจจับใบหน้าและดึงพิกัดกรอบจาก Face Recognition
        face_boxes = face_system.detect_face_with_boxes(image_array)
        
        # 4. ประมวลผลระบุตัวตน (ค้นหาว่าใบหน้าตรงกับใคร)
        user_id, confidence, all_matches = face_system.identify(image_array)
        
        # อัปเดตข้อความบนกรอบใบหน้าให้แสดงชื่อและความมั่นใจ
        if len(face_boxes) > 0:
            if user_id is not None:
                face_boxes[0]["label"] = f"{user_id.upper()} ({int(confidence)}%)"
            else:
                face_boxes[0]["label"] = "UNKNOWN FACE"
        
        # รวมกรอบทั้งหมด
        all_ui_boxes = object_boxes + face_boxes
        
        # กรณีไม่พบใบหน้าในภาพ
        if len(face_boxes) == 0:
            return {
                "success": True, 
                "identified": False, 
                "message": "ไม่พบใบหน้าในกล้อง",
                "lighting_status": lighting_status,
                "details": {
                    "hat_detected": hat_detected,
                    "boxes": all_ui_boxes
                }
            }
            
        # ตรวจสอบเงื่อนไขการ Login (ต้องมีชื่อผู้ใช้ และ ต้องใส่หมวก)
        is_identified = False
        if user_id is not None and hat_detected:
            is_identified = True
            message = f"✅ ยืนยันตัวตนสำเร็จ: {user_id}"
        elif user_id is not None and not hat_detected:
            message = "⚠️ พบใบหน้า แต่กรุณาสวมหมวกเพื่อเข้าใช้งาน"
        else:
            message = "❌ ไม่พบข้อมูลผู้ใช้นี้ในระบบ"

        return {
            "success": True,
            "identified": is_identified,
            "user_id": user_id,
            "confidence": confidence,
            "all_matches": all_matches,
            "message": message,
            "lighting_status": lighting_status, # ส่งสถานะแสงกลับไปให้ Vue
            "details": {
                "hat_detected": hat_detected,
                "boxes": all_ui_boxes 
            }
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register")
async def register_face(
    user_id: str = Form(..., description="รหัสผู้ใช้"),
    file: UploadFile = File(..., description="รูปภาพใบหน้า")
):
    """ลงทะเบียนใบหน้าใหม่"""
    try:
        contents = await file.read()
        image_array = read_image(contents)
        
        # 🔴 จุดที่แก้ไข: เช็คใบหน้าด้วย detect_face_with_boxes แทน
        face_boxes = face_system.detect_face_with_boxes(image_array)
        face_count = len(face_boxes)
        
        if face_count == 0:
            raise HTTPException(status_code=400, detail="❌ ไม่พบใบหน้าในภาพ")
        if face_count > 1:
            raise HTTPException(status_code=400, detail="❌ พบใบหน้ามากกว่า 1 คน")
            
        encoding = face_system.create_encoding(image_array)
        if encoding is None:
            raise HTTPException(status_code=400, detail="❌ ไม่สามารถประมวลผลใบหน้าได้")
        
        face_system.save_encoding(user_id, encoding)
        return {"success": True, "user_id": user_id, "message": "✅ ลงทะเบียนสำเร็จ"}
    except HTTPException: 
        raise
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-blink")
async def detect_blink(file: UploadFile = File(...)):
    """ตรวจจับการกระพริบตา (เผื่อเปิดใช้งานในอนาคต)"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="อ่านภาพไม่ได้")
            
        is_blinking, avg_ear, details = liveness_detector.detect_blink(image)
        return {
            "success": True,
            "is_blinking": is_blinking,
            "avg_ear": avg_ear,
            "details": details
        }
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
async def list_users():
    return {"success": True, "users": face_system.list_users()}

@app.delete("/user/{user_id}")
async def delete_user(user_id: str):
    success = face_system.delete_encoding(user_id)
    if success: return {"success": True, "message": "ลบข้อมูลสำเร็จ"}
    raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)