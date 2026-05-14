<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  activities: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['respond-invite', 'cancel-moment', 'edit-moment', 'reply-moment'])

const today = new Date()
const currentMonth = ref(today.getMonth())
const currentYear = ref(today.getFullYear())

const selectedEvent = ref(null)

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
})

const firstDayOfMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 1).getDay()
})

const calendarDays = computed(() => {
  const days = []
  for (let i = 0; i < firstDayOfMonth.value; i++) {
    days.push(null)
  }
  for (let i = 1; i <= daysInMonth.value; i++) {
    const d = new Date(currentYear.value, currentMonth.value, i)
    // format YYYY-MM-DD
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    
    // Find events for this day
    const dayEvents = props.activities.filter(a => a.date === dateStr)
    days.push({
      date: i,
      dateStr,
      events: dayEvents
    })
  }
  return days
})

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const getStatusColor = (status) => {
  if (status === 'Accepted') return '#4ade80'
  if (status === 'Declined') return '#f87171'
  return '#fcd34d'
}

const getGoogleMapsLink = (location) => {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(location)}`;
}

const getGoogleCalendarLink = (evt) => {
  const title = encodeURIComponent(`Date with ${evt.role === 'receiver' ? evt.sender_name : evt.target}`);
  const location = encodeURIComponent(evt.location || '');
  
  if (!evt.date || !evt.time) return '#';
  
  const dateStr = evt.date.replace(/-/g, '');
  const timeStr = evt.time.replace(':', '') + '00';
  
  const hour = parseInt(evt.time.split(':')[0]);
  const endHour = String((hour + 2) % 24).padStart(2, '0');
  const endTimeStr = endHour + evt.time.split(':')[1] + '00';
  
  const dates = `${dateStr}T${timeStr}/${dateStr}T${endTimeStr}`;
  
  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dates}&location=${location}`;
}

const selectEvent = (evt) => {
  selectedEvent.value = evt
}

const closeEventModal = () => {
  selectedEvent.value = null
}

const handleAction = (action) => {
  if (action === 'accept' || action === 'decline') {
    emit('respond-invite', selectedEvent.value.id, action)
  } else if (action === 'cancel') {
    emit('cancel-moment', selectedEvent.value.id)
  } else if (action === 'edit') {
    emit('edit-moment', selectedEvent.value)
  } else if (action === 'reply') {
    emit('reply-moment', selectedEvent.value)
  }
  closeEventModal()
}
</script>

<template>
  <div class="calendar-container neumorphic-card">
    <div class="calendar-header">
      <button class="neumorphic-btn-icon" @click="prevMonth">◀</button>
      <h2>{{ monthNames[currentMonth] }} {{ currentYear }}</h2>
      <button class="neumorphic-btn-icon" @click="nextMonth">▶</button>
    </div>

    <div class="calendar-grid">
      <div class="day-name">Sun</div>
      <div class="day-name">Mon</div>
      <div class="day-name">Tue</div>
      <div class="day-name">Wed</div>
      <div class="day-name">Thu</div>
      <div class="day-name">Fri</div>
      <div class="day-name">Sat</div>

      <div v-for="(day, index) in calendarDays" :key="index" class="day-cell" :class="{ 'empty': !day }">
        <span v-if="day" class="date-num">{{ day.date }}</span>
        <div class="events-list" v-if="day && day.events.length">
          <div 
            v-for="evt in day.events" 
            :key="evt.id" 
            class="event-badge"
            :style="{ backgroundColor: getStatusColor(evt.invitation_status) }"
            @click.stop="selectEvent(evt)"
          >
            {{ evt.time }} {{ evt.role === 'receiver' ? evt.sender_name : evt.target }}
          </div>
        </div>
      </div>
    </div>

    <!-- Event Details Modal -->
    <div v-if="selectedEvent" class="event-modal-overlay" @click.self="closeEventModal">
      <div class="event-modal neumorphic-card">
        <h3>{{ selectedEvent.role === 'receiver' ? 'Invitation from ' + selectedEvent.sender_name : 'Date with ' + selectedEvent.target }}</h3>
        <p><strong>Date:</strong> {{ selectedEvent.date }}</p>
        <p><strong>Time:</strong> {{ selectedEvent.time }}</p>
        <p v-if="selectedEvent.location">
          <strong>Location:</strong> 
          <a :href="getGoogleMapsLink(selectedEvent.location)" target="_blank" class="location-link">📍 {{ selectedEvent.location }}</a>
        </p>
        <p v-if="selectedEvent.message" class="message-text">
          <strong>Message:</strong> <i>"{{ selectedEvent.message }}"</i>
        </p>
        <p><strong>Status:</strong> <span :style="{ color: getStatusColor(selectedEvent.invitation_status) }">{{ selectedEvent.invitation_status || 'Pending' }}</span></p>
        
        <div class="modal-actions">
          <template v-if="selectedEvent.role === 'receiver' && selectedEvent.invitation_status === 'Pending'">
            <button class="accept-btn neumorphic-btn" @click="handleAction('accept')">Accept</button>
            <button class="decline-btn neumorphic-btn" @click="handleAction('decline')">Decline</button>
          </template>
          <template v-else-if="selectedEvent.role !== 'receiver' && (selectedEvent.invitation_status === 'Pending' || !selectedEvent.invitation_status)">
             <button class="edit-btn neumorphic-btn" @click="handleAction('edit')">Edit</button>
             <button class="cancel-btn neumorphic-btn" @click="handleAction('cancel')">Cancel</button>
          </template>
          <template v-else-if="selectedEvent.role !== 'receiver' && selectedEvent.invitation_status === 'Declined'">
             <button class="reply-btn neumorphic-btn" @click="handleAction('reply')">💬 Reply</button>
             <button class="cancel-btn neumorphic-btn" @click="handleAction('cancel')">🗑️ Remove</button>
          </template>
          <a v-if="selectedEvent.invitation_status === 'Accepted' || !selectedEvent.invitation_status" :href="getGoogleCalendarLink(selectedEvent)" target="_blank" class="calendar-btn neumorphic-btn">📅 Add to Calendar</a>
          <button class="close-btn neumorphic-btn" @click="closeEventModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-container {
  margin-top: 20px;
  padding: 20px;
  color: #333;
}
.neumorphic-card {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  color: #333;
}
.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.calendar-header h2 {
  font-size: 20px;
  font-weight: 800;
  margin: 0;
  color: #333;
}
.neumorphic-btn-icon {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  color: #555;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.05), -2px -2px 5px rgba(255,255,255,0.6);
}
.neumorphic-btn-icon:hover {
  background: rgba(255, 255, 255, 0.8);
}
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}
.day-name {
  text-align: center;
  font-weight: bold;
  font-size: 12px;
  color: #555;
  padding-bottom: 10px;
}
.day-cell {
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  min-height: 80px;
  padding: 8px;
  position: relative;
  display: flex;
  flex-direction: column;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
.day-cell.empty {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
}
.date-num {
  font-size: 12px;
  font-weight: bold;
  color: #444;
  margin-bottom: 4px;
}
.events-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
  max-height: 50px;
}
.event-badge {
  font-size: 10px;
  color: #000;
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 600;
  transition: transform 0.1s;
}
.event-badge:hover {
  transform: scale(1.05);
}

.event-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.event-modal {
  width: 320px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}
.event-modal h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}
.event-modal p {
  margin: 0;
  font-size: 14px;
  color: #555;
}
.message-text {
  background: rgba(0, 0, 0, 0.03);
  padding: 8px 10px;
  border-radius: 8px;
  border-left: 3px solid #0284c7;
}
.location-link {
  color: #0284c7;
  text-decoration: none;
  font-weight: bold;
  background: rgba(2, 132, 199, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
  transition: 0.2s;
}
.location-link:hover {
  background: rgba(2, 132, 199, 0.2);
}
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}
.neumorphic-btn {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  color: #555;
  padding: 8px 16px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: bold;
  flex: 1;
  text-align: center;
  transition: 0.2s;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
.neumorphic-btn:hover {
  background: rgba(255, 255, 255, 0.8);
  color: #333;
}
.accept-btn {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.5);
}
.calendar-btn {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.5);
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}
.edit-btn {
  background: rgba(56, 189, 248, 0.2);
  color: #0284c7;
  border-color: rgba(56, 189, 248, 0.5);
}
.reply-btn {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
  border-color: rgba(139, 92, 246, 0.5);
}
.decline-btn, .cancel-btn {
  background: rgba(248, 113, 113, 0.2);
  color: #ef4444;
  border-color: rgba(248, 113, 113, 0.5);
}
</style>
