<script setup lang="ts">
const { user, isAuthenticated, isAdmin, logout } = useAuth()
const route = useRoute()

const isPageActive = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const theme = ref('dark')

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  if (typeof window !== 'undefined') {
    document.documentElement.setAttribute('data-theme', theme.value)
    localStorage.setItem('sahih-theme', theme.value)
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    const savedTheme = localStorage.getItem('sahih-theme') || 'dark'
    theme.value = savedTheme
    document.documentElement.setAttribute('data-theme', theme.value)
  }
})
</script>

<template>
  <nav class="border-b border-theme transition-colors bg-slate-900/10 backdrop-blur-2xl sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-4 group cursor-pointer transition-all hover:scale-105 active:scale-95">
        <div class="relative">
          <img src="/logo.png" alt="SahihAksara" class="w-12 h-12 rounded-xl border border-white/10 shadow-2xl group-hover:rotate-6 transition-all duration-500 bg-white" />
          <div class="absolute inset-0 bg-purple-500/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </div>
        <span class="text-2xl font-black tracking-tight transition-colors font-heading">Sahih<span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-fuchsia-400">Aksara</span></span>
      </NuxtLink>

      <!-- Nav Links -->
      <div class="hidden md:flex gap-8 text-[11px] font-black text-content-muted uppercase tracking-[0.2em] px-8">
        <NuxtLink to="/" class="hover:text-white transition-all relative group py-2" :class="{ 'text-white': isPageActive('/') }">
          Beranda
          <span class="absolute bottom-0 left-0 h-0.5 bg-purple-500 rounded-full transition-all" :class="isPageActive('/') ? 'w-full' : 'w-0 group-hover:w-full'"></span>
        </NuxtLink>
        <NuxtLink to="/pricing" class="hover:text-white transition-all relative group py-2" :class="{ 'text-white': isPageActive('/pricing') }">
          Pricing
          <span class="absolute bottom-0 left-0 h-0.5 bg-purple-500 rounded-full transition-all" :class="isPageActive('/pricing') ? 'w-full' : 'w-0 group-hover:w-full'"></span>
        </NuxtLink>
        <NuxtLink to="/cara-kerja" class="hover:text-white transition-all relative group py-2" :class="{ 'text-white': isPageActive('/cara-kerja') }">
          Cara Kerja
          <span class="absolute bottom-0 left-0 h-0.5 bg-purple-500 rounded-full transition-all" :class="isPageActive('/cara-kerja') ? 'w-full' : 'w-0 group-hover:w-full'"></span>
        </NuxtLink>
        <NuxtLink to="/kebijakan-privasi" class="hover:text-white transition-all relative group py-2" :class="{ 'text-white': isPageActive('/kebijakan-privasi') }">
          Privasi
          <span class="absolute bottom-0 left-0 h-0.5 bg-purple-500 rounded-full transition-all" :class="isPageActive('/kebijakan-privasi') ? 'w-full' : 'w-0 group-hover:w-full'"></span>
        </NuxtLink>
        <NuxtLink v-if="isAuthenticated" to="/dashboard" class="hover:text-white transition-all relative group py-2" :class="{ 'text-white': isPageActive('/dashboard') && !isAdmin }">
          Dashboard
          <span class="absolute bottom-0 left-0 h-0.5 bg-purple-500 rounded-full transition-all" :class="isPageActive('/dashboard') && !isAdmin ? 'w-full' : 'w-0 group-hover:w-full'"></span>
        </NuxtLink>
        <NuxtLink v-if="isAdmin" to="/admin/dashboard" class="hover:text-white transition-all relative group py-2" :class="{ 'text-white': isPageActive('/admin/dashboard') }">
          Command Center
          <span class="absolute bottom-0 left-0 h-0.5 bg-purple-500 rounded-full transition-all" :class="isPageActive('/admin/dashboard') ? 'w-full' : 'w-0 group-hover:w-full'"></span>
        </NuxtLink>
      </div>
      
      <!-- Actions -->
      <div class="flex items-center gap-4 sm:gap-6">
        <!-- Theme Toggle -->
        <button 
          @click="toggleTheme" 
          class="p-2.5 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition-all text-slate-400 hover:text-white group relative"
          title="Toggle Theme"
        >
          <svg v-if="theme === 'dark'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M15 12a3 3 0 11-6 0 3 3 0 016 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span class="absolute -bottom-10 left-1/2 -translate-x-1/2 bg-slate-900 px-2 py-1 rounded text-[8px] opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            {{ theme === 'dark' ? 'Mode Terang' : 'Mode Gelap' }}
          </span>
        </button>

        <template v-if="!isAuthenticated">
          <NuxtLink to="/login" class="text-[11px] font-black uppercase tracking-widest text-slate-400 hover:text-white transition-all">
            Masuk
          </NuxtLink>
          <NuxtLink to="/register" class="px-6 py-2.5 bg-white text-slate-950 text-[11px] font-black uppercase tracking-widest rounded-xl hover:bg-purple-50 transition-all active:scale-95 shadow-lg shadow-white/10">
            Daftar
          </NuxtLink>
        </template>
        <template v-else>
          <div class="flex items-center gap-4 pl-4 border-l border-white/10">
            <div class="text-right hidden sm:block">
              <p class="text-[10px] font-black transition-colors uppercase leading-none">{{ user?.full_name?.split(' ')[0] }}</p>
              <p class="text-[8px] font-bold text-slate-500 uppercase tracking-widest mt-1">{{ user?.role }} Node</p>
            </div>
            <button @click="logout" class="p-2.5 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition-all text-slate-400 hover:text-white group">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>
