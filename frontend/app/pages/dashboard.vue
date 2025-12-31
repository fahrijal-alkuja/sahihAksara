<script setup lang="ts">
const { user, fetchMe, logout, initiateUpgrade, token } = useAuth()
const { scanHistory, fetchHistory, clearHistory } = useScanner()

const isGatewayOnline = ref(true)

const checkGatewayHealth = async () => {
    try {
        const data = await $fetch<{ online: boolean }>('http://localhost:8000/health/gateway')
        isGatewayOnline.value = data.online
    } catch (err) {
        isGatewayOnline.value = false
    }
}

onMounted(async () => {
  await fetchMe()
  await fetchHistory()
  checkGatewayHealth()
})

const getStatusColor = (prob: number) => {
  if (prob > 70) return 'text-red-400 bg-red-400/10 border-red-400/20'
  if (prob > 40) return 'text-amber-400 bg-amber-400/10 border-amber-400/20'
  return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const downloadReport = (scan: any) => {
  if (!token.value || !scan.sentences) return
  window.open(`http://localhost:8000/report/${scan.id}?token=${token.value}`, '_blank')
}

definePageMeta({
  layout: 'default',
  middleware: ['auth']
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-6 py-12 space-y-12 relative z-10">
    <SystemAlert 
      :show="!isGatewayOnline" 
      type="warning" 
      message="Sistem pembayaran UnikaPay terdeteksi sedang offline. Beberapa fitur mungkin terbatas."
    />

    <!-- Profile Header (Premium Glass) -->
    <div class="glass-panel p-10 flex flex-col md:flex-row items-center justify-between gap-10 relative overflow-hidden group">
      <!-- Background Ambient Glow -->
      <div class="absolute -top-24 -right-24 w-64 h-64 bg-purple-600/10 blur-[100px] rounded-full group-hover:bg-purple-600/20 transition-all duration-1000"></div>
      <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-blue-600/10 blur-[100px] rounded-full group-hover:bg-blue-600/20 transition-all duration-1000"></div>
      
      <div class="flex items-center gap-8 relative z-10">
        <div class="relative group/avatar">
          <div class="absolute -inset-1 rounded-[2.5rem] bg-gradient-to-tr from-purple-600 to-fuchsia-600 opacity-20 group-hover/avatar:opacity-40 blur-lg transition-opacity duration-700"></div>
          <div class="w-24 h-24 rounded-[2.2rem] bg-slate-900 border border-white/10 flex items-center justify-center text-4xl font-black text-white shadow-2xl relative z-10 font-heading">
            {{ user?.full_name?.charAt(0) || 'U' }}
          </div>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center gap-3">
             <h1 class="text-3xl font-black transition-colors font-heading tracking-tight mb-2">{{ user?.full_name || 'User SahihAksara' }}</h1>
             <span v-if="user?.role === 'pro'" class="text-[10px] font-black text-amber-500 bg-amber-500/10 border border-amber-500/20 px-3 py-1 rounded-full uppercase tracking-widest flex items-center gap-1.5 w-fit">
               <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
               👑 Premium
             </span>
          </div>
          <p class="text-content-muted font-medium tracking-wide flex items-center gap-2">
            <svg class="w-4 h-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            {{ user?.email }}
          </p>
          <div class="pt-2 flex items-center gap-4">
            <div v-if="user?.role === 'free'" class="px-4 py-1.5 bg-white/5 border border-white/10 rounded-xl">
              <span class="text-[10px] text-content-muted font-black uppercase tracking-widest">
                Daily Quota: <span class="transition-colors">{{ user?.daily_quota }} / 5</span>
              </span>
            </div>
            <div v-else class="px-4 py-1.5 bg-purple-500/10 border border-purple-500/20 rounded-xl flex items-center gap-3">
              <span class="text-[10px] text-purple-400 font-black uppercase tracking-widest leading-none">
                Unlimited Forensics Active
              </span>
              <div v-if="user?.pro_expires_at" class="h-3 w-px bg-purple-500/30"></div>
              <span v-if="user?.pro_expires_at" class="text-[9px] text-content-muted font-bold">
                Berakhir: {{ formatDate(user.pro_expires_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap gap-4 relative z-10">
        <button 
          v-if="user?.role === 'free'" 
          @click="isGatewayOnline ? initiateUpgrade() : null"
          :class="{'opacity-50 grayscale cursor-not-allowed': !isGatewayOnline}"
          class="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-amber-600 to-orange-700 hover:from-amber-500 hover:to-orange-600 text-white font-black text-xs uppercase tracking-[0.2em] rounded-2xl transition-all shadow-xl shadow-amber-500/20 active:scale-95 border border-white/10"
        >
          Upgrade ke Pro
        </button>
        <NuxtLink v-if="user?.role === 'admin'" to="/admin/dashboard" class="flex items-center gap-3 px-8 py-4 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 font-black text-xs uppercase tracking-[0.2em] rounded-2xl transition-all active:scale-95 shadow-lg shadow-purple-500/10">
          Admin Panel
        </NuxtLink>
        <NuxtLink to="/history-pembayaran" class="flex items-center gap-3 px-8 py-4 bg-white/5 hover:bg-white/10 text-content-muted hover:text-white font-black text-xs uppercase tracking-[0.2em] rounded-2xl border border-white/5 transition-all active:scale-95">
          History Pembayaran
        </NuxtLink>
        <button @click="logout" class="px-8 py-4 bg-white/5 hover:bg-white/10 text-content-muted hover:text-white font-black text-xs uppercase tracking-[0.2em] rounded-2xl border border-white/5 transition-all active:scale-95">
          Sign Out
        </button>
      </div>
    </div>

    <!-- Stats Grid (Luxury Tiles) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="glass-card p-10 rounded-[2.5rem] relative overflow-hidden group/tile">
        <div class="absolute top-0 right-0 p-6 opacity-5 group-hover/tile:opacity-10 transition-opacity">
           <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z"/></svg>
        </div>
        <h3 class="text-[10px] font-black text-content-muted uppercase tracking-[0.4em] mb-4">Total Analysis</h3>
        <p class="text-5xl font-black transition-colors font-heading tracking-tighter">{{ scanHistory.length }}</p>
        <p class="text-[9px] text-content-muted font-bold uppercase tracking-widest mt-4">Active Session Data</p>
      </div>
      
      <div class="glass-card p-10 rounded-[2.5rem] relative overflow-hidden group/tile">
        <div class="absolute top-0 right-0 p-6 opacity-5 group-hover/tile:opacity-10 transition-opacity">
           <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>
        </div>
        <h3 class="text-[10px] font-black text-content-muted uppercase tracking-[0.4em] mb-4">Node Health</h3>
        <p class="text-5xl font-black text-emerald-400 font-heading tracking-tighter">100%</p>
        <p class="text-[9px] text-emerald-500/80 font-bold uppercase tracking-widest mt-4 flex items-center gap-2">
           <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping"></span>
           Forensic Link Active
        </p>
      </div>

      <div class="glass-card p-10 rounded-[2.5rem] relative overflow-hidden group/tile">
        <div class="absolute top-0 right-0 p-6 opacity-5 group-hover/tile:opacity-10 transition-opacity">
           <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
        </div>
        <h3 class="text-[10px] font-black text-content-muted uppercase tracking-[0.4em] mb-4">Security Protocol</h3>
        <p class="text-5xl font-black transition-colors font-heading tracking-tighter uppercase shrink-0">L3</p>
        <p class="text-[9px] text-content-muted font-bold uppercase tracking-widest mt-4">Verified Authentication</p>
      </div>
    </div>

    <!-- Scan History (Forensic Table) -->
    <div class="glass-panel overflow-hidden border-purple-500/10 mb-20">
      <div class="p-10 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
        <h2 class="text-2xl font-black text-white font-heading tracking-tight flex items-center gap-4">
           Analysis History
           <span class="text-[10px] font-black text-content-muted px-3 py-1 bg-white/5 rounded-full border border-white/5 uppercase tracking-widest">{{ scanHistory.length }} Records</span>
        </h2>
        <button 
          v-if="scanHistory.length > 0"
          @click="clearHistory"
          class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 text-[10px] font-black uppercase tracking-widest transition-all active:scale-95"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Hapus Semua Riwayat
        </button>
      </div>
      
      <div v-if="scanHistory.length === 0" class="p-20 text-center space-y-4 flex flex-col items-center">
        <div class="w-20 h-20 rounded-full bg-white/5 border border-white/5 flex items-center justify-center text-slate-700 mb-4 blur-[0.5px]">
          <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </div>
        <h3 class="text-lg font-bold text-content-muted">No Records Found</h3>
        <p class="text-sm text-content-muted max-w-xs font-medium">Your forensic analysis data will appear here once you begin scanning documents.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left">
          <thead>
            <tr class="bg-white/5 text-content-muted text-[10px] font-black uppercase tracking-[0.3em] border-b border-white/5">
              <th class="px-10 py-6">Forensic Content Overlay</th>
              <th class="px-10 py-6 text-center">AI Intensity</th>
              <th class="px-10 py-6 text-center">Class</th>
              <th class="px-10 py-6 text-right">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr v-for="scan in scanHistory" :key="scan.id" @click="scan.sentences ? downloadReport(scan) : null" 
                :class="scan.sentences ? 'hover:bg-white/[0.03] cursor-pointer' : 'opacity-80 grayscale-[0.3] cursor-not-allowed'"
                class="transition-all duration-300 group">
              <td class="px-10 py-8 align-middle">
                <div class="flex flex-col gap-1.5">
                  <span class="text-sm font-bold line-clamp-1 group-hover:text-purple-500 transition-colors">
                    {{ scan.text_content.includes('[PURGED') ? 'Content Purged for Privacy' : scan.text_content }}
                  </span>
                  <span class="text-[9px] text-content-muted font-black uppercase tracking-widest flex items-center gap-2">
                    <span class="w-1.5 h-1.5 bg-slate-700 rounded-full border border-white/5"></span>
                    ID: {{ scan.id }}
                  </span>
                </div>
              </td>
              <td class="px-10 py-8 align-middle">
                <div class="flex flex-col items-center gap-2">
                  <div class="w-32 bg-slate-900 h-2 rounded-full overflow-hidden border border-white/5 p-[1px] shadow-inner relative">
                    <div class="h-full rounded-full transition-all duration-1000 shadow-lg" :style="{ width: scan.ai_probability + '%', backgroundColor: scan.ai_probability > 70 ? '#f87171' : scan.ai_probability > 40 ? '#fbbf24' : '#10b981', boxShadow: `0 0 10px ${scan.ai_probability > 70 ? 'rgba(248,113,113,0.3)' : scan.ai_probability > 40 ? 'rgba(251,191,36,0.2)' : 'rgba(16,185,129,0.2)'}` }"></div>
                  </div>
                  <span class="text-xs font-black transition-colors font-mono tracking-tighter">{{ scan.ai_probability }}%</span>
                </div>
              </td>
              <td class="px-10 py-8 align-middle text-center">
                <div class="flex justify-center">
                  <span :class="['w-36 py-2.5 rounded-xl text-[9px] font-black uppercase tracking-[0.2em] border shadow-2xl backdrop-blur-md text-center flex items-center justify-center', getStatusColor(scan.ai_probability)]">
                    {{ scan.status }}
                  </span>
                </div>
              </td>
              <td class="px-10 py-8 align-middle text-right">
                <div class="flex flex-col items-end gap-1.5">
                   <span class="text-xs font-bold text-content-muted font-mono transition-colors">{{ formatDate(scan.created_at) }}</span>
                   <div class="flex items-center gap-2">
                    <span class="text-[9px] text-content-muted/80 font-black tracking-widest uppercase">{{ scan.sentences ? 'Verified Entry' : 'Zero-Retention Inactive' }}</span>
                    <div :class="scan.sentences ? 'bg-emerald-500/30' : 'bg-slate-500/20'" class="w-1.5 h-1.5 rounded-full"></div>
                   </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
