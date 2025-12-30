<script setup lang="ts">
const { notifications, remove } = useNotify()

const getTypeStyles = (type: string) => {
  switch (type) {
    case 'success': return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
    case 'error': return 'border-red-500/30 bg-red-500/10 text-red-400'
    case 'warning': return 'border-amber-500/30 bg-amber-500/10 text-amber-400'
    case 'info': return 'border-blue-500/30 bg-blue-500/10 text-blue-400'
    default: return 'border-white/10 bg-white/5 text-white'
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'success': return '✅'
    case 'error': return '❌'
    case 'warning': return '⚠️'
    case 'info': return 'ℹ️'
    default: return '🔔'
  }
}
</script>

<template>
  <div class="fixed top-24 right-6 z-[100] space-y-4 pointer-events-none max-w-sm w-full">
    <TransitionGroup 
      name="notification"
      enter-active-class="transform transition duration-500 ease-out"
      enter-from-class="translate-x-full opacity-0"
      enter-to-class="translate-x-0 opacity-100"
      leave-active-class="transform transition duration-300 ease-in"
      leave-from-class="translate-x-0 opacity-100"
      leave-to-class="translate-x-full opacity-0"
    >
      <div 
        v-for="note in notifications.filter(n => !n.isModal)" 
        :key="note.id"
        class="pointer-events-auto glass-panel p-4 flex items-center justify-between gap-4 border"
        :class="getTypeStyles(note.type)"
      >
        <div class="flex items-center gap-3">
          <span class="text-xl">{{ getTypeIcon(note.type) }}</span>
          <p class="text-[11px] font-black uppercase tracking-widest">{{ note.message }}</p>
        </div>
        <button @click="remove(note.id)" class="text-slate-500 hover:text-white transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </TransitionGroup>

    <!-- Modal Style Notifications -->
    <TransitionGroup
      name="modal"
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div 
        v-for="note in notifications.filter(n => n.isModal)" 
        :key="note.id"
        class="fixed inset-0 z-[110] flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-sm pointer-events-auto"
      >
        <div class="glass-panel p-10 max-w-lg w-full text-center space-y-8 border" :class="getTypeStyles(note.type)">
           <div class="w-20 h-20 mx-auto rounded-3xl flex items-center justify-center text-4xl shadow-2xl" :class="getTypeStyles(note.type)">
             {{ getTypeIcon(note.type) }}
           </div>
           <div class="space-y-2">
             <h3 class="text-2xl font-black text-white font-heading uppercase">{{ note.type }}</h3>
             <p class="text-slate-400 font-medium">{{ note.message }}</p>
           </div>
           <div class="flex flex-col gap-3">
             <NuxtLink 
               v-if="note.actionLabel && note.actionRoute"
               :to="note.actionRoute"
               @click="remove(note.id)"
               class="w-full py-4 rounded-2xl bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] text-white font-black text-xs uppercase tracking-[0.2em] transition-all text-center flex items-center justify-center gap-2"
             >
               {{ note.actionLabel }}
               <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
             </NuxtLink>
             
             <button 
               @click="remove(note.id)"
               class="w-full py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-black text-xs uppercase tracking-[0.2em] transition-all"
             >
               {{ (note.actionLabel && note.actionRoute) ? 'Mungkin Nanti' : 'Tutup' }}
             </button>
           </div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.notification-move {
  transition: all 0.5s ease;
}
</style>
