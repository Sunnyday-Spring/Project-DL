<template>
  <div class="auth-page dark-theme">
    <div class="auth-card glass-morphism neon-border-blue">
      <div class="icon-container neon-bg-blue">
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
          <input type="email" v-model="form.email" required placeholder="your@email.com" class="dark-input" />
        </div>
        <div class="input-group">
          <label>รหัสผ่าน <span class="required">*</span></label>
          <input type="password" v-model="form.password" required class="dark-input" />
        </div>

        <button type="submit" class="submit-btn neon-btn">ถัดไป: สแกนใบหน้าและหมวก ⚡</button>
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
const form = ref({ email: '', password: '' })

const proceedToScanner = () => {
  router.push('/quick-login')
}
</script>

<style scoped>
/* --- Dark Theme & Colors (Reference from QuickLoginView) --- */
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
  padding: 20px; 
}

/* Glassmorphism Effect */
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
  max-width: 400px; 
  text-align: center; 
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

.form-container { 
  text-align: left; 
}

.input-group { 
  margin-bottom: 20px; 
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
  transition: 0.2s; 
  box-sizing: border-box; 
}

.dark-input:focus { 
  border-color: #38bdf8; 
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); 
}

/* Neon Button Style */
.submit-btn { 
  width: 100%; 
  border: none; 
  padding: 14px; 
  border-radius: 8px; 
  font-size: 1rem; 
  font-weight: bold; 
  cursor: pointer; 
  margin-top: 10px; 
  transition: 0.3s; 
}

.neon-btn { 
  background-color: #38bdf8; 
  color: #0f172a; 
  box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3); 
}

.neon-btn:hover { 
  background-color: #7dd3fc; 
  transform: translateY(-2px); 
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

.link:hover { 
  text-decoration: underline; 
}
</style>