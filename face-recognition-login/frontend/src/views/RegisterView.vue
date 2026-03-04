<template>
  <div class="auth-page dark-theme">
    <div class="auth-card glass-morphism neon-border-blue" :class="{'camera-mode': step === 2}">
      <div class="icon-container neon-bg-blue" v-if="step === 1">
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
            <input type="text" v-model="form.firstName" required class="dark-input" />
          </div>
          <div class="input-group">
            <label>นามสกุล <span class="required">*</span></label>
            <input type="text" v-model="form.lastName" required class="dark-input" />
          </div>
        </div>
        
        <div class="input-group">
          <label>อีเมล <span class="required">*</span></label>
          <input type="email" v-model="form.email" placeholder="your@email.com" required class="dark-input" />
        </div>
        
        <div class="input-group">
          <label>รหัสผ่าน <span class="required">*</span></label>
          <input type="password" v-model="form.password" required class="dark-input" />
        </div>
        <div class="input-group">
          <label>ยืนยันรหัสผ่าน <span class="required">*</span></label>
          <input type="password" v-model="form.confirmPassword" required class="dark-input" />
        </div>

        <button type="submit" class="submit-btn neon-btn">ถัดไป: ถ่ายภาพใบหน้า 📸</button>
        <div class="footer-link">
          มีบัญชีแล้ว? <router-link to="/login" class="link">เข้าสู่ระบบ</router-link>
        </div>
      </form>

      <div v-if="step === 2" class="camera-container">
        <div class="video-box neon-border">
          <video v-show="!capturedImageSrc" ref="videoElement" autoplay playsinline></video>
          <img v-show="capturedImageSrc" :src="capturedImageSrc" alt="Preview" class="preview-img" />
          <div class="scan-line" v-if="!capturedImageSrc"></div>
        </div>

        <div class="action-buttons">
          <button v-if="!capturedImageSrc" class="btn-capture neon-btn" @click="capturePhoto">📸 กดเพื่อถ่ายภาพ</button>
          
          <template v-else>
            <button class="btn-retake" @click="retakePhoto">🔄 ถ่ายใหม่</button>
            <button class="btn-confirm neon-btn-green" @click="submitRegistration" :disabled="isSubmitting">
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
import { registerFace } from '@/services/api'

const router = useRouter()
const step = ref(1)
const isSubmitting = ref(false)

const form = ref({
  firstName: '', lastName: '', email: '', password: '', confirmPassword: ''
})

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
    stopCamera()
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
/* --- Dark Theme & Glassmorphism Styles --- */
.dark-theme { 
  background-color: #0f172a; 
  color: #f8fafc; 
}

.auth-page { 
  min-height: 100vh; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-family: 'Kanit', sans-serif; 
  padding: 40px 20px; 
}

.glass-morphism { 
  background: rgba(30, 41, 59, 0.7); 
  backdrop-filter: blur(10px); 
  border: 1px solid rgba(255, 255, 255, 0.1); 
}

.neon-border-blue { 
  border: 1px solid rgba(56, 189, 248, 0.3); 
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.1); 
}

.auth-card { 
  padding: 40px 30px; 
  border-radius: 20px; 
  width: 100%; 
  max-width: 450px; 
  text-align: center; 
  transition: all 0.3s ease; 
}

.auth-card.camera-mode { 
  max-width: 600px; 
}

.icon-container { 
  width: 60px; 
  height: 60px; 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  margin: 0 auto 20px; 
  color: #0f172a; 
}

.neon-bg-blue { 
  background-color: #38bdf8; 
  box-shadow: 0 0 15px #38bdf8; 
}

.title { 
  font-size: 1.8rem; 
  color: #38bdf8; 
  margin: 0 0 5px; 
  font-weight: 600; 
}

.subtitle { 
  color: #94a3b8; 
  margin-bottom: 30px; 
  font-size: 0.95rem; 
}

.text-danger { 
  color: #ef4444; 
  font-weight: bold; 
}

.form-container { 
  text-align: left; 
}

.input-group { 
  margin-bottom: 15px; 
}

.grid-2-col { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 15px; 
}

.input-group label { 
  display: block; 
  margin-bottom: 8px; 
  font-size: 0.9rem; 
  color: #94a3b8; 
  font-weight: 500; 
}

.required { 
  color: #38bdf8; 
}

/* Dark Input Style */
.dark-input { 
  width: 100%; 
  padding: 12px 15px; 
  background: rgba(15, 23, 42, 0.6); 
  border: 1px solid #334155; 
  border-radius: 8px; 
  color: white; 
  font-size: 1rem; 
  outline: none; 
  transition: border-color 0.2s; 
  box-sizing: border-box; 
}

.dark-input:focus { 
  border-color: #38bdf8; 
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); 
}

/* Button Styles */
.submit-btn, .btn-capture, .btn-confirm { 
  width: 100%; 
  border: none; 
  padding: 14px; 
  border-radius: 8px; 
  font-size: 1rem; 
  font-weight: bold; 
  cursor: pointer; 
  transition: 0.2s; 
  margin-top: 15px; 
}

.neon-btn { 
  background-color: #38bdf8; 
  color: #0f172a; 
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.3); 
}

.neon-btn:hover { 
  background-color: #7dd3fc; 
  transform: translateY(-2px); 
}

.neon-btn-green { 
  background-color: #22c55e; 
  color: white; 
  box-shadow: 0 0 15px rgba(34, 197, 94, 0.3); 
}

.btn-retake { 
  width: 100%; 
  background-color: rgba(255, 255, 255, 0.05); 
  color: #94a3b8; 
  border: 1px solid #334155; 
  padding: 14px; 
  border-radius: 8px; 
  font-size: 1rem; 
  font-weight: bold; 
  cursor: pointer; 
  margin-top: 15px; 
  margin-bottom: 10px; 
}

.btn-back { 
  background: none; 
  border: none; 
  color: #64748b; 
  text-decoration: underline; 
  margin-top: 20px; 
  cursor: pointer; 
}

.footer-link { 
  margin-top: 25px; 
  font-size: 0.9rem; 
  color: #94a3b8; 
}

.link { 
  color: #38bdf8; 
  text-decoration: none; 
  font-weight: 500; 
}

/* Camera Box Styles */
.camera-container { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
}

.video-box { 
  width: 100%; 
  aspect-ratio: 4/3; 
  background: #000; 
  border-radius: 12px; 
  overflow: hidden; 
  position: relative; 
  border: 2px solid #334155; 
}

.neon-border { 
  border-color: rgba(56, 189, 248, 0.5); 
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); 
}

.video-box video, .preview-img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
  transform: scaleX(-1); 
}

.preview-img { 
  transform: scaleX(1); 
}

.scan-line { 
  position: absolute; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 2px; 
  background: #38bdf8; 
  box-shadow: 0 0 15px #38bdf8; 
  animation: scan 2s infinite linear; 
}

@keyframes scan { 
  0% { top: 0; } 
  100% { top: 100%; } 
}

.action-buttons { 
  width: 100%; 
  display: flex; 
  flex-direction: column; 
  gap: 10px; 
}
</style>