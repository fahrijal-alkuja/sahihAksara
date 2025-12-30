<script setup lang="ts">
const { register, login } = useAuth()
const router = useRouter()

const form = reactive({
  full_name: '',
  email: '',
  password: ''
})

const isLoading = ref(false)
const errorMsg = ref('')

const handleRegister = async () => {
  if (!form.full_name || !form.email || !form.password) return
  
  isLoading.value = true
  errorMsg.value = ''
  
  try {
    await register(form)
    // Auto login after register
    await login({ email: form.email, password: form.password })
    router.push('/')
  } catch (err: any) {
    errorMsg.value = err.data?.detail || 'Gagal mendaftar. Silakan cek data Anda.'
  } finally {
    isLoading.value = false
  }
}

definePageMeta({
  layout: 'default'
})
</script>

<template>
  <div class="min-h-[90vh] flex items-center justify-center px-4 py-20 relative z-10">
    <div class="max-w-md w-full glass-panel p-12 space-y-10 relative overflow-hidden group">
      <!-- Glow Effects -->
      <div class="absolute -top-24 -right-24 w-64 h-64 bg-blue-600/20 blur-[100px] rounded-full group-hover:bg-blue-600/30 transition-all duration-1000"></div>
      <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-purple-600/10 blur-[80px] rounded-full group-hover:bg-purple-600/20 transition-all duration-1000"></div>
      
      <div class="relative z-10 text-center space-y-3">
        <h2 class="text-4xl font-black text-white font-heading tracking-tight">Create Access</h2>
        <p class="text-slate-500 font-medium tracking-wide">Bergabung dengan jaringan forensik SahihAksara.</p>
      </div>

      <form class="space-y-6 relative z-10" @submit.prevent="handleRegister">
        <div class="space-y-5">
          <div class="space-y-2">
            <label for="name" class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Full Identity (Name)</label>
            <input 
              v-model="form.full_name"
              id="name" 
              type="text" 
              required 
              class="w-full px-6 py-4 bg-slate-900/50 border border-white/10 rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/30 transition-all shadow-inner"
              placeholder="Nama Lengkap Anda"
            >
          </div>
          <div class="space-y-2">
            <label for="email" class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Network Address (Email)</label>
            <input 
              v-model="form.email"
              id="email" 
              type="email" 
              required 
              class="w-full px-6 py-4 bg-slate-900/50 border border-white/10 rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/30 transition-all shadow-inner"
              placeholder="nama@email.com"
            >
          </div>
          <div class="space-y-2">
            <label for="password" class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Secure Key (Password)</label>
            <input 
              v-model="form.password"
              id="password" 
              type="password" 
              required 
              class="w-full px-6 py-4 bg-slate-900/50 border border-white/10 rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/30 transition-all shadow-inner"
              placeholder="Minimal 8 karakter"
            >
          </div>
        </div>

        <div v-if="errorMsg" class="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-[11px] font-black uppercase tracking-widest text-center">
          {{ errorMsg }}
        </div>

        <button 
          type="submit" 
          :disabled="isLoading"
          class="relative w-full py-5 px-6 bg-white text-slate-950 font-black text-xs uppercase tracking-[0.2em] rounded-2xl shadow-[0_20px_40px_rgba(255,255,255,0.05)] transition-all hover:scale-[1.02] hover:bg-slate-100 active:scale-95 disabled:opacity-50 flex items-center justify-center gap-3 overflow-hidden"
        >
          <div v-if="isLoading" class="w-4 h-4 border-2 border-slate-900/30 border-t-slate-900 rounded-full animate-spin"></div>
          <span>{{ isLoading ? 'Mendaftarkan...' : 'Mulai Analisis' }}</span>
        </button>

        <div class="text-center">
          <p class="text-[11px] font-black uppercase tracking-widest text-slate-600">
            Node sudah terdaftar? 
            <NuxtLink to="/login" class="text-blue-400 hover:text-blue-300 transition-colors border-b border-blue-500/30 pb-0.5 ml-1">Masuk Sekarang</NuxtLink>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>
