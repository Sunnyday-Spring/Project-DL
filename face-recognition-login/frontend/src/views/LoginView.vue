<template>
  <div class="auth-page light-theme">
    <div class="auth-card">
      <div class="icon-container">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shield-icon">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <path d="m9 12 2 2 4-4"></path>
        </svg>
      </div>
      
      <h1 class="title">เข้าสู่ระบบ</h1>
      <p class="subtitle">ยืนยันตัวตน 2 ขั้นตอน (2FA)</p>

      <form @submit.prevent="proceedToScanner" class="form-container">
        <div class="input-group">
          <label>อีเมล <span class="required">*</span></label>
          <input type="email" v-model="form.email" required placeholder="your@email.com" />
        </div>
        <div class="input-group">
          <label>รหัสผ่าน <span class="required">*</span></label>
          <input type="password" v-model="form.password" required />
        </div>

        <button type="submit" class="submit-btn">ถัดไป: สแกนใบหน้าและหมวก ⚡</button>
      </form>
      
      <div class="footer-link">
        ยังไม่มีบัญชี? <router-link to="/register" class="link">ลงทะเบียน</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
// 🔴 เปลี่ยนตัวแปรมารับค่า email แทน studentId
const form = ref({ email: '', password: '' })

const proceedToScanner = () => {
  // ของจริงอาจจะมีการเช็ค รหัสผ่านกับ Backend ก่อนหน้านี้
  // ถ้าผ่านแล้ว ค่อยเปลี่ยนหน้าไปให้เปิดกล้องสแกนใบหน้าและหมวก
  router.push('/quick-login')
}
</script>

<style scoped>
.light-theme { background-color: #f8faff; color: #333; }
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; font-family: 'Kanit', sans-serif; padding: 20px; }
.auth-card { background: white; padding: 40px 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); width: 100%; max-width: 400px; text-align: center; }
.icon-container { width: 60px; height: 60px; background-color: #9333ea; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; color: white; }
.title { font-size: 1.8rem; color: #1e293b; margin: 0 0 5px; font-weight: 600; }
.subtitle { color: #64748b; margin-bottom: 30px; font-size: 0.95rem; }
.form-container { text-align: left; }
.input-group { margin-bottom: 20px; }
.input-group label { display: block; margin-bottom: 8px; font-size: 0.9rem; color: #334155; font-weight: 500; }
.required { color: #9333ea; }
.input-group input { width: 100%; padding: 12px 15px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; transition: 0.2s; box-sizing: border-box; }
.input-group input:focus { border-color: #9333ea; }
.submit-btn { width: 100%; background-color: #9333ea; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; margin-top: 10px; transition: background-color 0.2s; }
.submit-btn:hover { background-color: #7e22ce; }
.footer-link { margin-top: 25px; font-size: 0.9rem; color: #475569; }
.link { color: #9333ea; text-decoration: none; font-weight: 500; }
.link:hover { text-decoration: underline; }
</style>