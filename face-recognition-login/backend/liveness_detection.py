# backend/liveness_detection.py

import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from typing import Tuple, Optional, Dict
import os

class LivenessDetector:
    """ตรวจจับว่าเป็นคนจริงผ่านการกระพริบตา"""
    
    def __init__(self, shape_predictor_path: str = "models/shape_predictor_68_face_landmarks.dat"):
        if not os.path.exists(shape_predictor_path):
            raise FileNotFoundError(
                f"ไม่พบไฟล์ {shape_predictor_path}\n"
                "โหลดได้จาก: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            )
        
        print(f"✅ โหลด shape predictor จาก: {shape_predictor_path}")
        
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(shape_predictor_path)
        
        self.LEFT_EYE_INDICES = list(range(42, 48))
        self.RIGHT_EYE_INDICES = list(range(36, 42))
        self.EAR_THRESHOLD = 0.25
        
        print("✅ Liveness Detector พร้อมใช้งาน")
    
    def eye_aspect_ratio(self, eye_landmarks: np.ndarray) -> float:
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        ear = (A + B) / (2.0 * C)
        return float(ear)
    
    def get_facial_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray, 0)
            
            if len(faces) == 0:
                return None
            
            face = faces[0]
            shape = self.predictor(gray, face)
            landmarks = np.array([[p.x, p.y] for p in shape.parts()])
            
            return landmarks
        except Exception as e:
            print(f"❌ Error in get_facial_landmarks: {e}")
            return None
    
    def detect_blink(self, image: np.ndarray) -> Tuple[bool, float, dict]:
        try:
            landmarks = self.get_facial_landmarks(image)
            
            if landmarks is None:
                return False, 0.0, {
                    'has_face': False,
                    'left_ear': 0.0,
                    'right_ear': 0.0,
                    'message': 'ไม่พบใบหน้า'
                }
            
            left_eye = landmarks[self.LEFT_EYE_INDICES]
            right_eye = landmarks[self.RIGHT_EYE_INDICES]
            
            left_ear = self.eye_aspect_ratio(left_eye)
            right_ear = self.eye_aspect_ratio(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0
            is_blinking = avg_ear < self.EAR_THRESHOLD
            
            details = {
                'has_face': True,
                'left_ear': round(float(left_ear), 3),
                'right_ear': round(float(right_ear), 3),
                'avg_ear': round(float(avg_ear), 3),
                'threshold': float(self.EAR_THRESHOLD),
                'is_blinking': bool(is_blinking),
                'message': 'กระพริบตา' if is_blinking else 'ลืมตา'
            }
            
            return bool(is_blinking), float(avg_ear), details
            
        except Exception as e:
            print(f"❌ Error in detect_blink: {e}")
            return False, 0.0, {
                'has_face': False,
                'error': str(e),
                'message': 'เกิดข้อผิดพลาด'
            }


# ===== NEW: Head Pose Detector =====

class HeadPoseDetector:
    """ตรวจจับการหันหน้าซ้าย-ขวา"""
    
    def __init__(self, shape_predictor_path: str = "models/shape_predictor_68_face_landmarks.dat"):
        if not os.path.exists(shape_predictor_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ {shape_predictor_path}")
        
        print(f"✅ โหลด shape predictor สำหรับ Head Pose")
        
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(shape_predictor_path)
        
        # 3D model points (จุดอ้างอิงใบหน้าใน 3D space)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip (30)
            (0.0, -330.0, -65.0),        # Chin (8)
            (-225.0, 170.0, -135.0),     # Left eye left corner (36)
            (225.0, 170.0, -135.0),      # Right eye right corner (45)
            (-150.0, -150.0, -125.0),    # Left mouth corner (48)
            (150.0, -150.0, -125.0)      # Right mouth corner (54)
        ], dtype=np.float64)
        
        # Thresholds สำหรับตรวจจับการหันหน้า
        self.YAW_THRESHOLD_LEFT = -15   # หันซ้าย (องศา)
        self.YAW_THRESHOLD_RIGHT = 15   # หันขวา (องศา)
        self.YAW_CENTER_RANGE = 10      # กลาง ±10 องศา
        
        print("✅ Head Pose Detector พร้อมใช้งาน")
    
    def get_facial_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """หาจุด landmarks 68 จุด"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray, 0)
            
            if len(faces) == 0:
                return None
            
            face = faces[0]
            shape = self.predictor(gray, face)
            landmarks = np.array([[p.x, p.y] for p in shape.parts()])
            
            return landmarks
        except Exception as e:
            print(f"❌ Error in get_facial_landmarks: {e}")
            return None
    
    def get_head_pose(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """
        คำนวณมุมการหันหน้า
        
        Returns:
            (success, pose_info)
            pose_info = {
                'yaw': มุมซ้าย-ขวา,
                'pitch': มุมขึ้น-ลง,
                'roll': มุมเอียง,
                'direction': 'left'/'right'/'center'/'unknown',
                'message': ข้อความอธิบาย
            }
        """
        try:
            landmarks = self.get_facial_landmarks(image)
            
            if landmarks is None:
                return False, {
                    'has_face': False,
                    'yaw': 0.0,
                    'pitch': 0.0,
                    'roll': 0.0,
                    'direction': 'unknown',
                    'message': 'ไม่พบใบหน้า'
                }
            
            # ดึงจุดสำคัญ 6 จุด (ตาม model_points)
            image_points = np.array([
                landmarks[30],    # Nose tip
                landmarks[8],     # Chin
                landmarks[36],    # Left eye left corner
                landmarks[45],    # Right eye right corner
                landmarks[48],    # Left mouth corner
                landmarks[54]     # Right mouth corner
            ], dtype=np.float64)
            
            # Camera matrix (approximate)
            size = image.shape
            focal_length = size[1]
            center = (size[1] / 2, size[0] / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            
            # Distortion coefficients (assume no lens distortion)
            dist_coeffs = np.zeros((4, 1))
            
            # solvePnP - หามุมการหมุนของศีรษะ
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if not success:
                return False, {
                    'has_face': True,
                    'yaw': 0.0,
                    'pitch': 0.0,
                    'roll': 0.0,
                    'direction': 'unknown',
                    'message': 'ไม่สามารถคำนวณมุมได้'
                }
            
            # แปลง rotation vector เป็น rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # คำนวณมุม Euler angles
            # Yaw = การหันซ้าย-ขวา
            # Pitch = การพยักหน้า
            # Roll = การเอียงศีรษะ
            
            sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
            singular = sy < 1e-6
            
            if not singular:
                yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
                pitch = np.arctan2(-rotation_matrix[2, 0], sy)
                roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            else:
                yaw = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
                pitch = np.arctan2(-rotation_matrix[2, 0], sy)
                roll = 0
            
            # แปลงเป็นองศา
            yaw_deg = float(np.degrees(yaw))
            pitch_deg = float(np.degrees(pitch))
            roll_deg = float(np.degrees(roll))
            
            # กำหนดทิศทางการหันหน้า
            if yaw_deg < self.YAW_THRESHOLD_LEFT:
                direction = 'left'
                message = 'หันซ้าย'
            elif yaw_deg > self.YAW_THRESHOLD_RIGHT:
                direction = 'right'
                message = 'หันขวา'
            elif abs(yaw_deg) < self.YAW_CENTER_RANGE:
                direction = 'center'
                message = 'หันตรง'
            else:
                direction = 'unknown'
                message = 'ไม่ชัดเจน'
            
            pose_info = {
                'has_face': True,
                'yaw': round(yaw_deg, 2),
                'pitch': round(pitch_deg, 2),
                'roll': round(roll_deg, 2),
                'direction': direction,
                'message': message
            }
            
            return True, pose_info
            
        except Exception as e:
            print(f"❌ Error in get_head_pose: {e}")
            import traceback
            traceback.print_exc()
            return False, {
                'has_face': False,
                'error': str(e),
                'message': 'เกิดข้อผิดพลาด'
            }


# สร้าง instances
try:
    liveness_detector = LivenessDetector()
    head_pose_detector = HeadPoseDetector()
except FileNotFoundError as e:
    print(f"⚠️  Warning: {e}")
    print("⚠️  Liveness Detection และ Head Pose Detection จะไม่สามารถใช้งานได้")
    liveness_detector = None
    head_pose_detector = None