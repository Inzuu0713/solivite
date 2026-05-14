<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import EventList from './EventList.vue'
import Calendar from './Calendar.vue'
import Memories from './Memories.vue'

const router = useRouter()

const showModal = ref(false)
const showSettings = ref(false)
const currentTab = ref('dashboard')
const currentStep = ref(1)
const userName = ref('User')
const userEmail = ref('')

const activities = ref([])
const invitations = ref([])

const themes = [
  {
    id: 'blue-pink',
    name: 'Blue to Pink',
    value: 'linear-gradient(135deg, #8ec5fc 0%, #e0c3fc 100%)',
  },
  {
    id: 'violet-orange',
    name: 'Violet to Orange',
    value: 'linear-gradient(135deg, #b088f9 0%, #ffc0a1 100%)',
  },
  { id: 'sky', name: 'Sky Color', value: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)' },
  { id: 'ocean', name: 'Ocean Color', value: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  {
    id: 'mountains',
    name: 'Sunset Mountains',
    value:
      'url("https://images.unsplash.com/photo-1542224566-6e85f2e6772f?q=80&w=2000&auto=format&fit=crop")',
  },
  {
    id: 'golden-sky',
    name: 'Golden Sky',
    value:
      'url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2000&auto=format&fit=crop")',
  },
  {
    id: 'purple-twilight',
    name: 'Purple Twilight',
    value:
      'url("https://images.unsplash.com/photo-1502481851512-e9e2529bfbf9?q=80&w=2000&auto=format&fit=crop")',
  },
  {
    id: 'ocean-breeze',
    name: 'Ocean Breeze',
    value:
      'url("https://images.unsplash.com/photo-1505118380757-91f5f5632de0?q=80&w=2000&auto=format&fit=crop")',
  },
  {
    id: 'sunset-glow',
    name: 'Warm Sunset',
    value:
      'url("https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?q=80&w=2000&auto=format&fit=crop")',
  },
  {
    id: 'going-night',
    name: 'Going Night',
    value:
      'url("https://images.unsplash.com/photo-1472552944129-b035e9ea3744?q=80&w=2000&auto=format&fit=crop")',
  },
  {
    id: 'starry-sky',
    name: 'Starry Sky',
    value:
      'url("https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=2000&auto=format&fit=crop")',
  },
]
const currentTheme = ref(localStorage.getItem('app_theme') || themes[0].value)

const setTheme = (themeVal) => {
  currentTheme.value = themeVal
  localStorage.setItem('app_theme', themeVal)
}

onMounted(async () => {
  const savedName = localStorage.getItem('user_fullname')
  const savedEmail = localStorage.getItem('user_email')
  if (savedName) userName.value = savedName
  if (savedEmail) userEmail.value = savedEmail

  await fetchMoments()
  await fetchInvitations()
})

const fetchMoments = async () => {
  try {
    const { data } = await api.get('/moments')
    if (data.success) activities.value = data.moments
  } catch (err) {
    console.error('Failed to fetch moments', err)
  }
}

const fetchInvitations = async () => {
  if (!userEmail.value) return
  try {
    const { data } = await api.get(`/invitations/${userEmail.value}`)
    if (data.success) invitations.value = data.invitations
  } catch (err) {
    console.error('Failed to fetch invitations', err)
  }
}

const newMoment = ref({
  id: null,
  invitee: '',
  location: '',
  date: '',
  time: '',
  email: '',
  message: '',
})

const nextStep = () => {
  if (
    !newMoment.value.invitee ||
    !newMoment.value.location ||
    !newMoment.value.date ||
    !newMoment.value.time
  ) {
    alert('Please fill in all details!')
    return
  }
  currentStep.value = 2
}

const submitMoment = async () => {
  try {
    const isEditing = !!newMoment.value.id
    const payload = {
      title: `Date at ${newMoment.value.location}`,
      target: newMoment.value.invitee,
      location: newMoment.value.location,
      date: newMoment.value.date,
      time: newMoment.value.time,
    }

    if (isEditing) {
      await api.put(`/moments/${newMoment.value.id}`, payload)
    } else {
      const { data } = await api.post('/moments', payload)
      if (data.success && newMoment.value.email) {
        await api.post('/invite', {
          receiver_email: newMoment.value.email,
          message: newMoment.value.message,
          location: newMoment.value.location,
          schedule_date: newMoment.value.date,
          schedule_time: newMoment.value.time,
          relationship_type: newMoment.value.invitee,
        })
      }
    }

    await fetchMoments()
    closeModal()
  } catch (err) {
    if (err.response?.status === 401) {
      alert('Session expired. Please log in again.')
      router.push('/login')
    } else {
      alert('Failed to save moment. Please try again.')
      console.error(err)
    }
  }
}

const closeModal = () => {
  showModal.value = false
  currentStep.value = 1
  newMoment.value = {
    id: null,
    invitee: '',
    location: '',
    date: '',
    time: '',
    email: '',
    message: '',
  }
}

const openEditModal = (moment) => {
  newMoment.value = {
    id: moment.id,
    invitee: moment.target,
    location: moment.location,
    date: moment.date,
    time: moment.time,
    email: '',
    message: '',
  }
  showModal.value = true
}

const handleInvite = async (id, status) => {
  try {
    const actionStr = status === 'accepted' || status === 'accept' ? 'Accepted' : 'Declined'
    await api.post('/invitations/respond', {
      invitation_id: id,
      action: actionStr,
    })
    await fetchInvitations()
    await fetchMoments()
    if (actionStr === 'Accepted') alert('Invite Accepted!')
  } catch (err) {
    console.error('Failed to respond to invite', err)
  }
}

const cancelMoment = async (id) => {
  if (confirm('Cancel this moment?')) {
    try {
      await api.delete(`/moments/${id}`)
      await fetchMoments()
    } catch (err) {
      console.error('Failed to cancel moment', err)
    }
  }
}

const handleLogout = async () => {
  try {
    await api.post('/logout')
  } catch (err) {
    console.log('Session already cleared or backend unreachable')
  }
  localStorage.clear()
  userName.value = 'User'
  activities.value = []
  invitations.value = []
  router.push('/login')
}

const buildCalendarUrl = (invite) => {
  try {
    const [year, month, day] = invite.schedule_date.split('-')
    const [hour, minute] = invite.schedule_time.split(':')
    const pad = (n) => String(n).padStart(2, '0')
    const start = `${year}${month}${day}T${pad(hour)}${pad(minute)}00`
    // Default 2-hour event
    let endHour = parseInt(hour, 10) + 2
    let endDay = day
    let endMonth = month
    let endYear = year
    if (endHour >= 24) { endHour -= 24; endDay = pad(parseInt(day, 10) + 1) }
    const end = `${endYear}${endMonth}${pad(endDay)}T${pad(endHour)}${pad(minute)}00`
    const title = encodeURIComponent(`Solivite Date with ${invite.sender_name}`)
    const details = encodeURIComponent(`Solivite invitation from ${invite.sender_name}`)
    const location = encodeURIComponent(invite.location || '')
    return `https://www.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${start}/${end}&details=${details}&location=${location}`
  } catch {
    return 'https://calendar.google.com'
  }
}
</script>

<template>
  <div class="page-container" :style="{ background: currentTheme }">
    <div class="glass-container dashboard-frame">
      <aside class="sidebar neumorphic-panel">
        <div class="brand">
          <div class="logo-heart">❤</div>
          <span class="logo-text">Solivite</span>
        </div>

        <nav class="nav-links">
          <div
            :class="['nav-item', { active: currentTab === 'dashboard' }]"
            @click="currentTab = 'dashboard'"
          >
            <span>🏠</span> Dashboard
          </div>
          <div
            :class="['nav-item', { active: currentTab === 'calendar' }]"
            @click="currentTab = 'calendar'"
          >
            <span>📅</span> Calendar
          </div>
          <div
            :class="['nav-item', { active: currentTab === 'invitations' }]"
            @click="currentTab = 'invitations'"
          >
            <span>💌</span> Invitations
            <span v-if="invitations.length > 0" class="badge">{{ invitations.length }}</span>
          </div>
          <div
            :class="['nav-item', { active: currentTab === 'memories' }]"
            @click="currentTab = 'memories'"
          >
            <span>📸</span> Memories
          </div>

          <div class="nav-item settings-toggle" @click="showSettings = !showSettings">
            <div class="nav-content"><span>⚙️</span> Settings</div>
            <span class="chevron">{{ showSettings ? '▲' : '▼' }}</span>
          </div>

          <div v-if="showSettings" class="settings-dropdown neumorphic-panel-inset">
            <div class="theme-selector">
              <label>Theme</label>
              <div class="theme-options">
                <div
                  v-for="t in themes"
                  :key="t.id"
                  class="theme-dot"
                  :style="{ background: t.value }"
                  :class="{ active: currentTheme === t.value }"
                  @click="setTheme(t.value)"
                  :title="t.name"
                ></div>
              </div>
            </div>
            <button class="sub-item logout-action" @click="handleLogout">
              <span>➡️</span> Log Out
            </button>
          </div>
        </nav>

        <div class="user-card neumorphic-panel">
          <div class="avatar-ring">👤</div>
          <div class="user-meta">
            <strong>{{ userName }}</strong>
          </div>
        </div>
      </aside>

      <main class="dashboard-body">
        <div v-if="currentTab === 'dashboard'">
          <header class="top-bar">
            <div class="welcome">
              <h1>Hello, {{ userName }}!</h1>
              <p>You have {{ activities.length }} moments scheduled.</p>
            </div>
            <button @click="showModal = true" class="create-btn neumorphic-btn">
              + New Moment
            </button>
          </header>

          <EventList
            :activities="activities"
            @cancel-moment="cancelMoment"
            @edit-moment="openEditModal"
          />
        </div>

        <div v-if="currentTab === 'calendar'">
          <header class="top-bar">
            <div class="welcome">
              <h1>Calendar</h1>
              <p>View all your scheduled and pending moments.</p>
            </div>
            <button @click="showModal = true" class="create-btn neumorphic-btn">
              + New Moment
            </button>
          </header>

          <Calendar
            :activities="activities"
            @respond-invite="handleInvite"
            @cancel-moment="cancelMoment"
            @edit-moment="openEditModal"
          />
        </div>

        <div v-if="currentTab === 'invitations'">
          <header class="top-bar">
            <div class="welcome">
              <h1>Invitations</h1>
              <p>Incoming date requests.</p>
            </div>
          </header>

          <section class="recent-section">
            <div class="activity-feed">
              <div v-if="invitations.length === 0" class="empty-state">No new invitations.</div>
              <div
                v-for="invite in invitations"
                :key="invite.id"
                class="invite-card neumorphic-panel"
              >
                <div class="invite-details">
                  <span class="invite-from">
                    Invitation from <strong>{{ invite.sender_name }}</strong>
                  </span>
                  <p class="invite-meta">
                    📅 {{ invite.schedule_date }} &nbsp;|&nbsp; ⏰ {{ invite.schedule_time }}
                  </p>
                  <p v-if="invite.location" class="invite-meta invite-location">
                    📍 {{ invite.location }}
                    &nbsp;
                    <a
                      :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(invite.location)}`"
                      target="_blank"
                      class="maps-link"
                    >🗺️ View on Google Maps</a>
                  </p>
                  <p v-if="invite.message" class="invite-msg">"{{ invite.message }}"</p>
                  <a
                    v-if="invite.schedule_date && invite.schedule_time"
                    :href="buildCalendarUrl(invite)"
                    target="_blank"
                    class="gcal-btn"
                  >📆 Add to Google Calendar</a>
                </div>
                <div class="invite-actions">
                  <button
                    class="accept-btn neumorphic-btn"
                    @click="handleInvite(invite.id, 'accepted')"
                  >
                    Accept
                  </button>
                  <button
                    class="decline-btn neumorphic-btn"
                    @click="handleInvite(invite.id, 'declined')"
                  >
                    Decline
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>

        <div v-if="currentTab === 'memories'">
          <Memories />
        </div>
      </main>

      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content neumorphic-panel">
          <h3>{{ currentStep === 1 ? 'Schedule a Moment' : 'Finalize Invitation' }}</h3>
          <div v-if="currentStep === 1">
            <div class="form-group">
              <label>Who are you Inviting?</label>
              <select v-model="newMoment.invitee" class="neumorphic-input">
                <option value="Partner">Partner</option>
                <option value="Spouse">Spouse</option>
                <option value="BF/GF">BF/GF</option>
                <option value="Best Friend">Best Friend</option>
                <option value="Crush">Crush</option>
                <option value="Family">Family</option>
                <option value="Friend">Friend</option>
                <option value="Casual Friend">Casual Friend</option>
                <option value="Ex">Ex</option>
                <option value="Prefer Not to say">Prefer Not to say</option>
                <option value="Cousin">Cousin</option>
              </select>
            </div>
            <div class="form-group">
              <label>Location</label>
              <input
                type="text"
                v-model="newMoment.location"
                placeholder="Where to?"
                class="neumorphic-input"
              />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Date</label>
                <input type="date" v-model="newMoment.date" class="neumorphic-input" />
              </div>
              <div class="form-group">
                <label>Time</label>
                <input type="time" v-model="newMoment.time" class="neumorphic-input" />
              </div>
            </div>
            <div class="modal-actions">
              <button class="cancel-btn neumorphic-btn" @click="closeModal">Cancel</button>
              <button class="confirm-btn neumorphic-btn primary" @click="nextStep">Next</button>
            </div>
          </div>
          <div v-if="currentStep === 2">
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="newMoment.email" class="neumorphic-input" />
            </div>
            <div class="form-group">
              <label>Message (optional)</label>
              <textarea v-model="newMoment.message" rows="3" class="neumorphic-input"></textarea>
            </div>
            <div class="modal-actions">
              <button class="cancel-btn neumorphic-btn" @click="currentStep = 1">Back</button>
              <button class="confirm-btn neumorphic-btn primary" @click="submitMoment">
                Send Invitation
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  font-family: 'Inter', sans-serif;
  transition: background 0.5s ease;
  background-size: cover !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
}

.dashboard-frame {
  display: flex;
  width: 100%;
  max-width: 1200px;
  height: 85vh;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 30px;
  overflow: hidden;
  box-shadow:
    10px 10px 30px rgba(0, 0, 0, 0.2),
    -10px -10px 30px rgba(255, 255, 255, 0.1);
}

.sidebar {
  width: 260px;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  padding: 40px 20px;
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 50px;
  color: white;
  padding-left: 10px;
}
.logo-heart {
  width: 35px;
  height: 35px;
  background: #ff758c;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 2px 2px 8px rgba(255, 117, 140, 0.5);
}
.logo-text {
  font-size: 22px;
  font-weight: bold;
  letter-spacing: 1px;
}

.nav-links {
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 14px 18px;
  border-radius: 16px;
  color: white;
  opacity: 0.7;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 10px;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  opacity: 1;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  opacity: 1;
  font-weight: bold;
  box-shadow:
    inset 2px 2px 5px rgba(255, 255, 255, 0.1),
    inset -2px -2px 5px rgba(0, 0, 0, 0.1);
}

.badge {
  position: absolute;
  right: 15px;
  background: #ff758c;
  color: white;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: bold;
  box-shadow: 0 0 10px rgba(255, 117, 140, 0.5);
}

.settings-toggle {
  display: flex;
  justify-content: space-between;
}

.settings-dropdown {
  margin: 5px 10px 15px 10px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.theme-selector label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
  display: block;
  font-weight: bold;
}
.theme-options {
  display: flex;
  gap: 10px;
}
.theme-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: transform 0.2s;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
}
.theme-dot:hover {
  transform: scale(1.1);
}
.theme-dot.active {
  border-color: white;
  transform: scale(1.1);
}

.logout-action {
  width: 100%;
  padding: 10px;
  background: none;
  border: none;
  color: #ffbaba;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s;
  text-align: left;
  border-radius: 8px;
}
.logout-action:hover {
  background: rgba(255, 50, 50, 0.15);
  color: #ff758c;
}

.user-card {
  margin-top: auto;
  display: flex;
  gap: 15px;
  align-items: center;
  padding: 15px;
}
.avatar-ring {
  width: 45px;
  height: 45px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  font-size: 20px;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
}

.dashboard-body {
  flex: 1;
  padding: 50px;
  overflow-y: auto;
  color: white;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}
.welcome h1 {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 5px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}
.welcome p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

/* Neumorphic Utilities */
.neumorphic-panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow:
    4px 4px 10px rgba(0, 0, 0, 0.1),
    -4px -4px 10px rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

.neumorphic-panel-inset {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  box-shadow:
    inset 4px 4px 8px rgba(0, 0, 0, 0.2),
    inset -4px -4px 8px rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.neumorphic-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 12px 24px;
  border-radius: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow:
    4px 4px 10px rgba(0, 0, 0, 0.1),
    -4px -4px 10px rgba(255, 255, 255, 0.1);
}
.neumorphic-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}
.neumorphic-btn:active {
  box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.1);
  transform: translateY(0);
}
.neumorphic-btn.primary {
  background: #ff758c;
  color: white;
  border: none;
  box-shadow: 4px 4px 10px rgba(255, 117, 140, 0.3);
}

.neumorphic-input {
  background: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #333 !important;
  padding: 14px;
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box;
  outline: none;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  font-weight: 600;
}
.neumorphic-input:focus {
  border-color: rgba(0, 0, 0, 0.3);
  background: white !important;
}
.neumorphic-input::placeholder {
  color: #888;
}
.neumorphic-input option {
  background-color: white;
  color: #333;
}

/* Modals */
.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  width: 420px;
  padding: 35px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  color: #333;
}
.modal-content h3 {
  font-size: 24px;
  margin-bottom: 25px;
  font-weight: 800;
  color: #333;
  text-align: center;
}
.form-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-group label {
  font-weight: 700;
  font-size: 14px;
  color: #555;
}
.form-row {
  display: flex;
  gap: 15px;
}
.form-row .form-group {
  flex: 1;
}
.modal-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}
.cancel-btn,
.confirm-btn {
  flex: 1;
}

.modal-actions .cancel-btn {
  background: #e53e3e;
  color: white;
  border: none;
}
.modal-actions .cancel-btn:hover {
  background: #c53030;
}

/* Invitations */
.invite-card {
  padding: 25px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.invite-details {
  flex: 1;
}
.invite-from {
  font-size: 18px;
}
.invite-meta {
  color: rgba(255, 255, 255, 0.7);
  margin-top: 5px;
  font-size: 14px;
}
.invite-msg {
  font-style: italic;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.2);
  padding: 12px;
  border-radius: 10px;
  margin-top: 15px;
  border-left: 3px solid #ff758c;
}
.invite-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-left: 20px;
}
.accept-btn {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.5);
}
.decline-btn {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.5);
}
.empty-state {
  opacity: 0.6;
  text-align: center;
  padding: 40px;
  font-style: italic;
}

.invite-location {
  font-size: 14px;
  margin-top: 6px;
  color: rgba(255,255,255,0.85);
}

.maps-link {
  color: #ffd700;
  font-weight: bold;
  text-decoration: none;
  margin-left: 6px;
  font-size: 13px;
  transition: color 0.2s;
}
.maps-link:hover {
  color: #fff;
  text-decoration: underline;
}

.gcal-btn {
  display: inline-block;
  margin-top: 12px;
  background: linear-gradient(135deg, #4285f4, #34a853);
  color: white;
  padding: 9px 18px;
  border-radius: 10px;
  text-decoration: none;
  font-size: 13px;
  font-weight: bold;
  letter-spacing: 0.3px;
  box-shadow: 0 3px 10px rgba(66,133,244,0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}
.gcal-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66,133,244,0.5);
}
</style>
