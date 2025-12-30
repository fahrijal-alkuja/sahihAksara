<script setup lang="ts">
const { token, user, isAdmin } = useAuth()

const stats = ref<any>({})
const users = ref<any[]>([])
const settings = ref<any[]>([])
const isLoading = ref(true)

const fetchAdminData = async () => {
  isLoading.value = true
  try {
    const [statsData, usersData, settingsData] = await Promise.all([
      $fetch<any>('http://localhost:8000/admin/stats', {
        headers: { Authorization: `Bearer ${token.value}` }
      }),
      $fetch<any[]>('http://localhost:8000/admin/users', {
        headers: { Authorization: `Bearer ${token.value}` }
      }),
      $fetch<any[]>('http://localhost:8000/admin/settings', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
    ])
    stats.value = statsData
    users.value = usersData
    settings.value = settingsData
  } catch (err) {
    console.error('Failed to fetch admin data:', err)
  } finally {
    isLoading.value = false
  }
}

const updateUser = async (userId: number, update: any) => {
  try {
    await $fetch(`http://localhost:8000/admin/users/${userId}`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token.value}` },
      body: update
    })
    await fetchAdminData() // Refresh
  } catch (err) {
    alert('Gagal mengupdate user.')
  }
}

const updateSetting = async (key: string, value: any) => {
  try {
    await $fetch(`http://localhost:8000/admin/settings/${key}`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token.value}` },
      body: { value: value.toString() }
    })
    await fetchAdminData()
  } catch (err) {
    alert('Gagal mengupdate setting.')
  }
}

const getSetting = (key: string) => {
  return settings.value.find(s => s.key === key)?.value || '0'
}

onMounted(() => {
  if (!isAdmin.value) {
    return navigateTo('/')
  }
  fetchAdminData()
})

definePageMeta({
  layout: 'default',
  middleware: ['auth']
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-6 py-12 space-y-12 relative z-10">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <h1 class="text-5xl font-black transition-colors tracking-tighter font-heading">Command Center</h1>
        <p class="text-content-muted font-medium tracking-wide mt-2">Pusat kendali operasional dan manajemen forensik naskah SahihAksara.</p>
      </div>
      <div class="flex items-center gap-4 bg-purple-600/10 border border-purple-500/20 px-6 py-3 rounded-2xl backdrop-blur-md">
        <div class="flex items-center gap-3">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-purple-500"></span>
          </span>
          <span class="text-[10px] font-black uppercase tracking-[0.4em] text-purple-400">Strict Protocol Active</span>
        </div>
      </div>
    </div>

    <!-- Analytics Cards (Luxury Grid) -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
      <div v-for="(val, label) in { 'Verified Nodes': stats.total_users, 'Daily Intensity': stats.scans_today, 'Elite Access': stats.pro_users, 'Total Analysis': stats.total_scans }" :key="label" 
           class="glass-card p-10 rounded-[2.5rem] relative overflow-hidden group/tile">
        <div class="absolute -bottom-8 -right-8 w-24 h-24 bg-white/5 blur-3xl rounded-full group-hover:bg-purple-600/10 transition-all duration-700"></div>
        <h3 class="text-content-muted text-[10px] font-black uppercase tracking-[0.3em] mb-4">{{ label }}</h3>
        <p class="text-4xl font-black transition-colors font-heading tracking-tighter">{{ val || 0 }}</p>
        <div class="w-full h-1 bg-white/5 rounded-full mt-6 overflow-hidden">
           <div class="h-full bg-gradient-to-r from-purple-500 to-fuchsia-500 w-1/2 animate-pulse"></div>
        </div>
      </div>
    </div>

    <!-- Revenue & Pricing Management (Premium Panel) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Monthly Plan -->
      <div class="glass-panel p-10 space-y-8">
         <div class="flex items-center justify-between gap-4 mb-2">
            <div class="flex items-center gap-4">
               <div class="p-2.5 bg-emerald-500/20 rounded-xl border border-emerald-500/30">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8c-1.657 0-3 1.343-3 3s1.343 3 3 3 3-1.343 3-3-1.343-3-3-3zM12 8V7m0 1v1m0 9v1m0-1v-1m4-4h1m-1 0h-1m-7 0H7m1 0h1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
               </div>
               <h2 class="text-xl font-black transition-colors font-heading">Pro Monthly Plan</h2>
            </div>
            <button 
              @click="updateSetting('is_discount_active', getSetting('is_discount_active') === 'true' ? 'false' : 'true')"
              :class="getSetting('is_discount_active') === 'true' ? 'bg-fuchsia-500 text-white px-4 shadow-lg shadow-fuchsia-500/20' : 'bg-white/5 text-content-muted px-6'"
              class="py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border border-white/5 hover:border-white/10"
            >
              {{ getSetting('is_discount_active') === 'true' ? 'Promos On' : 'Promos Off' }}
            </button>
         </div>
        
        <div class="space-y-6">
          <div class="space-y-3">
             <label class="text-[10px] font-black text-content-muted uppercase tracking-widest ml-1">Base Monthly Price (IDR)</label>
             <div class="relative">
                <input 
                  type="number" 
                  :value="getSetting('pro_monthly_price')"
                  @blur="updateSetting('pro_monthly_price', ($event.target as HTMLInputElement).value)"
                  class="w-full bg-slate-900 border border-theme rounded-2xl px-6 py-4 text-white font-black text-lg focus:ring-2 focus:ring-emerald-500/30 outline-none transition-all placeholder-slate-700"
                  placeholder="100000"
                />
                <span class="absolute right-6 top-1/2 -translate-y-1/2 text-[10px] font-black text-content-muted uppercase">Per Node</span>
             </div>
          </div>

          <div class="space-y-3">
             <label class="text-[10px] font-black text-content-muted uppercase tracking-widest ml-1">Monthly Discount (%)</label>
             <div class="relative">
                <input 
                  type="number" 
                  min="0"
                  max="100"
                  :value="getSetting('pro_discount_percent')"
                  @blur="updateSetting('pro_discount_percent', ($event.target as HTMLInputElement).value)"
                  class="w-full bg-slate-900 border border-theme rounded-2xl px-6 py-4 text-white font-black text-lg focus:ring-2 focus:ring-emerald-500/30 outline-none transition-all placeholder-slate-700"
                  placeholder="0"
                />
                <span class="absolute right-6 top-1/2 -translate-y-1/2 text-xl font-black text-content-muted">%</span>
             </div>
          </div>

          <div class="p-6 bg-emerald-500/5 border border-emerald-500/10 rounded-2xl flex items-center justify-between">
             <div class="space-y-1">
                <p class="text-xs font-bold text-emerald-400">Monthly Yield</p>
                <p class="text-[10px] text-content-muted font-black uppercase tracking-widest">Calculated Net per Seat</p>
             </div>
             <p class="text-2xl font-black text-white font-heading">
                Rp {{ (Number(getSetting('pro_monthly_price')) * (1 - (getSetting('is_discount_active') === 'true' ? Number(getSetting('pro_discount_percent')) : 0) / 100)).toLocaleString('id-ID') }}
             </p>
          </div>
        </div>
      </div>

      <!-- Day Pass Plan -->
      <div class="glass-panel p-10 space-y-8">
         <div class="flex items-center gap-4">
            <div class="p-2.5 bg-amber-500/20 rounded-xl border border-amber-500/30">
                 <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5a2 2 0 10-2 2h2zm0 0h1m-1 0H7m11 0h1M5 8h2m10 0h2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <h2 class="text-xl font-black transition-colors font-heading">Pro Day Pass</h2>
         </div>

        <div class="space-y-6">
           <div class="space-y-3">
              <label class="text-[10px] font-black text-content-muted uppercase tracking-widest ml-1">Day Pass Price (IDR)</label>
              <div class="relative">
                 <input 
                   type="number" 
                   :value="getSetting('pro_day_price')"
                   @blur="updateSetting('pro_day_price', ($event.target as HTMLInputElement).value)"
                   class="w-full bg-slate-900 border border-theme rounded-2xl px-6 py-4 text-white font-black text-lg focus:ring-2 focus:ring-amber-500/30 outline-none transition-all"
                 />
                 <span class="absolute right-6 top-1/2 -translate-y-1/2 text-[10px] font-black text-content-muted uppercase">24h Access</span>
              </div>
           </div>

           <div class="space-y-3">
              <label class="text-[10px] font-black text-content-muted uppercase tracking-widest ml-1">Day Pass Discount (%)</label>
              <div class="relative">
                 <input 
                   type="number" 
                   min="0"
                   max="100"
                   :value="getSetting('pro_day_discount_percent')"
                   @blur="updateSetting('pro_day_discount_percent', ($event.target as HTMLInputElement).value)"
                   class="w-full bg-slate-900 border border-theme rounded-2xl px-6 py-4 text-white font-black text-lg focus:ring-2 focus:ring-amber-500/30 outline-none transition-all"
                 />
                 <span class="absolute right-6 top-1/2 -translate-y-1/2 text-xl font-black text-content-muted">%</span>
              </div>
           </div>

           <div class="p-6 bg-amber-500/5 border border-amber-500/10 rounded-2xl flex items-center justify-between">
              <div class="space-y-1">
                 <p class="text-xs font-bold text-amber-400">Day Pass Yield</p>
                 <p class="text-[10px] text-content-muted font-black uppercase tracking-widest">Net Revenue</p>
              </div>
              <p class="text-2xl font-black text-white font-heading">
                 Rp {{ (Number(getSetting('pro_day_price')) * (1 - (getSetting('is_discount_active') === 'true' ? Number(getSetting('pro_day_discount_percent')) : 0) / 100)).toLocaleString('id-ID') }}
              </p>
           </div>
        </div>
      </div>
    </div>

    <!-- User Management Section (Forensic Panel) -->
    <div class="glass-panel overflow-hidden border-white/5 shadow-[0_50px_100px_-20px_rgba(0,0,0,0.8)]">
      <div class="p-10 border-b border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-6 bg-white/[0.02]">
        <div class="flex items-center gap-5">
           <div class="p-3 bg-purple-600/20 rounded-2xl border border-purple-500/30">
              <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
           </div>
           <h2 class="text-2xl font-black transition-colors font-heading tracking-tight">Node Management</h2>
        </div>
        <button @click="fetchAdminData" class="btn-premium flex items-center gap-3 bg-white/5 border border-white/10 hover:border-purple-500/30 text-slate-300">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Sync Records
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-white/5 text-content-muted text-[10px] font-black uppercase tracking-[0.3em]">
            <tr>
              <th class="px-10 py-6">Operator Identity</th>
              <th class="px-10 py-6">Access Tier</th>
              <th class="px-10 py-6 text-center">Quota Limit</th>
              <th class="px-10 py-6 text-center">Onboarded</th>
              <th class="px-10 py-6 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr v-for="u in users" :key="u.id" class="hover:bg-white/[0.02] transition-all group">
              <td class="px-10 py-8 align-middle">
                <div class="flex items-center gap-5">
                  <div class="w-12 h-12 rounded-[1.2rem] bg-slate-900 border border-white/10 flex items-center justify-center text-lg font-black text-content-muted group-hover:text-white group-hover:border-purple-500/30 transition-all font-heading shadow-lg">
                    {{ u.full_name?.charAt(0) }}
                  </div>
                  <div class="space-y-1">
                    <div class="text-sm font-bold group-hover:text-purple-500 transition-colors">{{ u.full_name }}</div>
                    <div class="text-[10px] text-content-muted font-mono tracking-tight">{{ u.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-10 py-8 align-middle">
                <div class="relative inline-block w-full min-w-[140px]">
                  <select 
                    @change="updateUser(u.id, { role: ($event.target as HTMLSelectElement).value })"
                    class="appearance-none w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all cursor-pointer hover:border-purple-500/30"
                  >
                    <option value="free" :selected="u.role === 'free'" class="bg-slate-900">Free Tier</option>
                    <option value="pro" :selected="u.role === 'pro'" class="bg-slate-900 text-amber-400">Pro Tier</option>
                    <option value="admin" :selected="u.role === 'admin'" class="bg-slate-900 text-purple-400">Admin</option>
                  </select>
                  <div class="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-content-muted">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </div>
                </div>
              </td>
              <td class="px-10 py-8 align-middle">
                <div class="flex items-center justify-center">
                  <input 
                    type="number"
                    :value="u.daily_quota"
                    @blur="updateUser(u.id, { daily_quota: parseInt(($event.target as HTMLInputElement).value) })"
                    class="w-20 bg-slate-900 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-center font-bold text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all hover:border-white/20"
                  />
                </div>
              </td>
              <td class="px-10 py-8 align-middle text-center">
                <div class="flex flex-col items-center gap-1.5">
                   <span class="text-xs font-bold text-content-muted font-mono">{{ u.created_at?.split('T')[0] }}</span>
                   <div class="flex items-center gap-2">
                     <span class="text-[8px] text-content-muted font-black uppercase tracking-widest leading-none">Registry Date</span>
                     <div class="w-1 h-1 rounded-full bg-slate-700"></div>
                   </div>
                </div>
              </td>
              <td class="px-10 py-8 align-middle text-right">
                <button 
                  @click="updateUser(u.id, { is_active: u.is_active === 1 ? 0 : 1 })"
                  :class="u.is_active === 0 
                    ? 'text-emerald-400 hover:text-emerald-300 border-emerald-500/20 hover:border-emerald-400/50 hover:bg-emerald-400/10' 
                    : 'text-content-muted hover:text-red-400 border-white/5 hover:border-red-400/20 hover:bg-red-400/5'"
                  class="px-6 py-2.5 text-[10px] font-black uppercase tracking-widest border rounded-xl transition-all shadow-sm bg-white/[0.02]"
                >
                  {{ u.is_active === 0 ? 'Restore Node' : 'Restrict Node' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
