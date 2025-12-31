<script setup lang="ts">
const { token, user, isAuthenticated } = useAuth()
const { notify, warning, error: notifyError } = useNotify()
const settings = ref<any[]>([])
const isLoading = ref(true)
const isGatewayOnline = ref(true)

const checkGatewayHealth = async () => {
  try {
    const data = await $fetch<{ online: boolean }>('http://localhost:8000/health/gateway')
    isGatewayOnline.value = data.online
  } catch (err) {
    isGatewayOnline.value = false
  }
}

const plans = {
  free: [
    '5 Cek per hari',
    'Deteksi AI Dasar',
    'Highlight kalimat',
    'Akses Beranda'
  ],
  daily: [
    'Akses tak terbatas 24j',
    'Forensik Mendalam',
    'Download Laporan PDF',
    'Prioritas Antrian',
    'Tanpa Iklan'
  ],
  monthly: [
    'Semua fitur Day Pass',
    'Berlaku selama 30 hari',
    'Analisis Batch Dokumen',
    'Dukungan VIP 24/7',
    'Akses Fitur Beta'
  ]
}

const fetchSettings = async () => {
  isLoading.value = true
  try {
    // Try relative path first for consistency
    const data = await $fetch<any[]>('http://localhost:8000/settings')
    if (data && Array.isArray(data)) {
      settings.value = data
    }
  } catch (err) {
    console.error('Failed to fetch pricing settings:', err)
    notifyError('Gagal memuat data harga terbaru.')
  } finally {
    isLoading.value = false
  }
}

const getSetting = (key: string) => {
  const s = settings.value.find(s => s.key === key)
  return s ? s.value : '0'
}

const isDiscountActive = computed(() => getSetting('is_discount_active') === 'true')

const getPrice = (type: 'daily' | 'monthly') => {
  const base = getSetting(type === 'daily' ? 'pro_day_price' : 'pro_monthly_price')
  const basePrice = Number(base) || 0
  
  const discountStr = getSetting(type === 'daily' ? 'pro_day_discount_percent' : 'pro_discount_percent')
  const discount = isDiscountActive.value ? (Number(discountStr) || 0) : 0
  
  return basePrice * (1 - discount / 100)
}

const getBasePrice = (type: 'daily' | 'monthly') => {
  const base = getSetting(type === 'daily' ? 'pro_day_price' : 'pro_monthly_price')
  return Number(base) || 0
}

// Add declaration for global window object
declare global {
  interface Window {
    snap: any
  }
}

const handleUpgrade = async (planType: string) => {
  if (!isAuthenticated.value) {
    warning('Silakan masuk untuk melanjutkan upgrade.')
    return navigateTo('/login')
  }
  
  isLoading.value = true
  try {
    const data = await $fetch<{ token: string, redirect_url: string }>('http://localhost:8000/payments/create', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}` },
      params: { plan_type: planType }
    })
    
    // Use Snap JS Popup
    if (data.token && typeof window.snap !== 'undefined') {
      window.snap.pay(data.token, {
        onSuccess: function(result: any) {
          notify('Pembayaran berhasil! Akun Anda telah diupgrade.', 'success')
          if (typeof window !== 'undefined') window.location.reload()
        },
        onPending: function(result: any) {
          notify('Menunggu pembayaran Anda...', 'info')
        },
        onError: function(result: any) {
          notifyError('Pembayaran gagal. Silakan coba lagi.')
        },
        onClose: function() {
          notify('Jendela pembayaran ditutup.', 'warning')
        }
      })
    } else if (data.redirect_url) {
      // Fallback if Snap JS fail
      window.location.href = data.redirect_url
    }
  } catch (err) {
    notifyError('Gagal menginisiasi pembayaran. Silakan coba lagi.')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchSettings()
  checkGatewayHealth()
})

definePageMeta({
  layout: 'default'
})
</script>

<template>
  <div class="min-h-[90vh] py-20 px-6 relative overflow-hidden">
    <!-- Ambient Background -->
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full pointer-events-none">
      <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full animate-glow"></div>
      <div class="absolute bottom-[10%] right-[-10%] w-[35%] h-[35%] bg-blue-600/10 blur-[120px] rounded-full animate-glow" style="animation-delay: -4s"></div>
    </div>

    <div class="max-w-4xl mx-auto space-y-16 relative z-10">
      <!-- System Alert -->
      <SystemAlert 
        :show="!isGatewayOnline" 
        type="warning" 
        message="Sistem pembayaran pihak ketiga (UnikaPay) sedang mengalami gangguan teknis. Proses upgrade Pro sementara tidak dapat dilakukan."
      />

      <!-- Header -->
      <div class="text-center space-y-4">
        <h1 class="text-5xl md:text-7xl font-black transition-colors tracking-tighter font-heading">
          Pilih Rencana <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-fuchsia-400">Forensik</span> Anda
        </h1>
        <p class="text-slate-400 text-lg font-medium max-w-2xl mx-auto">
          Akses tak terbatas ke deteksi AI tercanggih. Mulai dari sekali cek hingga langganan bulanan penuh.
        </p>
      </div>

      <!-- Pricing List (Horizontal Pattern) -->
      <div class="space-y-6">
        <!-- 1. Day Pass (Starter) -->
        <div @click="isGatewayOnline ? handleUpgrade('daily') : null" 
             :class="{'opacity-50 grayscale cursor-not-allowed': !isGatewayOnline}"
             class="group relative glass-panel p-8 md:p-10 flex flex-col md:flex-row md:items-center justify-between gap-8 cursor-pointer hover:border-amber-500/30 transition-all duration-500 hover:scale-[1.01]">
          <div class="flex flex-col md:flex-row md:items-center gap-6">
            <div class="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-3xl shrink-0 group-hover:bg-amber-500/20 transition-all">
              ⚡
            </div>
            <div class="space-y-4">
              <div>
                <div class="flex items-center gap-3 mb-1">
                  <h3 class="text-2xl font-black transition-colors font-heading">Day Pass Access</h3>
                  <span class="px-3 py-1 bg-amber-500/10 text-amber-500 text-[10px] font-black uppercase tracking-widest rounded-full border border-amber-500/30">Trial Mode</span>
                </div>
                <p class="text-content-muted text-sm font-medium">Akses tak terbatas selama 24 jam penuh.</p>
              </div>
              <!-- Features -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
                <div v-for="feat in plans.daily" :key="feat" class="flex items-center gap-2 text-[10px] font-bold text-content-muted uppercase tracking-widest">
                  <svg class="w-3.5 h-3.5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  {{ feat }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex flex-row md:flex-col items-center md:items-end gap-4 md:gap-1 ml-auto md:ml-0">
            <div v-if="isDiscountActive && getSetting('pro_day_discount_percent') !== '0'" class="text-sm font-bold text-content-muted/60 line-through">
              Rp {{ getBasePrice('daily').toLocaleString('id-ID') }}
            </div>
            <div class="text-3xl font-black transition-colors font-heading min-w-[140px] text-right">
              <span v-if="isLoading" class="inline-block w-24 h-8 bg-white/5 animate-pulse rounded-lg"></span>
              <template v-else>
                Rp {{ getPrice('daily').toLocaleString('id-ID') }}
                <span class="text-sm text-content-muted font-medium font-sans">/24j</span>
              </template>
            </div>
          </div>
        </div>

        <!-- 2. Pro Monthly (Most Popular) -->
        <div @click="isGatewayOnline ? handleUpgrade('monthly') : null" 
             :class="{'opacity-50 grayscale cursor-not-allowed': !isGatewayOnline}"
             class="group relative glass-panel p-8 md:p-10 flex flex-col md:flex-row md:items-center justify-between gap-8 cursor-pointer border-purple-500/30 ring-1 ring-purple-500/20 hover:border-purple-500/50 transition-all duration-500 hover:scale-[1.01] overflow-hidden">
          <!-- Most Popular Badge -->
          <div class="absolute -top-1 -right-1">
            <div class="bg-gradient-to-r from-purple-500 to-fuchsia-500 text-white text-[9px] font-black uppercase tracking-[0.2em] px-6 py-2 rounded-bl-2xl shadow-xl">
              Most Popular
            </div>
          </div>

          <div class="flex flex-col md:flex-row md:items-center gap-6">
            <div class="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-3xl shrink-0 group-hover:bg-purple-600/20 transition-all">
              💎
            </div>
            <div class="space-y-4">
              <div>
                <div class="flex items-center gap-3 mb-1">
                  <h3 class="text-2xl font-black transition-colors font-heading">Unlimited Monthly</h3>
                  <span v-if="isDiscountActive" class="px-3 py-1 bg-fuchsia-100 text-fuchsia-700 text-[10px] font-black uppercase tracking-widest rounded-full border border-fuchsia-500/20 animate-pulse">Hemat {{ getSetting('pro_discount_percent') }}%</span>
                </div>
                <p class="text-slate-500 text-sm font-medium">Investasi terbaik untuk kreator konten & profesional.</p>
              </div>
              <!-- Features -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
                <div v-for="feat in plans.monthly" :key="feat" class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  <svg class="w-3.5 h-3.5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  {{ feat }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex flex-row md:flex-col items-center md:items-end gap-4 md:gap-1 ml-auto md:ml-0">
            <div v-if="isDiscountActive && getSetting('pro_discount_percent') !== '0'" class="text-sm font-bold text-content-muted/60 line-through">
              Rp {{ getBasePrice('monthly').toLocaleString('id-ID') }}
            </div>
            <div class="text-3xl font-black transition-colors font-heading min-w-[140px] text-right">
              <span v-if="isLoading" class="inline-block w-24 h-8 bg-white/5 animate-pulse rounded-lg"></span>
              <template v-else>
                Rp {{ getPrice('monthly').toLocaleString('id-ID') }}
                <span class="text-sm text-slate-500 font-medium font-sans">/bln</span>
              </template>
            </div>
          </div>
        </div>

        <!-- 3. Free Tier -->
        <div class="glass-panel p-8 md:p-10 flex flex-col md:flex-row md:items-center justify-between gap-8 opacity-60">
          <div class="flex flex-col md:flex-row md:items-center gap-6">
            <div class="w-16 h-16 rounded-2xl bg-slate-800/50 border border-white/5 flex items-center justify-center text-3xl shrink-0">
              🌱
            </div>
            <div class="space-y-4">
              <div>
                <h3 class="text-2xl font-black transition-colors font-heading mb-1">Starter Pack</h3>
                <p class="text-content-muted text-sm font-medium">Batas 5 kali cek per hari untuk semua orang.</p>
              </div>
              <!-- Features -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
                <div v-for="feat in plans.free" :key="feat" class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  {{ feat }}
                </div>
              </div>
            </div>
          </div>
          <div class="text-3xl font-black text-content-muted font-heading ml-auto md:ml-0">GRATIS</div>
        </div>
      </div>

      <!-- Feature Comparison Footer -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 pt-10 border-t border-white/5">
        <div class="space-y-4">
          <h4 class="text-xs font-black text-slate-500 uppercase tracking-widest">Akurasi Forensik</h4>
          <p class="text-sm text-slate-400 font-medium">Model deteksi kami dilatih khusus untuk naskah Indonesia dengan akurasi hingga 99%.</p>
        </div>
        <div class="space-y-4">
          <h4 class="text-xs font-black text-slate-500 uppercase tracking-widest">Laporan Lengkap</h4>
          <p class="text-sm text-slate-400 font-medium">Download sertifikat originalitas PDF untuk setiap naskah yang Anda verifikasi.</p>
        </div>
        <div class="space-y-4">
          <h4 class="text-xs font-black text-slate-500 uppercase tracking-widest">Tanpa Batas</h4>
          <p class="text-sm text-slate-400 font-medium">Tidak ada batasan kata per naskah. Masukkan dokumen setebal apa pun.</p>
        </div>
      </div>
    </div>
  </div>
</template>
