<template>
  <div class="auth-page">
    <div class="auth-card" :class="{'camera-mode': step === 2}">
      <div class="icon-container" v-if="step === 1">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shield-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
      </div>
      
      <h1 class="title">{{ step === 1 ? 'ลงทะเบียน' : 'ถ่ายภาพยืนยันตัวตน' }}</h1>
      <p class="subtitle" :class="{'text-danger': step === 2}">
        {{ step === 1 ? 'สร้างบัญชีใหม่เพื่อเริ่มต้นใช้งาน' : '⚠️ กรุณาถอดหมวกและมองตรงมาที่กล้อง' }}
      </p>

      <form v-if="step === 1" @submit.prevent="goToCameraStep" class="form-container">
        
        <div class="grid-2-col">
          <div class="input-group">
            <label>ชื่อ <span class="required">*</span></label>
            <input type="text" v-model="form.firstName" required />
          </div>
          <div class="input-group">
            <label>นามสกุล <span class="required">*</span></label>
            <input type="text" v-model="form.lastName" required />
          </div>
        </div>
        
        <div class="input-group">
          <label>อีเมล <span class="required">*</span></label>
          <input type="email" v-model="form.email" placeholder="your@email.com" required />
        </div>
        
        <div class="input-group">
          <label>รหัสผ่าน <span class="required">*</span></label>
          <input type="password" v-model="form.password" required />
        </div>
        <div class="input-group">
          <label>ยืนยันรหัสผ่าน <span class="required">*</span></label>
          <input type="password" v-model="form.confirmPassword" required />
        </div>

        <button type="submit" class="submit-btn">ถัดไป: ถ่ายภาพใบหน้า 📸</button>
        <div class="footer-link">
          มีบัญชีแล้ว? <router-link to="/login" class="link">เข้าสู่ระบบ</router-link>
        </div>
      </form>

      <div v-if="step === 2" class="camera-container">
        <div class="video-box">
          <video v-show="!capturedImageSrc" ref="videoElement" autoplay playsinline></video>
          <img v-show="capturedImageSrc" :src="capturedImageSrc" alt="Preview" class="preview-img" />
        </div>

        <div class="action-buttons">
          <button v-if="!capturedImageSrc" class="btn-capture" @click="capturePhoto">📸 กดเพื่อถ่ายภาพ</button>
          
          <template v-else>
            <button class="btn-retake" @click="retakePhoto">🔄 ถ่ายใหม่</button>
            <button class="btn-confirm" @click="submitRegistration" :disabled="isSubmitting">
              {{ isSubmitting ? 'กำลังบันทึกข้อมูล...' : '✅ ยืนยันการลงทะเบียน' }}
            </button>
          </template>
        </div>
        
        <button v-if="!isSubmitting" class="btn-back" @click="step = 1; stopCamera()">⬅️ กลับไปแก้ไขข้อมูล</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { registerFace } from '@/services/api' // โหลดฟังก์ชันจาก api.js

const router = useRouter()
const step = ref(1)
const isSubmitting = ref(false)

// 🔴 อัปเดตตัวแปร form ให้เก็บ email แทน
const form = ref({
  firstName: '', lastName: '', email: '', password: '', confirmPassword: ''
})

// Camera variables
const videoElement = ref(null)
const capturedBlob = ref(null)
const capturedImageSrc = ref(null)
let stream = null

const goToCameraStep = () => {
  if (form.value.password !== form.value.confirmPassword) {
    alert('รหัสผ่านไม่ตรงกัน!')
    return
  }
  step.value = 2
  startCamera()
}

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { ideal: 720 } })
    if (videoElement.value) {
      videoElement.value.srcObject = stream
    }
  } catch (err) {
    alert("ไม่สามารถเปิดกล้องได้ กรุณาอนุญาตการใช้งานกล้อง")
  }
}

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
}

const capturePhoto = () => {
  const canvas = document.createElement('canvas')
  canvas.width = videoElement.value.videoWidth
  canvas.height = videoElement.value.videoHeight
  canvas.getContext('2d').drawImage(videoElement.value, 0, 0)
  
  canvas.toBlob((blob) => {
    capturedBlob.value = blob
    capturedImageSrc.value = URL.createObjectURL(blob)
    stopCamera() // หยุดกล้องตอนโชว์พรีวิว
  }, 'image/jpeg', 0.9)
}

const retakePhoto = () => {
  capturedBlob.value = null
  capturedImageSrc.value = null
  startCamera()
}

const submitRegistration = async () => {
  if (!capturedBlob.value) return
  isSubmitting.value = true
  
  try {
    // 🔴 ใช้อีเมลเป็น user_id ส่งไปให้ Face Recognition
    const userId = form.value.email
    const res = await registerFace(userId, capturedBlob.value)
    
    alert(res.message || "✅ ลงทะเบียนสำเร็จ!")
    router.push('/login')
  } catch (error) {
    console.error(error)
    alert("❌ เกิดข้อผิดพลาดในการลงทะเบียน (ตรวจสอบที่ Backend)")
  } finally {
    isSubmitting.value = false
  }
}

onUnmounted(() => {
  stopCamera()
})
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background-color: #f8faff; font-family: 'Kanit', sans-serif; padding: 40px 20px; }
.auth-card { background: white; padding: 40px 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); width: 100%; max-width: 450px; text-align: center; transition: all 0.3s ease; }
.auth-card.camera-mode { max-width: 600px; }
.icon-container { width: 60px; height: 60px; background-color: #9333ea; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; color: white; }
.title { font-size: 1.8rem; color: #1e293b; margin: 0 0 5px; font-weight: 600; }
.subtitle { color: #64748b; margin-bottom: 30px; font-size: 0.95rem; }
.text-danger { color: #ef4444; font-weight: bold; }
.form-container { text-align: left; }
.input-group { margin-bottom: 15px; }
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.input-group label { display: block; margin-bottom: 8px; font-size: 0.9rem; color: #334155; font-weight: 500; }
.required { color: #9333ea; }
.input-group input { width: 100%; padding: 12px 15px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.2s; box-sizing: border-box; }
.input-group input:focus { border-color: #9333ea; }
.submit-btn, .btn-capture, .btn-confirm { width: 100%; background-color: #9333ea; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 15px; }
.submit-btn:hover, .btn-capture:hover, .btn-confirm:hover { background-color: #7e22ce; }
.btn-retake { width: 100%; background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 14px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; margin-top: 15px; margin-bottom: 10px; }
.btn-back { background: none; border: none; color: #64748b; text-decoration: underline; margin-top: 20px; cursor: pointer; }
.footer-link { margin-top: 25px; font-size: 0.9rem; color: #475569; }
.link { color: #9333ea; text-decoration: none; font-weight: 500; }
.camera-container { display: flex; flex-direction: column; align-items: center; }
.video-box { width: 100%; aspect-ratio: 4/3; background: #000; border-radius: 12px; overflow: hidden; position: relative; }
.video-box video, .preview-img { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
.preview-img { transform: scaleX(1); }
.action-buttons { width: 100%; display: flex; flex-direction: column; gap: 10px; }
</style>