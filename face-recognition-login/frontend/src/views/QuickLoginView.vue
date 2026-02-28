<template>
  <div class="quick-login-page dark-theme">
    <div class="container">
      <div class="header-section">
        <div class="header-logo">🛡️</div>
        <h1>SECURE ACCESS</h1>
        <p class="subtitle">FACE & HELMET COMPLIANCE SYSTEM</p>
      </div>

      <div class="main-layout glass-morphism">
        <div class="video-section">
          <div class="video-container neon-border" :class="{ 'scanning-active': scanning }">
            <video ref="videoElement" autoplay playsinline :class="{ 'identified-flash': identified }" />
            
            <canvas ref="overlayCanvas" class="overlay-canvas"></canvas>
            
            <div v-if="cameraActive" class="env-alerts">
              <div v-if="lightingStatus === 'TOO_DARK'" class="alert-item warning">⚠️ แสงมืดเกินไป</div>
              <div v-if="lightingStatus === 'TOO_BRIGHT'" class="alert-item warning">⚠️ แสงจ้า/ย้อนแสง</div>
              <div v-if="!hatDetected" class="alert-item danger">🚫 ไม่พบหมวก</div>
            </div>

            <div class="status-bar-overlay">
              <span class="status-dot" :class="statusClass"></span>
              {{ statusText }}
            </div>
          </div>
        </div>

        <div class="side-panel">
          <div class="control-box">
            <button v-if="!cameraActive" class="btn-start" @click="startScanning">เปิดระบบสแกน</button>
            <button v-else class="btn-stop" @click="stopScanning">ปิดกล้อง</button>
          </div>

          <div class="metrics-stack">
            <div class="info-card" :class="hatDetected ? 'success-border' : 'danger-border'">
              <span class="label">การสวมหมวก</span>
              <span class="value" :class="hatDetected ? 'text-green' : 'text-danger'">
                {{ hatDetected ? 'เรียบร้อย' : 'ไม่พบหมวก' }}
              </span>
            </div>

            <div class="info-card neon-border-blue">
              <span class="label">ความแม่นยำใบหน้า</span>
              <span class="value text-blue">
                {{ faceConfidence }}%
              </span>
            </div>
          </div>

          <div class="log-box-terminal">
            <div class="log-title">SYSTEM LOG</div>
            <div class="log-entries">
              <p :class="lightingStatus === 'NORMAL' ? 'text-green' : 'text-danger'">
                > แสงสว่าง: {{ lightingStatus === 'NORMAL' ? 'เหมาะสม' : 'ต้องปรับปรุง' }}
              </p>
              <p :class="{ 'text-green': hatDetected }">> หมวก: {{ hatDetected ? 'ตรวจพบ' : 'ค้นหา...' }}</p>
              <p v-if="identified" class="text-green">> ยืนยันตัวตนสำเร็จ</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { identifyFace } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const videoElement = ref(null)
const overlayCanvas = ref(null)
const cameraActive = ref(false)
const scanning = ref(false)
const identified = ref(false)
const hatDetected = ref(false)
const allMatches = ref([])
const faceConfidence = ref(0)
const lightingStatus = ref('NORMAL')

let stream = null
let loopActive = false

const statusText = computed(() => {
  if (!cameraActive.value) return 'กรุณาเปิดกล้อง'
  if (identified.value) return 'ยืนยันตัวตนสำเร็จ'
  if (!hatDetected.value) return 'กรุณาสวมหมวก'
  if (faceConfidence.value === 0) return 'ไม่รู้จักใบหน้านี้'
  return 'กำลังตรวจสอบใบหน้าและหมวก...'
})

const statusClass = computed(() => identified.value ? 'success' : (scanning.value ? 'scanning' : 'ready'))

const startScanning = async () => {
  resetState()
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: { ideal: 1280 }, height: { ideal: 720 } } 
    })
    videoElement.value.srcObject = stream
    cameraActive.value = true
    loopActive = true
    
    videoElement.value.onloadedmetadata = () => {
      syncCanvasSize()
    }
    processLoop()
  } catch (err) { console.error("Camera Error:", err) }
}

const syncCanvasSize = () => {
  if (overlayCanvas.value && videoElement.value) {
    overlayCanvas.value.width = videoElement.value.videoWidth
    overlayCanvas.value.height = videoElement.value.videoHeight
  }
}

const stopScanning = () => {
  loopActive = false
  if (stream) stream.getTracks().forEach(t => t.stop())
  cameraActive.value = false
  if (overlayCanvas.value) {
    const ctx = overlayCanvas.value.getContext('2d')
    ctx.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height)
  }
}

const processLoop = async () => {
  if (!loopActive || identified.value) return
  await handleIdentify()
  setTimeout(processLoop, 150) 
}

const handleIdentify = async () => {
  if (scanning.value) return
  scanning.value = true
  const blob = await capture()
  
  if (blob) {
    try {
      const res = await identifyFace(blob)
      
      hatDetected.value = !!res.details?.hat_detected
      allMatches.value = res.all_matches || []
      lightingStatus.value = res.lighting_status || 'NORMAL'
      
      // ดึงคะแนนใบหน้ามาโชว์
      if (res.all_matches && res.all_matches.length > 0) {
        faceConfidence.value = Math.floor(res.all_matches[0].confidence)
      } else {
        faceConfidence.value = 0
      }
      
      if (res.details?.boxes) drawBoxes(res.details.boxes)

      if (res.identified) {
        identified.value = true
        setTimeout(() => { 
          authStore.login(res.user_id)
          router.push('/dashboard') 
        }, 1200)
      }
    } catch (e) {
      console.error(e)
    }
  }
  scanning.value = false
}

const drawBoxes = (boxes) => {
  if (!overlayCanvas.value) return
  const ctx = overlayCanvas.value.getContext('2d')
  ctx.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height)
  
  boxes.forEach(box => {
    const [x1, y1, x2, y2] = box.coords
    ctx.strokeStyle = box.is_hat ? '#00ff00' : '#00ccff'
    ctx.lineWidth = 5
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
    
    // วาดพื้นหลังให้ตัวอักษรอ่านง่าย
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'
    ctx.fillRect(x1, y1 - 30, ctx.measureText(box.label.toUpperCase()).width + 10, 30)
    
    ctx.fillStyle = ctx.strokeStyle
    ctx.font = 'bold 20px Arial'
    ctx.fillText(`${box.label.toUpperCase()}`, x1 + 5, y1 - 8)
  })
}

const capture = () => {
  if (!videoElement.value) return null
  const canvas = document.createElement('canvas')
  canvas.width = videoElement.value.videoWidth
  canvas.height = videoElement.value.videoHeight
  canvas.getContext('2d').drawImage(videoElement.value, 0, 0)
  return new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.8))
}

const resetState = () => {
  identified.value = false
  hatDetected.value = false
  faceConfidence.value = 0
  allMatches.value = []
  lightingStatus.value = 'NORMAL'
}

onUnmounted(stopScanning)
</script>

<style scoped>
.quick-login-page { min-height: 100vh; background: #0f172a; color: #f8fafc; padding: 20px; display: flex; align-items: center; }
.container { max-width: 1000px; margin: 0 auto; width: 100%; }
.header-section { text-align: center; margin-bottom: 20px; }
.header-section h1 { font-size: 1.8rem; color: #38bdf8; margin: 0; }
.main-layout { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; padding: 20px; }
.glass-morphism { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }
.video-container { background: #000; border-radius: 15px; position: relative; overflow: hidden; width: 100%; max-width: 540px; margin: 0 auto; aspect-ratio: 4/3; }
video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
.overlay-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; transform: scaleX(-1); z-index: 2; }
.env-alerts { position: absolute; top: 10px; right: 10px; display: flex; flex-direction: column; gap: 8px; z-index: 4; }
.alert-item { padding: 8px 12px; border-radius: 8px; font-weight: bold; font-size: 0.85rem; animation: pulse 1.5s infinite; }
.alert-item.warning { background: rgba(234, 179, 8, 0.9); color: #422006; }
.alert-item.danger { background: rgba(239, 68, 68, 0.9); color: white; }
.status-bar-overlay { position: absolute; bottom: 0; width: 100%; background: rgba(0,0,0,0.7); padding: 10px; text-align: center; font-size: 0.9rem; z-index: 3; }
.status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
.status-dot.ready { background: #94a3b8; }
.status-dot.scanning { background: #38bdf8; box-shadow: 0 0 10px #38bdf8; }
.status-dot.success { background: #22c55e; }
.side-panel { display: flex; flex-direction: column; gap: 15px; }
.btn-start { background: #38bdf8; color: #0f172a; border: none; padding: 15px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; }
.btn-stop { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; padding: 15px; border-radius: 10px; cursor: pointer; width: 100%; }
.info-card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; }
.label { font-size: 0.75rem; color: #94a3b8; display: block; }
.value { font-size: 1.5rem; font-weight: bold; }
.success-border { border-left: 4px solid #22c55e; }
.danger-border { border-left: 4px solid #ef4444; }
.text-green { color: #22c55e; }
.text-danger { color: #ef4444; }
.text-blue { color: #38bdf8; }
.log-box-terminal { background: #000; padding: 15px; border-radius: 10px; font-family: monospace; font-size: 0.8rem; flex-grow: 1; }
.log-title { color: #38bdf8; border-bottom: 1px solid #333; margin-bottom: 5px; }
@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
</style>