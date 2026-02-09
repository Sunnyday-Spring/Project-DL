<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="logo">Face Recognition</router-link>
        
        <div class="nav-links">
          <template v-if="authStore && !authStore.isAuthenticated">
            <router-link to="/">หน้าแรก</router-link>
            <router-link to="/quick-login" class="quick-link">⚡ Quick Login</router-link>
            <router-link to="/register">ลงทะเบียน</router-link>
            <router-link to="/login">เข้าสู่ระบบ</router-link>
          </template>
          
          <template v-else-if="authStore">
            <router-link to="/dashboard">Dashboard</router-link>
            <button @click="handleLogout" class="logout-btn">ออกจากระบบ</button>
          </template>
        </div>
      </div>
    </nav>

    <main>
      <RouterView />
    </main>

    <footer class="footer">
      <p>Face Recognition Login System - Demo Version</p>
    </footer>
  </div>
</template>

<script setup>
import { useRouter, RouterView } from 'vue-router'
// เปลี่ยนจาก '@/stores/auth' เป็น '../stores/auth.js' เพื่อความชัวร์
import { useAuthStore } from './stores/auth.js' 

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  if (confirm('ออกจากระบบ?')) {
    authStore.logout()
    router.push('/')
  }
}
</script>

<style>
/* คงส่วน CSS เดิมของคุณไว้ */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

.navbar {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.3rem;
  font-weight: 700;
  text-decoration: none;
  color: #2196F3;
}

.nav-links {
  display: flex;
  gap: 15px;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: #666;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 15px;
}

.nav-links a:hover {
  background: #f5f5f5;
}

.nav-links a.router-link-active {
  color: #2196F3;
  font-weight: 600;
}

.quick-link {
  background: #e3f2fd;
  color: #2196F3 !important;
  font-weight: 600;
}

.logout-btn {
  background: #ff5252;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.footer {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  color: #666;
  font-size: 14px;
}
</style>