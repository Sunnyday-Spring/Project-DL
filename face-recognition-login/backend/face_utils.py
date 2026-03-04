import face_recognition
import numpy as np
import os
import pickle
from typing import Optional, Tuple, List, Dict
import config
from ultralytics import YOLO

class FaceSystem:
    def __init__(self):
        self.encodings_path = config.FACE_ENCODINGS_PATH
        self.tolerance = config.FACE_RECOGNITION_TOLERANCE
        
        # โหลด YOLOv11
        model_name = 'best.pt' if os.path.exists('best.pt') else 'yolo11n.pt'
        print(f"🔄 กำลังโหลดโมเดล: {model_name}")
        self.hat_model = YOLO(model_name)
        
        os.makedirs(self.encodings_path, exist_ok=True)
    
    def detect_objects_and_hat(self, image_array: np.ndarray) -> Tuple[bool, List[Dict]]:
        """ตรวจจับเฉพาะ 'หมวก' และคืนค่าพิกัดกรอบ (ตัดวัตถุอื่นทิ้งทั้งหมด)"""
        try:
            results = self.hat_model(image_array, verbose=False)[0]
            detected_boxes = []
            hat_detected = False
            
            for box in results.boxes:
                class_id = int(box.cls[0])
                # ดึงชื่อคลาสที่ AI พ่นออกมาจริงๆ
                original_label = results.names[class_id]
                
                # 🔴 1. เคลียร์ชื่อให้สะอาด (ลบตัวใหญ่ เปลี่ยน - หรือ _ เป็นช่องว่าง)
                clean_label = original_label.lower().replace('-', ' ').replace('_', ' ')
                
                confidence = float(box.conf[0])
                coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]
                
                # 1. กรองความมั่นใจ: ตั้งไว้ที่ 15% ชั่วคราวเพื่อให้โมเดลใหม่จับได้ง่ายขึ้น
                if confidence < 0.60:
                    continue
                
                # 🔴 2. เช็คว่าเป็นหมวกหรือไม่แบบฉลาด (Smart Keyword)
                hat_keywords = ['cap', 'helmet', 'baseball','hat']
                
                # ถ้าคำใดคำหนึ่งใน hat_keywords ไปโผล่อยู่ในชื่อที่ AI ส่งมา ถือว่าเป็นหมวกทันที!
                is_hat = any(keyword in clean_label for keyword in hat_keywords)
                
                # 3. สำคัญที่สุด: ถ้า "ไม่ใช่หมวก" ให้ข้ามไปเลย ไม่ต้องนำไปวาดกรอบ!
                if not is_hat:
                    continue
                
                # ถ้าผ่านมาถึงตรงนี้ แสดงว่าเป็น "หมวก" 
                hat_detected = True
                
                # พิมพ์ลง Terminal เพื่อให้ตรวจสอบได้ว่า AI ตัวใหม่มันแอบเรียกหมวกว่าอะไร
                print(f"   -> 🟢 เจอหมวก: '{original_label}' (ความมั่นใจ: {confidence*100:.2f}%)")
                
                detected_boxes.append({
                    "coords": coords,
                    "label": "HAT", # บังคับให้แสดงคำว่า HAT บนหน้าจอเลย จะได้ดูเป็นระเบียบ
                    "confidence": round(confidence, 2),
                    "is_hat": True
                })
            
            return hat_detected, detected_boxes
        except Exception as e:
            print(f"❌ Error in detection: {e}")
            return False, []

    def detect_face_with_boxes(self, image_array: np.ndarray) -> List[Dict]:
        """คืนค่าพิกัดใบหน้าสำหรับวาดบน UI (จับหน้าอย่างเดียว)"""
        face_locations = face_recognition.face_locations(image_array)
        face_boxes = []
        for (top, right, bottom, left) in face_locations:
            face_boxes.append({
                "coords": [left, top, right, bottom],
                "label": "FACE",
                "confidence": 1.0,
                "is_hat": False
            })
        return face_boxes

    def create_encoding(self, image_array: np.ndarray) -> Optional[np.ndarray]:
        try:
            encodings = face_recognition.face_encodings(image_array)
            return encodings[0] if len(encodings) > 0 else None
        except Exception as e:
            print(f"❌ Error creating encoding: {e}")
            return None

    def save_encoding(self, user_id: str, encoding: np.ndarray):
        file_path = os.path.join(self.encodings_path, f"{user_id}.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(encoding, f)

    def load_encoding(self, user_id: str) -> Optional[np.ndarray]:
        file_path = os.path.join(self.encodings_path, f"{user_id}.pkl")
        if not os.path.exists(file_path): return None
        try:
            with open(file_path, 'rb') as f: return pickle.load(f)
        except: return None

    def load_all_encodings(self) -> dict:
        all_encodings = {}
        files = os.listdir(self.encodings_path)
        users = [f.replace('.pkl', '') for f in files if f.endswith('.pkl')]
        for user_id in users:
            encoding = self.load_encoding(user_id)
            if encoding is not None: all_encodings[user_id] = encoding
        return all_encodings

    def identify(self, image_array: np.ndarray) -> Tuple[Optional[str], float, List[dict]]:
        face_encoding = self.create_encoding(image_array)
        if face_encoding is None: return None, 0.0, []
        all_encodings = self.load_all_encodings()
        if len(all_encodings) == 0: return None, 0.0, []
        results = []
        for user_id, saved_encoding in all_encodings.items():
            distance = face_recognition.face_distance([saved_encoding], face_encoding)[0]
            confidence = (1 - distance) * 100
            results.append({
                'user_id': user_id,
                'confidence': round(float(confidence), 2),
                'match': bool(distance <= self.tolerance)
            })
        results.sort(key=lambda x: x['confidence'], reverse=True)
        best_match = results[0]
        if best_match['match']: return best_match['user_id'], best_match['confidence'], results
        return None, best_match['confidence'], results

# สร้าง Instance
face_system = FaceSystem()