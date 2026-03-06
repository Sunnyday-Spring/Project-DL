<template>
  <div class="f1-store-page">
    <header class="store-header">
      <div class="logo-area">
        <h1>🏎️ F1 <span class="text-neon">EXCLUSIVE SHOP</span></h1>
        <p class="user-badge" v-if="authStore.user">👤 ผู้ใช้งาน: {{ authStore.user }}</p>
      </div>
      <button @click="logout" class="btn-logout">ออกจากระบบ</button>
    </header>

    <div class="store-container">
      <aside class="sidebar">
        <h3>เลือกทีม (TEAMS)</h3>
        <ul class="team-list">
          <li 
            v-for="team in teams" 
            :key="team"
            @click="selectedTeam = team"
            :class="{ active: selectedTeam === team }"
          >
            {{ team }}
          </li>
        </ul>
      </aside>

      <main class="product-gallery">
        <div class="filter-header">
          <div class="type-filters">
            <button 
              v-for="type in productTypes" 
              :key="type.value"
              @click="selectedType = type.value"
              :class="{ active: selectedType === type.value }"
              class="type-btn"
            >
              {{ type.label }}
            </button>
          </div>
        </div>

        <div class="gallery-header">
          <h2>สินค้าหมวด: <span class="text-neon">{{ selectedTeam }}</span> 
            <small v-if="selectedType !== 'All'" class="type-tag">/ {{ selectedType }}</small>
          </h2>
        </div>

        <div class="product-grid">
          <div 
            v-for="product in filteredProducts" 
            :key="product.id" 
            class="product-card"
          >
            <div class="product-image" :class="getTeamColor(product.team)">
              <span class="emoji">{{ product.icon }}</span>
            </div>
            
            <div class="product-info">
              <span class="team-tag">{{ product.team }}</span>
              <h3 class="product-name">{{ product.name }}</h3>
              <div class="price-row">
                <span class="price">฿{{ product.price.toLocaleString() }}</span>
                <button class="btn-buy">🛒 ซื้อเลย</button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="filteredProducts.length === 0" class="empty-state">
          <p>🏁 ยังไม่มีสินค้าในหมวดหมู่นี้</p>
          <button @click="resetFilters" class="btn-reset">ล้างการค้นหา</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// หมวดหมู่ทีม
const teams = ['ทั้งหมด (All Teams)', 'Red Bull Racing', 'Scuderia Ferrari', 'Mercedes-AMG', 'McLaren']
const selectedTeam = ref('ทั้งหมด (All Teams)')

// หมวดหมู่ประเภทสินค้า (เพิ่มใหม่)
const productTypes = [
  { label: 'ทั้งหมด', value: 'All' },
  { label: 'เสื้อ (Shirt)', value: 'Shirt' },
  { label: 'หมวก (Hat)', value: 'Hat' },
  { label: 'แจ็คเก็ต (Jacket)', value: 'Jacket' },
  { label: 'อื่นๆ', value: 'Bag' }
]
const selectedType = ref('All')

// ข้อมูลสินค้า
const products = ref([
  { id: 1, name: 'Red Bull Racing 2024 Team Polo', team: 'Red Bull Racing', price: 2500, type: 'Shirt', icon: '👕' },
  { id: 2, name: 'Max Verstappen Flat Cap', team: 'Red Bull Racing', price: 1200, type: 'Hat', icon: '🧢' },
  { id: 3, name: 'Ferrari SF-24 Team T-Shirt', team: 'Scuderia Ferrari', price: 2300, type: 'Shirt', icon: '👕' },
  { id: 4, name: 'Charles Leclerc Monza Cap', team: 'Scuderia Ferrari', price: 1500, type: 'Hat', icon: '🧢' },
  { id: 5, name: 'Ferrari Race Jacket', team: 'Scuderia Ferrari', price: 4500, type: 'Jacket', icon: '🧥' },
  { id: 6, name: 'Mercedes Lewis Hamilton Hoodie', team: 'Mercedes-AMG', price: 3500, type: 'Jacket', icon: '🧥' },
  { id: 7, name: 'Mercedes Team Beanie', team: 'Mercedes-AMG', price: 900, type: 'Hat', icon: '🧢' },
  { id: 8, name: 'McLaren Lando Norris T-Shirt', team: 'McLaren', price: 2100, type: 'Shirt', icon: '👕' },
  { id: 9, name: 'McLaren Papaya Backpack', team: 'McLaren', price: 1800, type: 'Bag', icon: '🎒' },
])

// ฟิลเตอร์สินค้าตามทีม และ ประเภท (ปรับปรุงใหม่)
const filteredProducts = computed(() => {
  return products.value.filter(product => {
    const matchTeam = selectedTeam.value === 'ทั้งหมด (All Teams)' || product.team === selectedTeam.value
    const matchType = selectedType.value === 'All' || product.type === selectedType.value
    return matchTeam && matchType
  })
})

const getTeamColor = (team) => {
  switch(team) {
    case 'Red Bull Racing': return 'bg-redbull'
    case 'Scuderia Ferrari': return 'bg-ferrari'
    case 'Mercedes-AMG': return 'bg-mercedes'
    case 'McLaren': return 'bg-mclaren'
    default: return 'bg-default'
  }
}

const resetFilters = () => {
  selectedTeam.value = 'ทั้งหมด (All Teams)'
  selectedType.value = 'All'
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* CSS เดิมของคุณคงไว้ และเพิ่มส่วนข้างล่างนี้ */

.filter-header {
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 12px;
}

.type-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.type-btn {
  background: #1e293b;
  color: #cbd5e1;
  border: 1px solid #334155;
  padding: 8px 20px;
  border-radius: 25px;
  cursor: pointer;
  transition: 0.2s;
  font-weight: 500;
}

.type-btn:hover {
  border-color: #38bdf8;
}

.type-btn.active {
  background: #38bdf8;
  color: #0f172a;
  border-color: #38bdf8;
  font-weight: bold;
}

.type-tag {
  font-size: 1rem;
  color: #94a3b8;
  font-weight: normal;
}

.btn-reset {
  margin-top: 15px;
  background: #334155;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

/* คง CSS ส่วนอื่นๆ ที่คุณมีอยู่แล้ว */
.f1-store-page { min-height: 100vh; background-color: #0f172a; color: #f8fafc; font-family: 'Kanit', sans-serif; }
.store-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 40px; background-color: #1e293b; border-bottom: 2px solid #38bdf8; }
.store-header h1 { margin: 0; font-size: 1.8rem; font-style: italic; font-weight: 800; }
.text-neon { color: #38bdf8; text-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
.user-badge { margin: 5px 0 0 0; color: #94a3b8; font-size: 0.9rem; }
.btn-logout { background-color: transparent; color: #ef4444; border: 1px solid #ef4444; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.2s; }
.btn-logout:hover { background-color: rgba(239, 68, 68, 0.1); }
.store-container { display: flex; max-width: 1400px; margin: 0 auto; padding: 30px 20px; gap: 30px; }
.sidebar { width: 250px; flex-shrink: 0; background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 12px; height: fit-content; }
.sidebar h3 { color: #94a3b8; font-size: 1rem; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-top: 0; }
.team-list { list-style: none; padding: 0; margin: 0; }
.team-list li { padding: 12px 15px; margin-bottom: 8px; border-radius: 8px; cursor: pointer; transition: 0.2s; color: #cbd5e1; font-weight: 500; }
.team-list li:hover { background: rgba(255, 255, 255, 0.1); }
.team-list li.active { background: #38bdf8; color: #0f172a; font-weight: bold; }
.product-gallery { flex-grow: 1; }
.gallery-header h2 { margin-top: 0; margin-bottom: 25px; border-left: 4px solid #38bdf8; padding-left: 15px; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; }
.product-card { background: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; transition: transform 0.2s, box-shadow 0.2s; }
.product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3); }
.product-image { height: 200px; display: flex; align-items: center; justify-content: center; }
.emoji { font-size: 5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3)); }
.bg-redbull { background: linear-gradient(135deg, #0600ef, #000000); }
.bg-ferrari { background: linear-gradient(135deg, #dc0000, #5c0000); }
.bg-mercedes { background: linear-gradient(135deg, #00a19c, #000000); }
.bg-mclaren { background: linear-gradient(135deg, #ff8000, #000000); }
.bg-default { background: linear-gradient(135deg, #475569, #1e293b); }
.product-info { padding: 20px; }
.team-tag { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
.product-name { font-size: 1.1rem; margin: 10px 0; color: #f8fafc; line-height: 1.4; height: 48px; overflow: hidden; }
.price-row { display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid #334155; }
.price { font-size: 1.3rem; font-weight: bold; color: #38bdf8; }
.btn-buy { background: #22c55e; color: white; border: none; padding: 8px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-buy:hover { background: #16a34a; }
.empty-state { text-align: center; padding: 50px; color: #64748b; font-size: 1.2rem; background: #1e293b; border-radius: 12px; }
</style>