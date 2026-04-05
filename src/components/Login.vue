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
    <div class="glass-container">
      <div class="brand-section">
        <div class="logo-container">
          <div class="logo-box">❤️</div>
          <span class="logo-text">Solivite</span>
        </div>
        <h1 class="tagline">The Light That<br />Connects Hearts</h1>
        <div class="features-list">
          <div class="feature-item"><span>📋</span> Plan Special Moments</div>
          <div class="feature-item"><span>👥</span> Connect With Loved Ones</div>
          <div class="feature-item"><span>🕒</span> Never Miss a Moment</div>
        </div>
      </div>

      <div class="form-section">
        <div class="form-card">
          <div class="tabs">
            <router-link to="/login" class="tab" active-class="active">LOGIN</router-link>
            <router-link to="/signup" class="tab" active-class="active">SIGN UP</router-link>
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
              <label class="remember-me"><input type="checkbox" /> Remember me</label>
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
  background: linear-gradient(135deg, #6366f1 0%, #d946ef 100%);
  padding: 20px;
}

.glass-container {
  display: flex;
  width: 100%;
  max-width: 900px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.brand-section {
  flex: 1;
  padding: 60px;
  color: white;
  display: flex;
  flex-direction: column;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
}

.logo-box {
  width: 45px;
  height: 45px;
  background: #ff758c;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 28px;
  font-weight: 800;
}

.tagline {
  font-size: 20px;
  margin-bottom: 45px;
  opacity: 0.9;
}

.feature-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 12px 20px;
  border-radius: 14px;
  margin-bottom: 12px;
  display: flex;
  gap: 12px;
}

.form-section {
  flex: 1.1;
  padding: 20px;
  display: flex;
}

.form-card {
  background: white;
  width: 100%;
  border-radius: 20px;
  padding: 40px;
  box-sizing: border-box;
}

.tabs {
  display: flex;
  background: #f3f4f6;
  border-radius: 12px;
  padding: 6px;
  margin-bottom: 30px;
}

.tab {
  flex: 1;
  padding: 12px;
  text-decoration: none;
  text-align: center;
  border-radius: 10px;
  font-weight: 700;
  color: #9ca3af;
  transition: 0.3s;
}

.tab.active {
  background: white;
  color: #6366f1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.auth-form {
  text-align: left;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #555;
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-bottom: 25px;
  color: #666;
}

.forgot-link {
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
}

.submit-btn {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}
</style>
