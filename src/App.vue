<script setup>
/**
 * Solivite Main Shell
 * This file stays simple so that the Router can
 * swap between the Login Layout and the Full Dashboard.
 */
</script>

<template>
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style>
/* 1. Global Reset: This fixes the "narrow strip" issue by 
      ensuring the app fills the entire browser window. */
body,
html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #6366f1; /* Fallback color */
  overflow-x: hidden;
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* 2. Transition Animations: Smoothes the switch 
      between Login and Dashboard. */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 3. Global Scrollbar Styling (Optional) */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}
</style>
