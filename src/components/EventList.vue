<script setup>
defineProps({
  activities: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['cancel-moment', 'edit-moment', 'reply-moment'])

const getStatusClass = (status) => {
  if (status === 'Accepted') return 'accepted'
  if (status === 'Declined') return 'declined'
  return 'pulsing'
}

const getGoogleMapsLink = (location) => {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(location)}`;
}

const getGoogleCalendarLink = (act) => {
  const title = encodeURIComponent(`Moment with ${act.role === 'receiver' ? act.sender_name : act.target}`);
  const location = encodeURIComponent(act.location || '');
  
  if (!act.date || !act.time) return '#';
  
  const dateStr = act.date.replace(/-/g, '');
  const timeStr = act.time.replace(':', '') + '00';
  
  const hour = parseInt(act.time.split(':')[0]);
  const endHour = String((hour + 2) % 24).padStart(2, '0');
  const endTimeStr = endHour + act.time.split(':')[1] + '00';
  
  const dates = `${dateStr}T${timeStr}/${dateStr}T${endTimeStr}`;
  
  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dates}&location=${location}`;
}
</script>

<template>
  <section class="recent-section">
    <h2>Scheduled Moments</h2>
    <div class="activity-feed">
      <div v-if="activities.length === 0" class="empty-state">No upcoming moments.</div>
      <div v-for="act in activities" :key="act.id" class="activity-row neumorphic-card">
        <div :class="['status-dot', getStatusClass(act.invitation_status)]"></div>
        <div class="activity-info">
          <strong>{{ act.role === 'receiver' ? act.sender_name : act.target }}</strong>
          <span v-if="act.role === 'receiver'" class="receiver-tag"> invited you</span>
          <a v-if="act.location" :href="getGoogleMapsLink(act.location)" target="_blank" class="location-link">
            📍 {{ act.location }}
          </a>
          <span class="details-text">{{ act.date }} at {{ act.time }}</span>
          <p v-if="act.message" class="message-text">"{{ act.message }}"</p>
        </div>
        <span :class="['status-badge', getStatusClass(act.invitation_status)]">
          {{ act.invitation_status || 'Pending' }}
        </span>
        <div class="action-buttons" v-if="
            (act.invitation_status === 'Pending' || !act.invitation_status) &&
            act.role !== 'receiver'
          ">
          <a :href="getGoogleCalendarLink(act)" target="_blank" class="calendar-action-btn neumorphic-btn-sm" title="Add to Google Calendar">
            📅
          </a>
          <button
            class="edit-action-btn neumorphic-btn-sm"
            @click="emit('edit-moment', act)"
          >
            Edit
          </button>
          <button
            class="cancel-action-btn neumorphic-btn-sm"
            @click="emit('cancel-moment', act.id)"
          >
            Cancel
          </button>
        </div>
        <div class="action-buttons" v-else-if="act.invitation_status === 'Accepted'">
          <a :href="getGoogleCalendarLink(act)" target="_blank" class="calendar-action-btn neumorphic-btn-sm" title="Add to Google Calendar">
            📅 Add to Calendar
          </a>
        </div>
        <div class="action-buttons" v-else-if="act.invitation_status === 'Declined'">
          <button
            class="reply-action-btn neumorphic-btn-sm"
            @click="emit('reply-moment', act)"
          >
            💬 Reply
          </button>
          <button
            class="cancel-action-btn neumorphic-btn-sm"
            @click="emit('cancel-moment', act.id)"
          >
            🗑️ Remove
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.recent-section {
  margin-top: 20px;
}
.recent-section h2 {
  font-size: 20px;
  margin-bottom: 20px;
  font-weight: 800;
  color: #333;
}
.activity-feed {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.activity-row {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px 24px;
}
.neumorphic-card {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 20px;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 
    10px 10px 20px rgba(0, 0, 0, 0.05),
    -10px -10px 20px rgba(255, 255, 255, 0.6);
}
.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.pulsing {
  background: #f59e0b;
  box-shadow: 0 0 10px #fcd34d;
  animation: pulse 2s infinite;
}
.status-dot.accepted {
  background: #10b981;
  box-shadow: 0 0 10px #4ade80;
}
.status-dot.declined {
  background: #ef4444;
  box-shadow: 0 0 10px #f87171;
  opacity: 0.8;
}
.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 800;
  margin-left: auto;
  white-space: nowrap;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.status-badge.accepted {
  background: rgba(16, 185, 129, 0.15);
  color: #047857;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.status-badge.declined {
  background: rgba(239, 68, 68, 0.15);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
.status-badge.pulsing {
  background: rgba(245, 158, 11, 0.15);
  color: #b45309;
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.activity-info {
  flex: 1;
}
.activity-info strong {
  font-size: 16px;
  color: #222;
  font-weight: 800;
}
.receiver-tag {
  font-size: 11px;
  color: #047857;
  font-weight: bold;
  margin-left: 6px;
  background: rgba(16, 185, 129, 0.15);
  padding: 2px 6px;
  border-radius: 6px;
}
.location-link {
  color: #0284c7;
  font-size: 14px;
  font-weight: bold;
  text-decoration: none;
  margin-left: 8px;
  background: rgba(2, 132, 199, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
  transition: 0.2s;
}
.location-link:hover {
  background: rgba(2, 132, 199, 0.2);
}
.details-text {
  display: block;
  font-size: 13px;
  color: #777;
  margin-top: 4px;
  font-weight: 600;
}
.message-text {
  margin-top: 6px;
  font-size: 13px;
  font-style: italic;
  color: #555;
  background: rgba(0, 0, 0, 0.03);
  padding: 6px 10px;
  border-radius: 8px;
  border-left: 2px solid #0284c7;
}
.action-buttons {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.neumorphic-btn-sm {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  padding: 6px 14px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.2s;
  box-shadow: 
    4px 4px 8px rgba(0, 0, 0, 0.05),
    -4px -4px 8px rgba(255, 255, 255, 0.8);
}
.neumorphic-btn-sm:hover {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 
    inset 2px 2px 5px rgba(0, 0, 0, 0.05),
    inset -2px -2px 5px rgba(255, 255, 255, 0.8);
}
.cancel-action-btn {
  color: #ef4444;
}
.edit-action-btn {
  color: #0284c7;
}
.reply-action-btn {
  color: #8b5cf6;
}
.calendar-action-btn {
  color: #10b981;
  text-decoration: none;
  display: flex;
  align-items: center;
}
.empty-state {
  opacity: 0.8;
  text-align: center;
  padding: 40px;
  font-style: italic;
  color: #555;
  font-weight: 600;
}
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.5; }
  100% { transform: scale(1); opacity: 1; }
}
@media (max-width: 768px) {
  .activity-row {
    flex-wrap: wrap;
    padding: 14px 16px;
    gap: 10px;
  }
  .activity-info {
    flex: 1;
    min-width: 0;
  }
  .status-badge {
    margin-left: 0;
  }
  .action-buttons {
    width: 100%;
    flex-wrap: wrap;
  }
  .neumorphic-btn-sm {
    flex: 1;
    text-align: center;
    justify-content: center;
  }
  .calendar-action-btn {
    flex: 1;
    justify-content: center;
    text-align: center;
  }
}
</style>
