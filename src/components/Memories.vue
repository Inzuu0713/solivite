<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const photos = ref([])
const showUploadModal = ref(false)
const newCaption = ref('')
const newCompanion = ref('')
const selectedFile = ref(null)
const previewUrl = ref(null)
const editingId = ref(null)

const fetchMemories = async () => {
  try {
    const { data } = await api.get('/memories')
    if (data.success) {
      photos.value = data.memories
    }
  } catch (err) {
    console.error("Failed to load memories", err)
  }
}

onMounted(() => {
  fetchMemories()
})

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (!file) return
  selectedFile.value = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const savePhoto = async () => {
  if (editingId.value) {
    // Edit existing
    try {
      await api.put(`/memories/${editingId.value}`, {
        caption: newCaption.value,
        companion: newCompanion.value
      })
      await fetchMemories()
      closeModal()
    } catch (err) {
      alert("Failed to update memory")
    }
  } else {
    // Create new
    if (!previewUrl.value) return
    try {
      await api.post('/memories', {
        url: previewUrl.value,
        caption: newCaption.value,
        companion: newCompanion.value,
        date: new Date().toLocaleDateString()
      })
      await fetchMemories()
      closeModal()
    } catch (err) {
      alert("Failed to save memory")
    }
  }
}

const deletePhoto = async (id) => {
  if (confirm("Are you sure you want to delete this memory?")) {
    try {
      await api.delete(`/memories/${id}`)
      await fetchMemories()
    } catch (err) {
      alert("Failed to delete memory")
    }
  }
}

const closeModal = () => {
  showUploadModal.value = false
  newCaption.value = ''
  newCompanion.value = ''
  selectedFile.value = null
  previewUrl.value = null
  editingId.value = null
}

const openEditModal = (photo) => {
  editingId.value = photo.id
  previewUrl.value = photo.url
  newCaption.value = photo.caption
  newCompanion.value = photo.companion
  showUploadModal.value = true
}
</script>

<template>
  <div class="memories-container">
    <header class="top-bar">
      <div class="welcome">
        <h1>Memories</h1>
        <p>A gallery of your favorite moments together.</p>
      </div>
      <button @click="showUploadModal = true" class="create-btn neumorphic-btn">
        📸 Upload Photo
      </button>
    </header>

    <div v-if="photos.length === 0" class="empty-state">
      <p>You haven't uploaded any photos yet!</p>
      <p>Click "Upload Photo" to start saving memories.</p>
    </div>

    <div v-else class="gallery-grid">
      <div v-for="photo in photos" :key="photo.id" class="photo-card neumorphic-panel">
        <div class="photo-wrapper">
          <img :src="photo.url" alt="Memory" class="memory-img" />
          <button class="action-btn edit-btn" @click="openEditModal(photo)">✏️</button>
          <button class="action-btn delete-btn" @click="deletePhoto(photo.id)">✖</button>
        </div>
        <div class="photo-info">
          <p class="caption">{{ photo.caption || 'Beautiful Moment' }}</p>
          <p class="companion" v-if="photo.companion"><span>👥 With:</span> {{ photo.companion }}</p>
          <span class="date">{{ photo.date }}</span>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content neumorphic-panel">
        <h3>{{ editingId ? 'Edit Memory' : 'Save a Memory' }}</h3>
        
        <div class="form-group" v-if="!editingId">
          <label>Select Photo</label>
          <input type="file" accept="image/*" @change="handleFileSelect" class="file-input neumorphic-input" />
        </div>
        
        <div v-if="previewUrl" class="preview-container">
          <img :src="previewUrl" alt="Preview" class="preview-img" />
        </div>

        <div class="form-group" v-if="previewUrl">
          <label>Caption</label>
          <input type="text" v-model="newCaption" placeholder="E.g., Cafe date!" class="neumorphic-input" />
        </div>

        <div class="form-group" v-if="previewUrl">
          <label>Who were you with?</label>
          <input type="text" v-model="newCompanion" placeholder="E.g., Bestie, Mark, etc." class="neumorphic-input" />
        </div>

        <div class="modal-actions">
          <button class="cancel-btn neumorphic-btn" @click="closeModal">Cancel</button>
          <button class="save-btn neumorphic-btn primary" @click="savePhoto" :disabled="!previewUrl">{{ editingId ? 'Save Changes' : 'Save Photo' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.memories-container {
  padding-bottom: 50px;
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
  color: #222;
  text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
}
.welcome p {
  color: #555;
  font-size: 16px;
  font-weight: 500;
}

.neumorphic-btn {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  color: #555;
  padding: 12px 24px;
  border-radius: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 
    6px 6px 12px rgba(0, 0, 0, 0.05),
    -6px -6px 12px rgba(255, 255, 255, 0.8);
}
.neumorphic-btn:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-2px);
  color: #333;
}
.neumorphic-btn.primary {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
  color: #d81b60;
  border: 1px solid white;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #555;
  font-size: 16px;
  font-style: italic;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  border: 1px dashed rgba(255, 255, 255, 0.8);
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 25px;
}
.photo-card {
  padding: 15px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 20px;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 
    10px 10px 20px rgba(0, 0, 0, 0.05),
    -10px -10px 20px rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
}
.photo-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: inset 4px 4px 8px rgba(0,0,0,0.1);
  background: rgba(255, 255, 255, 0.2);
}
.memory-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.memory-img:hover {
  transform: scale(1.05);
}
.action-btn {
  position: absolute;
  top: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}
.delete-btn {
  right: 10px;
  color: #ff4757;
}
.delete-btn:hover {
  background: #ff4757;
  color: white;
}
.edit-btn {
  right: 48px;
  color: #4facfe;
  font-size: 14px;
}
.edit-btn:hover {
  background: #4facfe;
  color: white;
}
.photo-info {
  margin-top: 15px;
  padding: 0 5px;
}
.caption {
  font-weight: 800;
  color: #333;
  margin: 0 0 5px 0;
  font-size: 15px;
}
.companion {
  font-size: 13px;
  color: #555;
  margin: 0 0 8px 0;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.4);
  padding: 4px 8px;
  border-radius: 8px;
  display: inline-block;
}
.companion span {
  font-weight: 700;
  color: #ff758c;
}
.date {
  font-size: 12px;
  color: #777;
  font-weight: 600;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(255, 255, 255, 0.2);
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
.neumorphic-input {
  background: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #333 !important;
  padding: 14px;
  border-radius: 12px;
  width: 100%;
  outline: none;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  font-weight: 600;
  box-sizing: border-box;
}
.neumorphic-input:focus {
  border-color: rgba(0, 0, 0, 0.3);
  background: white !important;
}
.file-input {
  padding: 10px;
}
.preview-container {
  margin-bottom: 18px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: inset 2px 2px 5px rgba(0,0,0,0.1);
  border: 1px solid rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.3);
}
.preview-img {
  width: 100%;
  height: 200px;
  object-fit: contain;
  display: block;
}
.modal-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}
.cancel-btn, .save-btn {
  flex: 1;
  text-align: center;
}
.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
