# backend/face_utils.py - ฟังก์ชันสำหรับจัดการ Face Recognition

import face_recognition
import numpy as np
import os
import pickle
from typing import Optional, Tuple, List
import config

class FaceSystem:
    """ระบบจัดการ Face Recognition"""
    
    def __init__(self):
        self.encodings_path = config.FACE_ENCODINGS_PATH
        self.tolerance = config.FACE_RECOGNITION_TOLERANCE
        
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        os.makedirs(self.encodings_path, exist_ok=True)
    
    def detect_face(self, image_array: np.ndarray) -> Tuple[bool, int]:
        """
        ตรวจจับใบหน้าในภาพ
        
        Args:
            image_array: ภาพในรูปแบบ numpy array (RGB)
        
        Returns:
            (มีใบหน้าหรือไม่, จำนวนใบหน้า)
        """
        face_locations = face_recognition.face_locations(image_array)
        face_count = len(face_locations)
        return face_count > 0, face_count
    
    def create_encoding(self, image_array: np.ndarray) -> Optional[np.ndarray]:
        """
        สร้าง face encoding จากภาพ
        
        Args:
            image_array: ภาพในรูปแบบ numpy array (RGB)
        
        Returns:
            face encoding หรือ None ถ้าไม่พบใบหน้า
        """
        try:
            encodings = face_recognition.face_encodings(image_array)
            
            if len(encodings) == 0:
                return None
            
            # ใช้ใบหน้าแรกที่พบ
            return encodings[0]
            
        except Exception as e:
            print(f"❌ Error creating encoding: {e}")
            return None
    
    def save_encoding(self, user_id: str, encoding: np.ndarray):
        """บันทึก face encoding ลงไฟล์"""
        file_path = os.path.join(self.encodings_path, f"{user_id}.pkl")
        
        with open(file_path, 'wb') as f:
            pickle.dump(encoding, f)
        
        print(f"✅ บันทึก encoding สำหรับ {user_id}")
    
    def load_encoding(self, user_id: str) -> Optional[np.ndarray]:
        """โหลด face encoding จากไฟล์"""
        file_path = os.path.join(self.encodings_path, f"{user_id}.pkl")
        
        if not os.path.exists(file_path):
            print(f"❌ ไม่พบข้อมูลของ {user_id}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                encoding = pickle.load(f)
            print(f"✅ โหลด encoding สำหรับ {user_id}")
            return encoding
            
        except Exception as e:
            print(f"❌ Error loading encoding: {e}")
            return None
    
    def verify(self, image_array: np.ndarray, user_id: str) -> Tuple[bool, float]:
        """
        ยืนยันใบหน้ากับข้อมูลที่บันทึกไว้
        
        Args:
            image_array: ภาพที่จะตรวจสอบ
            user_id: รหัสผู้ใช้
        
        Returns:
            (ตรงกันหรือไม่, ค่า confidence 0-100)
        """
        # โหลดข้อมูลเดิม
        saved_encoding = self.load_encoding(user_id)
        if saved_encoding is None:
            return False, 0.0
        
        # สร้าง encoding จากภาพใหม่
        new_encoding = self.create_encoding(image_array)
        if new_encoding is None:
            return False, 0.0
        
        # คำนวณระยะห่างระหว่างใบหน้า (ยิ่งน้อยยิ่งคล้าย)
        distance = face_recognition.face_distance([saved_encoding], new_encoding)[0]
        
        # ตรวจสอบว่าตรงกันหรือไม่
        is_match = distance <= self.tolerance
        
        # แปลงเป็นค่า confidence (0-100%)
        confidence = (1 - distance) * 100
        
        return is_match, round(confidence, 2)
    
    def delete_encoding(self, user_id: str) -> bool:
        """ลบข้อมูล face encoding"""
        file_path = os.path.join(self.encodings_path, f"{user_id}.pkl")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ ลบข้อมูลของ {user_id}")
            return True
        
        return False
    
    def list_users(self) -> list:
        """แสดงรายชื่อผู้ใช้ทั้งหมดที่ลงทะเบียน"""
        files = os.listdir(self.encodings_path)
        users = [f.replace('.pkl', '') for f in files if f.endswith('.pkl')]
        return users
    
    # ===== ฟังก์ชันใหม่: Identify (Real-time Login) =====
    
    def load_all_encodings(self) -> dict:
        """
        โหลด face encodings ของผู้ใช้ทั้งหมด
        Returns: {user_id: encoding}
        """
        all_encodings = {}
        users = self.list_users()
        
        for user_id in users:
            encoding = self.load_encoding(user_id)
            if encoding is not None:
                all_encodings[user_id] = encoding
        
        return all_encodings
    
    def identify(self, image_array: np.ndarray) -> Tuple[Optional[str], float, List[dict]]:
        """
        ระบุตัวตนจากใบหน้า (ค้นหาว่าเป็นใคร)
        
        Args:
            image_array: ภาพที่จะตรวจสอบ
        
        Returns:
            (user_id, confidence, all_matches)
            - user_id: ผู้ใช้ที่ตรงกันมากที่สุด (หรือ None)
            - confidence: ความมั่นใจ 0-100
            - all_matches: รายชื่อผู้ใช้ทั้งหมดที่ใกล้เคียง
        """
        # สร้าง encoding จากภาพ
        face_encoding = self.create_encoding(image_array)
        if face_encoding is None:
            return None, 0.0, []
        
        # โหลด encodings ทั้งหมด
        all_encodings = self.load_all_encodings()
        
        if len(all_encodings) == 0:
            return None, 0.0, []
        
        # คำนวณระยะห่างกับทุกคน
        results = []
        for user_id, saved_encoding in all_encodings.items():
            distance = face_recognition.face_distance([saved_encoding], face_encoding)[0]
            confidence = (1 - distance) * 100
            
            # แปลง numpy types เป็น Python types
            results.append({
                'user_id': user_id,
                'confidence': round(float(confidence), 2),
                'distance': float(distance),
                'match': bool(distance <= self.tolerance)
            })
        
        # เรียงตาม confidence (สูงสุดก่อน)
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # คนที่ตรงกันมากที่สุด
        best_match = results[0]
        
        if best_match['match']:
            return best_match['user_id'], best_match['confidence'], results
        else:
            return None, best_match['confidence'], results


# สร้าง instance
face_system = FaceSystem()