<template>
  <div class="quick-login-page">
    <div class="container">
      <div class="header-section">
        <h1>⚡ Quick Login</h1>
        <p class="subtitle">สแกนใบหน้าอัตโนมัติพร้อมยืนยันตัวตน</p>
      </div>

      <div class="main-card">
        <div class="video-container">
          <video ref="videoElement" autoplay playsinline :class="{ 'identified-flash': identified }"></video>
          
          <div v-if="cameraActive && !livenessVerified" class="overlay-left">
            <div class="blink-status-card">
              <span class="status-label">Liveness Check</span>
              <div class="blink-dots">
                <div v-for="n in requiredBlinks" :key="n" 
                     :class="['dot', { active: n <= blinkCount }]">
                </div>
              </div>
              <p class="blink-hint">กระพริบตา {{ requiredBlinks }} ครั้ง</p>
            </div>
          </div>

          <div v-if="currentEAR !== null && cameraActive && !livenessVerified" class="overlay-right">
            <div class="ear-tag" :class="{ 'active-blink': isBlinking }">
              EAR: {{ currentEAR.toFixed(2) }}
            </div>
          </div>

          <div class="face-frame" :class="{ 'scanning-mode': scanning, 'success-mode': identified }">
            <div v-if="scanning && !identified" class="scan-line-v2"></div>
            <div v-if="identified" class="check-icon">✓</div>
          </div>

          <div v-if="cameraActive && !identified" class="instruction-bubble">
            <span :class="statusClass">{{ statusText }}</span>
          </div>
        </div>

        <div class="action-section">
          <div class="controls">
            <button v-if="!cameraActive" @click="startScanning" class="btn-primary-v2">
              เริ่มสแกนใบหน้า
            </button>
            <button v-else @click="stopScanning" class="btn-danger-v2">
              หยุดสแกน
            </button>
          </div>

          <div v-if="cameraActive" class="dashboard-grid">
            <div class="info-tile">
              <span class="tile-label">สถานะระบบ</span>
              <span class="tile-value" :class="statusClass">{{ statusText }}</span>
            </div>
            <div v-if="scanCount > 0" class="info-tile">
              <span class="tile-label">จำนวนการสแกน</span>
              <span class="tile-value">{{ scanCount }} ครั้ง</span>
            </div>
          </div>

          <div v-if="allMatches.length > 0" class="matches-container">
            <h3>ผลการวิเคราะห์ใบหน้า</h3>
            <div class="match-grid">
              <div v-for="match in allMatches" :key="match.user_id" 
                   class="match-card-v2" :class="{ 'is-identified': match.match }">
                <div class="match-info">
                  <span class="user-id">{{ match.user_id }}</span>
                  <span class="confidence-text">{{ match.confidence }}%</span>
                </div>
                <div class="progress-bg">
                  <div class="progress-fill" :style="{ width: match.confidence + '%' }"
                       :class="getMatchClass(match.confidence)"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>
        <p v-if="info" class="info-msg">{{ info }}</p>
      </div>

      <div class="footer-navigation">
        <router-link to="/login">← เข้าสู่ระบบด้วยรหัสผ่าน</router-link>
        <router-link to="/register">ลงทะเบียนสมาชิกใหม่</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { identifyFace, detectBlink } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const videoElement = ref(null)
const cameraActive = ref(false)
const scanning = ref(false)
const identified = ref(false)
const identifiedUser = ref(null)
const identifiedConfidence = ref(0)
const scanCount = ref(0)
const allMatches = ref([])
const error = ref('')
const info = ref('')

// Liveness Detection
const blinkCount = ref(0)
const requiredBlinks = ref(3)
const livenessVerified = ref(false)
const currentEAR = ref(null)
const isBlinking = ref(false)
const wasBlinking = ref(false)

let stream = null
let scanInterval = null

const statusText = computed(() => {
  if (!cameraActive.value) return 'พร้อมสแกน'
  if (identified.value) return 'ยืนยันตัวตนสำเร็จ'
  if (!livenessVerified.value) return 'กรุณากระพริบตา'
  if (scanning.value) return 'กำลังระบุตัวตน...'
  return 'กำลังวิเคราะห์'
})

const statusClass = computed(() => {
  if (identified.value) return 'success'
  if (scanning.value) return 'scanning'
  if (!livenessVerified.value) return 'waiting'
  return 'ready'
})

const startScanning = async () => {
  try {
    error.value = ''
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720, facingMode: 'user' },
      audio: false
    })
    
    if (videoElement.value) {
      videoElement.value.srcObject = stream
      cameraActive.value = true
      
      await new Promise(resolve => {
        videoElement.value.onloadeddata = resolve
      })
      
      blinkCount.value = 0
      livenessVerified.value = false
      startBlinkDetection()
    }
  } catch (err) {
    error.value = 'ไม่สามารถเข้าถึงกล้องได้'
  }
}

const stopScanning = () => {
  if (stream) stream.getTracks().forEach(track => track.stop())
  if (scanInterval) clearInterval(scanInterval)
  cameraActive.value = scanning.value = identified.value = false
  allMatches.value = []
  blinkCount.value = 0
  livenessVerified.value = false
}

const startBlinkDetection = () => {
  scanInterval = setInterval(async () => {
    if (!cameraActive.value || identified.value) return
    if (!livenessVerified.value) {
      await detectBlinkFrame()
    } else {
      await performScan()
    }
  }, 200)
}

const detectBlinkFrame = async () => {
  if (!videoElement.value) return
  try {
    const canvas = document.createElement('canvas')
    canvas.width = videoElement.value.videoWidth
    canvas.height = videoElement.value.videoHeight
    canvas.getContext('2d').drawImage(videoElement.value, 0, 0)
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8))
    
    const result = await detectBlink(blob)
    if (result.success && result.details.has_face) {
      currentEAR.value = result.avg_ear
      isBlinking.value = result.is_blinking
      if (wasBlinking.value && !isBlinking.value) {
        blinkCount.value++
        if (blinkCount.value >= requiredBlinks.value) {
          livenessVerified.value = true
          if (scanInterval) clearInterval(scanInterval)
          scanInterval = setInterval(async () => {
            if (!cameraActive.value || identified.value) return
            await performScan()
          }, 1500)
        }
      }
      wasBlinking.value = isBlinking.value
    }
  } catch (err) { console.error(err) }
}

const performScan = async () => {
  if (!videoElement.value || scanning.value) return
  scanning.value = true
  try {
    const canvas = document.createElement('canvas')
    canvas.width = videoElement.value.videoWidth
    canvas.height = videoElement.value.videoHeight
    canvas.getContext('2d').drawImage(videoElement.value, 0, 0)
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8))
    
    const result = await identifyFace(blob)
    scanCount.value++
    allMatches.value = result.all_matches || []
    
    if (result.identified) {
      identified.value = true
      identifiedUser.value = result.user_id
      identifiedConfidence.value = result.confidence
      clearInterval(scanInterval)
      setTimeout(() => {
        authStore.login(result.user_id)
        router.push('/dashboard')
      }, 2000)
    }
  } catch (err) {
    error.value = 'การเชื่อมต่อผิดพลาด'
  } finally {
    scanning.value = false
  }
}

const getMatchClass = (conf) => conf >= 80 ? 'high' : conf >= 60 ? 'medium' : 'low'

onUnmounted(() => stopScanning())
</script>

<style scoped>
/* Base Styles */
.quick-login-page {
  min-height: 100vh;
  background: #f0f2f5;
  padding: 40px 20px;
  font-family: 'Inter', sans-serif;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-section h1 { color: #1a1a1a; font-size: 2.2rem; margin: 0; }
.subtitle { color: #666; margin-top: 5px; }

/* Main Card */
.main-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.08);
  overflow: hidden;
}

/* Video Container & Overlays */
.video-container {
  position: relative;
  background: #000;
  aspect-ratio: 16 / 9;
  display: flex;
  justify-content: center;
  align-items: center;
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
  transition: opacity 0.3s;
}

.identified-flash { opacity: 0.6; }

/* Left Status Overlay */
.overlay-left {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 5;
}

.blink-status-card {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
}

.status-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; }

.blink-dots {
  display: flex;
  gap: 8px;
  margin: 8px 0;
}

.dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  transition: all 0.3s ease;
}

.dot.active {
  background: #4CAF50;
  box-shadow: 0 0 12px #4CAF50;
}

.blink-hint { font-size: 12px; margin: 0; }

/* Right Status Overlay */
.overlay-right {
  position: absolute;
  top: 20px;
  right: 20px;
}

.ear-tag {
  background: rgba(33, 150, 243, 0.9);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 12px;
  transition: transform 0.1s;
}

.active-blink { transform: scale(1.1); background: #4CAF50; }

/* Face Frame Guide */
.face-frame {
  position: absolute;
  width: 280px;
  height: 280px;
  border: 2px dashed rgba(255,255,255,0.4);
  border-radius: 50%;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanning-mode { border: 3px solid #2196F3; border-style: solid; box-shadow: 0 0 30px rgba(33, 150, 243, 0.3); }
.success-mode { border: 4px solid #4CAF50; background: rgba(76, 175, 80, 0.2); }

.scan-line-v2 {
  position: absolute;
  width: 90%;
  height: 2px;
  background: #2196F3;
  box-shadow: 0 0 15px #2196F3;
  animation: scanning 2s ease-in-out infinite;
}

@keyframes scanning {
  0%, 100% { transform: translateY(-100px); }
  50% { transform: translateY(100px); }
}

.check-icon { font-size: 80px; color: white; }

/* Instruction Bubble */
.instruction-bubble {
  position: absolute;
  bottom: 25px;
  background: white;
  padding: 10px 24px;
  border-radius: 50px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  font-weight: 700;
  z-index: 10;
}

/* Action Section */
.action-section { padding: 30px; }

.controls { display: flex; justify-content: center; margin-bottom: 25px; }

.btn-primary-v2 {
  background: #2196F3;
  color: white;
  padding: 16px 48px;
  border-radius: 16px;
  border: none;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary-v2:hover { background: #1976D2; transform: translateY(-2px); }

.btn-danger-v2 {
  background: #ffeded;
  color: #d32f2f;
  padding: 12px 30px;
  border-radius: 12px;
  border: 1px solid #ffcdd2;
  cursor: pointer;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 30px;
}

.info-tile {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
}

.tile-label { font-size: 12px; color: #888; margin-bottom: 4px; }
.tile-value { font-weight: 700; color: #333; }
.tile-value.success { color: #4CAF50; }
.tile-value.scanning { color: #2196F3; }

/* Matches Results */
.matches-container h3 { font-size: 1rem; color: #444; margin-bottom: 15px; }

.match-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.match-card-v2 {
  background: white;
  border: 1px solid #eee;
  padding: 12px;
  border-radius: 12px;
}

.match-card-v2.is-identified { border-color: #4CAF50; background: #f1f8e9; }

.match-info { display: flex; justify-content: space-between; margin-bottom: 8px; }
.user-id { font-weight: 600; font-size: 14px; }
.confidence-text { font-size: 12px; color: #666; }

.progress-bg { height: 6px; background: #eee; border-radius: 10px; overflow: hidden; }
.progress-fill { height: 100%; transition: width 0.5s ease; }
.progress-fill.high { background: #4CAF50; }
.progress-fill.medium { background: #FF9800; }
.progress-fill.low { background: #f44336; }

/* Utils */
.error-msg { text-align: center; color: #d32f2f; background: #ffebee; padding: 10px; border-radius: 8px; }
.info-msg { text-align: center; color: #1976d2; margin-top: 10px; }

.footer-navigation {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
}

.footer-navigation a { color: #2196F3; text-decoration: none; font-size: 14px; font-weight: 500; }

@media (max-width: 600px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .video-container { aspect-ratio: 4 / 3; }
}
</style>