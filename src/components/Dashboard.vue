<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

const showModal = ref(false)
const showSettings = ref(false)
const currentTab = ref('dashboard')
const currentStep = ref(1)
const userName = ref('User')
const userEmail = ref('')

const activities = ref([])
const invitations = ref([])

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

const newMoment = ref({ invitee: '', location: '', date: '', time: '', email: '', message: '' })

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

const getStatusClass = (status) => {
  if (status === 'Accepted') return 'accepted'
  if (status === 'Declined') return 'declined'
  return 'pulsing'
}

const submitMoment = async () => {
  try {
    const { data } = await api.post('/moments', {
      title: `Date at ${newMoment.value.location}`,
      target: newMoment.value.invitee,
      location: newMoment.value.location,
      date: newMoment.value.date,
      time: newMoment.value.time,
    })

    if (data.success) {
      if (newMoment.value.email) {
        await api.post('/invite', {
          receiver_email: newMoment.value.email,
          message: newMoment.value.message,
          schedule_date: newMoment.value.date,
          schedule_time: newMoment.value.time,
          relationship_type: newMoment.value.invitee,
        })
      }
      await fetchMoments()
      closeModal()
    }
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
  newMoment.value = { invitee: '', location: '', date: '', time: '', email: '', message: '' }
}

const handleInvite = async (id, status) => {
  try {
    await api.post('/invitations/respond', {
      invitation_id: id,
      action: status === 'accepted' ? 'Accepted' : 'Declined',
    })
    await fetchInvitations()
    await fetchMoments()
    if (status === 'accepted') alert('Invite Accepted!')
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
</script>

<template>
  <div class="page-container">
    <div class="glass-container dashboard-frame">
      <aside class="sidebar">
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
            :class="['nav-item', { active: currentTab === 'invitations' }]"
            @click="currentTab = 'invitations'"
          >
            <span>💌</span> Invitations
            <span v-if="invitations.length > 0" class="badge">{{ invitations.length }}</span>
          </div>

          <div class="nav-item settings-toggle" @click="showSettings = !showSettings">
            <div class="nav-content"><span>⚙️</span> Settings</div>
            <span class="chevron">{{ showSettings ? '▲' : '▼' }}</span>
          </div>

          <div v-if="showSettings" class="settings-dropdown">
            <button class="sub-item logout-action" @click="handleLogout">
              <span>➡️</span> Log Out
            </button>
          </div>
        </nav>

        <div class="user-card">
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
            <button @click="showModal = true" class="create-btn">+ New Moment</button>
          </header>

          <section class="recent-section">
            <h2>Scheduled Moments</h2>
            <div class="activity-feed">
              <div v-if="activities.length === 0" class="empty-state">No upcoming moments.</div>
              <div v-for="act in activities" :key="act.id" class="activity-row">
                <div :class="['status-dot', getStatusClass(act.invitation_status)]"></div>
                <div class="activity-info">
                  <strong>{{ act.role === 'receiver' ? act.sender_name : act.target }}</strong>
                  <span v-if="act.role === 'receiver'" class="receiver-tag"> invited you</span>
                  <span v-if="act.location"> — {{ act.location }}</span>
                  <span class="details-text">{{ act.date }} at {{ act.time }}</span>
                </div>
                <span :class="['status-badge', getStatusClass(act.invitation_status)]">
                  {{ act.invitation_status || 'Pending' }}
                </span>
                <button
                  v-if="
                    (act.invitation_status === 'Pending' || !act.invitation_status) &&
                    act.role !== 'receiver'
                  "
                  class="cancel-action-btn"
                  @click="cancelMoment(act.id)"
                >
                  Cancel
                </button>
              </div>
            </div>
          </section>
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
              <div v-for="invite in invitations" :key="invite.id" class="invite-card">
                <div class="invite-details">
                  <span class="invite-from"
                    >Invitation from <strong>{{ invite.sender_name }}</strong></span
                  >
                  <p class="invite-meta">
                    📅 {{ invite.schedule_date }} | ⏰ {{ invite.schedule_time }}
                  </p>
                  <p v-if="invite.message" class="invite-msg">"{{ invite.message }}"</p>
                </div>
                <div class="invite-actions">
                  <button class="accept-btn" @click="handleInvite(invite.id, 'accepted')">
                    Accept
                  </button>
                  <button class="decline-btn" @click="handleInvite(invite.id, 'declined')">
                    Decline
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <h3>{{ currentStep === 1 ? 'Schedule a Moment' : 'Finalize Invitation' }}</h3>
          <div v-if="currentStep === 1">
            <div class="form-group">
              <label>Who are you Inviting?</label>
              <select v-model="newMoment.invitee" class="dark-select">
                <option value="Partner">Partner</option>
                <option value="Best Friend">Best Friend</option>
                <option value="Crush">Crush</option>
                <option value="Family">Family</option>
                <option value="Wife">Wife</option>
              </select>
            </div>
            <div class="form-group">
              <label>Location</label>
              <input
                type="text"
                v-model="newMoment.location"
                placeholder="Where to?"
                class="dark-input"
              />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Date</label><input type="date" v-model="newMoment.date" />
              </div>
              <div class="form-group">
                <label>Time</label><input type="time" v-model="newMoment.time" />
              </div>
            </div>
            <div class="modal-actions">
              <button class="cancel-btn" @click="closeModal">Cancel</button>
              <button class="confirm-btn" @click="nextStep">Next</button>
            </div>
          </div>
          <div v-if="currentStep === 2">
            <div class="form-group">
              <label>Email</label><input type="email" v-model="newMoment.email" />
            </div>
            <div class="form-group">
              <label>Message (optional)</label>
              <textarea v-model="newMoment.message" rows="3"></textarea>
            </div>
            <div class="modal-actions">
              <button class="cancel-btn" @click="currentStep = 1">Back</button>
              <button class="confirm-btn" @click="submitMoment">Send Invitation</button>
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Inter', sans-serif;
}
.dashboard-frame {
  display: flex;
  width: 100%;
  max-width: 1100px;
  height: 85vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 30px;
  overflow: hidden;
}
.sidebar {
  width: 250px;
  background: rgba(0, 0, 0, 0.2);
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
}
.logo-heart {
  width: 35px;
  height: 35px;
  background: #ff758c;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-links {
  flex: 1;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  border-radius: 12px;
  color: white;
  opacity: 0.6;
  cursor: pointer;
  transition: 0.3s;
  margin-bottom: 8px;
  position: relative;
}
.nav-item.active {
  background: white;
  color: #6366f1;
  opacity: 1;
  font-weight: bold;
}
.settings-toggle {
  display: flex;
  justify-content: space-between;
}
.settings-dropdown {
  background: rgba(0, 0, 0, 0.2);
  margin: -5px 10px 10px 10px;
  border-radius: 0 0 12px 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-top: none;
}
.logout-action {
  width: 100%;
  padding: 12px 15px;
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
}
.logout-action:hover {
  background: rgba(255, 50, 50, 0.1);
  color: #ff758c;
}
.badge {
  position: absolute;
  right: 15px;
  background: #ff758c;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
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
  margin-bottom: 40px;
}
.create-btn {
  background: white;
  color: #6366f1;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: bold;
  cursor: pointer;
}
.activity-row {
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 12px;
  padding: 15px 20px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  gap: 15px;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.pulsing {
  background: #ff758c;
  box-shadow: 0 0 10px #ff758c;
  animation: pulse 2s infinite;
}
.status-dot.accepted {
  background: #4ade80;
  box-shadow: 0 0 10px #4ade80;
  animation: none;
}
.status-dot.declined {
  background: #ff758c;
  box-shadow: none;
  animation: none;
  opacity: 0.5;
}
.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: bold;
  margin-left: auto;
  white-space: nowrap;
}
.status-badge.accepted {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}
.status-badge.declined {
  background: rgba(255, 117, 140, 0.2);
  color: #ff758c;
}
.status-badge.pulsing {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
}
.activity-info {
  flex: 1;
}
.receiver-tag {
  font-size: 11px;
  color: #4ade80;
  font-weight: normal;
  margin-left: 4px;
}
.details-text {
  display: block;
  font-size: 12px;
  opacity: 0.5;
}
.dark-select {
  background-color: rgba(255, 255, 255, 0.05) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
  border-radius: 10px;
  width: 100%;
  outline: none;
}
.dark-select option {
  background-color: #1a1a2e;
  color: white;
}
.dark-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
  border-radius: 10px;
  color: white;
  width: 100%;
  outline: none;
}
.dark-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}
.cancel-action-btn {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffbaba;
  padding: 5px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 11px;
  flex-shrink: 0;
}
.invite-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.invite-msg {
  font-style: italic;
  font-size: 13px;
  background: rgba(0, 0, 0, 0.2);
  padding: 10px;
  border-radius: 10px;
  margin-top: 10px;
}
.invite-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.accept-btn {
  background: #4ade80;
  color: #064e3b;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
}
.decline-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #ffbaba;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
}
.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  width: 400px;
  background: #1a1a2e;
  padding: 30px;
  border-radius: 24px;
}
.modal-content h3 {
  color: white;
  font-size: 20px;
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.form-group label {
  color: white;
  font-weight: bold;
}
.form-group input,
.form-group select,
textarea {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
  border-radius: 10px;
  color: white;
  outline: none;
}
.form-row {
  display: flex;
  gap: 10px;
}
.form-row .form-group {
  flex: 1;
}
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
.confirm-btn {
  flex: 1;
  background: #ff758c;
  border: none;
  padding: 12px;
  border-radius: 10px;
  color: white;
  font-weight: bold;
  cursor: pointer;
}
.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  padding: 12px;
  border-radius: 10px;
  color: white;
  cursor: pointer;
}
.user-card {
  margin-top: auto;
  display: flex;
  gap: 12px;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.avatar-ring {
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}
.empty-state {
  opacity: 0.5;
  text-align: center;
  padding: 40px;
}
@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  70% {
    transform: scale(1.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}
</style>
