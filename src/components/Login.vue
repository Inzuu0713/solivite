<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const email = ref('')
const password = ref('')

const handleLogin = async () => {
  if (!email.value || !password.value) {
    alert('Please enter your credentials')
    return
  }

  try {
    const { data } = await api.post('/login', {
      email: email.value,
      password: password.value,
    })

    if (data.success) {
  localStorage.setItem('isLoggedIn', 'true')
  localStorage.setItem('user_fullname', data.name)
  localStorage.setItem('user_email', data.email)
  localStorage.setItem('user_id', data.user_id)
  router.push('/dashboard')
} else {
      alert(data.message)
    }
  } catch (error) {
    if (error.response?.status === 401) {
      alert('Invalid email or password.')
    } else {
      alert('Something went wrong. Please try again.')
    }
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="split-layout-container">
      
      <!-- Left Column: Brand Section -->
      <div class="brand-section">
        <div class="logo-container">
          <div class="logo-frame">
            <!-- Place your logo image here -->
            <span class="logo-placeholder">❤️</span>
          </div>
          <span class="logo-text">Solivite</span>
        </div>
        
        <h1 class="tagline">The Light That<br />Connects Hearts</h1>
        
        <div class="features-list">
          <div class="feature-item">
            <span class="feature-icon">📋</span> Plan Special Moments
          </div>
          <div class="feature-item">
            <span class="feature-icon">👥</span> Connect With Loved Ones
          </div>
          <div class="feature-item">
            <span class="feature-icon">🕒</span> Never Miss a Moment
          </div>
        </div>
      </div>

      <!-- Right Column: Form Section -->
      <div class="form-section">
        <div class="form-card">
          
          <div class="tabs-container">
            <div class="tabs-pill">
              <router-link to="/login" class="tab active">LOGIN</router-link>
              <router-link to="/signup" class="tab">SIGN UP</router-link>
            </div>
          </div>

          <form @submit.prevent="handleLogin" class="auth-form">
            <div class="input-group">
              <label>Email</label>
              <input v-model="email" type="email" placeholder="Enter your email" required />
            </div>

            <div class="input-group">
              <label>Password</label>
              <input
                v-model="password"
                type="password"
                placeholder="Enter your password"
                required
              />
            </div>

            <div class="form-options">
              <label class="remember-me">
                <input type="checkbox" /> Remember me
              </label>
              <a href="#" class="forgot-link">Forgot password?</a>
            </div>

            <button type="submit" class="submit-btn">Login &rarr;</button>
          </form>

        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Beautiful gradient from the second photo reference */
  background: linear-gradient(180deg, #4a7acb 0%, #9068be 30%, #e684ae 70%, #fbb096 100%);
  padding: 20px;
  font-family: 'Inter', sans-serif;
}

.split-layout-container {
  display: flex;
  width: 100%;
  max-width: 1000px;
  gap: 60px;
  align-items: center;
}

/* --- Brand Section (Left) --- */
.brand-section {
  flex: 1;
  color: white;
  display: flex;
  flex-direction: column;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.logo-frame {
  width: 60px;
  height: 60px;
  background: #ff758c;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(255, 117, 140, 0.4);
  overflow: hidden;
}

.logo-placeholder {
  font-size: 28px;
}

.logo-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-text {
  font-size: 36px;
  font-weight: 800;
  letter-spacing: 1px;
}

.tagline {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 50px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.feature-item {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 14px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 15px;
  font-weight: 500;
  font-size: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.feature-icon {
  font-size: 18px;
}

/* --- Form Section (Right) --- */
.form-section {
  flex: 1;
  display: flex;
  justify-content: center;
}

.form-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  width: 100%;
  max-width: 450px;
  border-radius: 24px;
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    10px 10px 30px rgba(0, 0, 0, 0.15),
    -10px -10px 30px rgba(255, 255, 255, 0.2);
  box-sizing: border-box;
}

.tabs-container {
  display: flex;
  justify-content: center;
  margin-bottom: 35px;
}

.tabs-pill {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 6px;
  width: 100%;
  box-shadow: 
    inset 4px 4px 8px rgba(0, 0, 0, 0.1),
    inset -4px -4px 8px rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tab {
  flex: 1;
  text-align: center;
  padding: 12px;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 700;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.tab.active {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  box-shadow: 
    4px 4px 10px rgba(0, 0, 0, 0.1),
    -4px -4px 10px rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.auth-form {
  text-align: left;
}

.input-group {
  margin-bottom: 22px;
}

.input-group label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.input-group input {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 14px;
  box-sizing: border-box;
  color: white;
  font-weight: 500;
  box-shadow: 
    inset 4px 4px 8px rgba(0, 0, 0, 0.1),
    inset -4px -4px 8px rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.input-group input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 
    inset 2px 2px 5px rgba(0, 0, 0, 0.05),
    inset -2px -2px 5px rgba(255, 255, 255, 0.2);
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-weight: normal;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-bottom: 30px;
  color: white;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.forgot-link {
  color: white;
  text-decoration: none;
  font-weight: 700;
}
.forgot-link:hover {
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  font-weight: 800;
  font-size: 15px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 
    6px 6px 15px rgba(0, 0, 0, 0.1),
    -6px -6px 15px rgba(255, 255, 255, 0.2);
}

.submit-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.submit-btn:active {
  transform: translateY(0);
  box-shadow: 
    inset 4px 4px 8px rgba(0, 0, 0, 0.1),
    inset -4px -4px 8px rgba(255, 255, 255, 0.2);
}

/* Responsive Design */
@media (max-width: 850px) {
  .split-layout-container {
    flex-direction: column;
    gap: 40px;
  }
  .brand-section {
    align-items: center;
    text-align: center;
  }
  .features-list {
    align-items: center;
  }
}
</style>
