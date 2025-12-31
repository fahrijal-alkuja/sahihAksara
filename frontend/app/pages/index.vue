<script setup>
const { isAuthenticated, user, logout, token, fetchMe } = useAuth()
const { notify, warning, error, showModal } = useNotify()
const { scanResult, isScanning, scanHistory, scanText, uploadFile, fetchHistory } = useScanner()
const textInput = ref('')
const fileInput = ref(null)

const handleScan = () => {
  if (!isAuthenticated.value) {
    showModal('Silakan masuk terlebih dahulu untuk menggunakan layanan SahihAksara.', 'warning')
    return navigateTo('/login')
  }
  if (!textInput.value || textInput.value.length < 50) {
    warning('Harap masukkan minimal 50 karakter untuk analisis yang akurat.')
    return
  }
  scanText(textInput.value)
}

const triggerFileUpload = () => {
  fileInput.value.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const result = await uploadFile(file)
  if (result && result.text_content) {
    textInput.value = result.text_content
  }
}

const downloadReport = () => {
  if (!scanResult.value?.id) return
  window.open(`http://localhost:8000/report/${scanResult.value.id}?token=${token.value}`, '_blank')
}



const loadScanHistory = (item) => {
  scanResult.value = item
  textInput.value = item.text_content
  notify('Berhasil memuat data dari riwayat.', 'info')
  // Scroll to top to see results
  window.scrollTo({ top: 0, behavior: 'smooth' })
}


const getScoreColor = (score) => {
  if (score > 70) return 'text-red-500'
  if (score > 40) return 'text-orange-500'
  if (score > 15) return 'text-amber-500 font-medium'
  return 'text-emerald-500 font-bold'
}

const getStrokeColor = (score) => {
  if (score > 70) return 'stroke-red-500'
  if (score > 40) return 'stroke-orange-500'
  if (score > 15) return 'stroke-amber-500'
  return 'stroke-emerald-500'
}

const getHighlightColor = (score) => {
  if (score === -1) return 'bg-blue-500/20 text-blue-400 border border-blue-500/30' // Non-ID marker
  if (score > 80) return 'bg-red-500/20 text-red-500'
  if (score > 60) return 'bg-amber-500/20 text-amber-500'
  if (score > 40) return 'bg-orange-500/20 text-orange-500'
  return 'bg-emerald-500/20 text-emerald-500'
}

const analysisSummary = computed(() => {
  if (!scanResult.value || !scanResult.value.sentences) return null
  
  const total = scanResult.value.sentences.length
  if (total === 0) return null

  const counts = {
    identical: 0,
    paraphrased: 0,
    mixed: 0,
    human: 0
  }

  scanResult.value.sentences.forEach(s => {
    if (s.score > 75) counts.identical++
    else if (s.score > 50) counts.paraphrased++
    else if (s.score > 25) counts.mixed++
    else counts.human++
  })

  const getPercent = (count) => Math.round((count / total) * 100)

  return {
    identical: getPercent(counts.identical),
    paraphrased: getPercent(counts.paraphrased),
    mixed: getPercent(counts.mixed),
    human: getPercent(counts.human)
  }
})

const integrityVerdict = computed(() => {
  if (!analysisSummary.value) return null
  
  const aiTotal = analysisSummary.value.identical + analysisSummary.value.paraphrased
  const aiSignature = scanResult.value.ai_probability
  
  if (aiTotal < 20 && aiSignature < 50) {
    return {
      status: 'LULUS (PASSED)',
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0',
      recommendation: 'Karya menunjukkan orisinalitas yang kuat. Kontribusi manusia dominan dan penggunaan AI berada dalam batas toleransi wajar ( < 20% ).'
    }
  } else if (aiTotal <= 50) {
    return {
      status: 'PERLU REVISI (REVISION REQUIRED)',
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
      icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      recommendation: 'Ditemukan kontaminasi AI yang signifikan (20% - 50%). Penulis disarankan untuk merumuskan ulang bagian yang terdeteksi AI dengan gaya bahasa sendiri.'
    }
  } else {
    return {
      status: 'INVESTIGASI LANJUT (INVESTIGATE)',
      color: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0',
      recommendation: 'Kadar AI melebihi ambang batas toleransi ( > 50% ). Diperlukan verifikasi lebih lanjut oleh tim editor atau dosen terkait keabsahan naskah ini.'
    }
  }
})

onMounted(async () => {
  if (token.value && !user.value) {
    await fetchMe()
  }
  fetchHistory()
})
</script>

<template>
  <div class="min-h-screen bg-[var(--bg-color)] text-[var(--text-main)] font-sans selection:bg-purple-500/30 overflow-x-hidden transition-colors duration-500">
    <!-- Decorative Background Elements -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div class="absolute -top-24 -left-24 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px] animate-glow"></div>
      <div class="absolute top-1/2 -right-24 w-96 h-96 bg-blue-600/10 rounded-full blur-[120px] animate-glow" style="animation-delay: -4s"></div>
      <div class="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-fuchsia-600/5 rounded-full blur-[150px] animate-glow" style="animation-delay: -2s"></div>
      <div class="absolute top-1/3 left-1/2 -translate-x-1/2 w-full h-full bg-gradient-to-b from-transparent via-[var(--bg-color)] to-[var(--bg-color)] opacity-60 pointer-events-none"></div>
    </div>

    <!-- No more local navbar, handled globally -->

    <main class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <!-- Hero Section -->
      <div class="text-center mb-24 space-y-10 animate-in fade-in slide-in-from-top-6 duration-1000">
        <div class="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-white/5 border border-white/10 text-purple-400 text-[10px] font-black uppercase tracking-[0.4em] backdrop-blur-2xl shadow-2xl hover:border-purple-500/30 transition-all cursor-default group">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-purple-500"></span>
          </span>
          Intelligence V3.0 • Recalibrated
        </div>
        <h1 class="text-6xl sm:text-8xl font-black tracking-tighter leading-[0.85] font-heading drop-shadow-2xl">
          Verifikasi <br class="hidden sm:block" />
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-[var(--text-main)] to-purple-400">Kejujuran Karya</span>
        </h1>
        <p class="text-xl text-theme-dim max-w-2xl mx-auto font-light leading-relaxed tracking-wide opacity-80 decoration-purple-500/30">
          Standar emas deteksi AI untuk <span class="text-theme-main font-bold tracking-tight">Bahasa Indonesia</span>. Menggunakan algoritma <span class="text-indigo-400 font-black italic">Ensemble Deep-Learning</span> yang dioptimasi khusus untuk struktur linguistik nusantara.
        </p>
      </div>

      <div class="grid lg:grid-cols-3 gap-16 items-start">
        <!-- Input Area -->
        <div class="lg:col-span-2 space-y-16">
          <div class="glass-card rounded-[3.5rem] p-3 bg-gradient-to-br from-white/10 via-white/5 to-transparent relative overflow-hidden group/input shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] border-white/5">
            <!-- Animated Background Glows -->
            <div class="absolute -top-32 -right-32 w-80 h-80 bg-indigo-600/10 rounded-full blur-[100px] group-hover/input:bg-indigo-600/20 transition-all duration-1000"></div>
            <div class="absolute -bottom-32 -left-32 w-80 h-80 bg-purple-600/10 rounded-full blur-[100px] group-hover/input:bg-purple-600/20 transition-all duration-1000"></div>
            
            <div class="bg-[var(--panel-bg)] rounded-[3.2rem] p-12 backdrop-blur-3xl border border-white/5 relative z-10">
              <textarea
                v-model="textInput"
                class="w-full h-[480px] bg-transparent border-none focus:ring-0 text-xl lg:text-2xl resize-none placeholder:text-theme-dim/40 text-theme-main leading-relaxed font-light transition-all selection:bg-indigo-500/30 custom-scrollbar pr-4 italic"
                placeholder="Letakkan naskah akademis, artikel, atau esai Anda di sini..."
              ></textarea>
              
              <input 
                type="file" 
                ref="fileInput" 
                class="hidden" 
                accept=".pdf,.docx,.txt"
                @change="handleFileUpload"
              />
              
              <div class="flex flex-col md:flex-row items-center justify-between mt-10 pt-10 border-t border-white/5 gap-8">
                <div class="flex items-center gap-8">
                  <div class="flex flex-col space-y-1">
                    <span class="text-[9px] text-theme-dim font-black uppercase tracking-[0.3em]">Analysis Scope</span>
                    <span class="text-sm text-theme-main font-mono font-medium flex items-center gap-2">
                       <span :class="textInput.length >= 50 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-slate-600'" class="w-1.5 h-1.5 rounded-full transition-colors"></span>
                       {{ textInput.length.toLocaleString() }} <span class="text-[10px] text-theme-dim uppercase font-black">Characters</span>
                    </span>
                  </div>
                  <div v-if="textInput.length > 0 && textInput.length < 50" class="px-4 py-1.5 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                    <span class="text-[9px] text-amber-500 font-black uppercase tracking-widest animate-pulse">Min. 50 Karakter</span>
                  </div>
                </div>
                
                <div class="group/actions flex items-center gap-5">
                  <button 
                    @click="triggerFileUpload"
                    class="h-16 w-16 flex items-center justify-center rounded-2xl bg-[var(--text-main)]/5 border border-theme hover:border-purple-500/30 hover:bg-purple-500/10 transition-all active:scale-90 group/upload"
                    title="Upload File"
                  >
                    <svg class="w-6 h-6 text-theme-dim group-hover/upload:text-purple-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </button>
                  
                  <button
                    @click="handleScan"
                    :disabled="isScanning || textInput.length < 50"
                    class="group relative h-16 px-14 bg-[var(--btn-main)] text-[var(--btn-main-text)] font-black uppercase tracking-[0.3em] text-[10px] rounded-2xl shadow-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-20 disabled:hover:scale-100 flex items-center gap-4 overflow-hidden border border-theme"
                  >
                    <div v-if="isScanning" class="w-4 h-4 border-3 border-current/30 border-t-current rounded-full animate-spin"></div>
                    <span>{{ isScanning ? 'Processing...' : 'Start Intelligence Scan' }}</span>
                    <svg v-if="!isScanning" class="w-4 h-4 group-hover:translate-x-1.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Sentence Highlighting Results -->
          <Transition 
            enter-active-class="transition duration-700 ease-out"
            enter-from-class="transform translate-y-8 opacity-0"
            enter-to-class="transform translate-y-0 opacity-100"
          >
            <div v-if="scanResult && scanResult.sentences" class="glass-card rounded-[3rem] p-10 space-y-8 relative overflow-hidden">
              <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500/50 via-blue-500/50 to-purple-500/50"></div>
              
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div class="space-y-1">
                  <h3 class="text-2xl font-black transition-colors font-heading tracking-tight">Analisis Detail</h3>
                  <div v-if="scanResult.partially_analyzed" class="flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg w-fit mt-2">
                    <svg class="w-3.5 h-3.5 text-amber-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    <span class="text-[9px] font-black text-amber-500 uppercase tracking-widest">Optimasi: Analisis Parsial Aktif (Dokumen Besar)</span>
                  </div>
                  <p v-else class="text-xs text-slate-500 font-medium uppercase tracking-widest">Peta Panas Keaslian Kalimat</p>
                </div>
                <div class="flex items-center gap-6 bg-white/5 px-6 py-3 rounded-2xl border border-white/5 backdrop-blur-md">
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.4)]"></span>
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">AI</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 bg-amber-500 rounded-full shadow-[0_0_8px_rgba(245,158,11,0.4)]"></span>
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Mix</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Human</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.4)]"></span>
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Non-ID</span>
                  </div>
                </div>
              </div>
              
              <div class="p-10 bg-[var(--panel-bg)] rounded-[2.5rem] border border-theme leading-[1.8] text-xl font-light text-theme-main shadow-inner max-h-[500px] overflow-y-auto custom-scrollbar">
                <span 
                  v-for="(sent, idx) in scanResult.sentences" 
                  :key="idx"
                  :class="getHighlightColor(sent.score)"
                  class="inline-block px-1.5 rounded-lg transition-all duration-300 cursor-default"
                >
                  {{ sent.text }}&nbsp;
                </span>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Sidebar Section (Scores & History) -->
        <div class="space-y-8">
          <!-- Result Container with Transition -->
          <Transition name="fade" mode="out-in">
            <div v-if="isScanning" key="loading" class="glass-card rounded-[2.5rem] p-8">
              <SkeletonLoader />
            </div>

            <div v-else-if="scanResult" key="result" class="space-y-6">
              <!-- Score Ring & Matrix -->
              <div class="glass-card rounded-[2.5rem] p-8 space-y-8 relative overflow-hidden group/main-score border-white/10 shadow-2xl">
                <div :class="getScoreColor(scanResult.ai_probability)" class="absolute -right-20 -top-20 w-40 h-40 opacity-10 blur-[80px] rounded-full transition-all duration-1000"></div>
                
                <div class="flex items-center justify-between relative z-10 transition-colors">
                  <h3 class="text-[9px] font-black text-theme-dim uppercase tracking-[0.3em]">Detection Matrix</h3>
                  <div :class="getScoreColor(scanResult.ai_probability)" class="text-[9px] font-black px-3 py-1 bg-[var(--text-main)]/5 rounded-full border border-theme flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                    {{ scanResult.status.toUpperCase() }}
                  </div>
                </div>
                
                <div class="flex flex-col items-center py-2 relative">
                  <div class="relative w-56 h-56 flex items-center justify-center group-hover/main-score:scale-105 transition-transform duration-700">
                    <div :class="getScoreColor(scanResult.ai_probability)" class="absolute inset-0 rounded-full blur-[30px] opacity-10"></div>
                    <svg class="w-full h-full transform -rotate-90 relative z-10">
                      <circle cx="112" cy="112" r="95" fill="none" stroke="currentColor" stroke-width="10" class="text-slate-900/40" />
                      <circle cx="112" cy="112" r="95" fill="none" stroke="currentColor" stroke-width="10" 
                        :stroke-dasharray="597" 
                        :stroke-dashoffset="597 - (597 * (scanResult.ai_probability) / 100)"
                        :class="getStrokeColor(scanResult.ai_probability)"
                        class="transition-all duration-[2000ms] ease-out" 
                        stroke-linecap="round"
                      />
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center z-20">
                      <span class="text-6xl font-black text-theme-main transition-colors leading-none tracking-tighter">{{ Math.round(scanResult.ai_probability) }}<span class="text-2xl text-theme-dim">%</span></span>
                      <span class="text-[9px] text-theme-dim uppercase tracking-[0.3em] mt-4 font-black">AI Signature</span>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4 relative z-10">
                  <div class="bg-[var(--text-main)]/5 p-4 rounded-3xl border border-theme text-center group/metric hover:border-purple-500/20 transition-all">
                    <div class="text-[8px] text-theme-dim font-bold uppercase tracking-widest mb-1.5">Word Density</div>
                    <div class="text-lg font-mono font-bold text-theme-main">{{ scanResult.perplexity?.toFixed(3) }}</div>
                  </div>
                  <div class="bg-[var(--text-main)]/5 p-4 rounded-3xl border border-theme text-center group/metric hover:border-blue-500/20 transition-all">
                    <div class="text-[8px] text-theme-dim font-bold uppercase tracking-widest mb-1.5">Structural Flex</div>
                    <div class="text-lg font-mono font-bold text-theme-main">{{ scanResult.burstiness?.toFixed(3) }}</div>
                  </div>
                </div>
              </div>

              <!-- Ensemble Debate -->
              <div v-if="scanResult.opinion_semantic !== undefined" class="glass-card rounded-[2.5rem] p-8 space-y-6 relative overflow-hidden group/ensemble border-white/10">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="text-[9px] font-black text-theme-dim uppercase tracking-[0.3em] flex items-center gap-2">
                    <svg class="w-3 h-3 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    Ensemble Debate
                  </h4>
                  <span class="text-[8px] font-black text-indigo-400/80 uppercase tracking-widest bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">Multi-Model</span>
                </div>

                <div class="space-y-4">
                  <!-- Opinions with Thinner Bars -->
                  <div v-for="(val, label, idx) in { 
                    'Semantic Opinion': scanResult.opinion_semantic, 
                    'Perplexity Opinion': scanResult.opinion_perplexity, 
                    'Burstiness Opinion': scanResult.opinion_burstiness 
                  }" :key="idx" class="space-y-1.5">
                    <div class="flex justify-between text-[8px] font-bold uppercase tracking-wider text-theme-dim">
                      <span>{{ idx + 1 }}. {{ label }}</span>
                      <span class="text-theme-main">{{ val?.toFixed(1) }}%</span>
                    </div>
                    <div class="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden p-[1px]">
                      <div :style="{ width: val + '%' }" 
                        :class="idx === 0 ? 'bg-blue-500' : idx === 1 ? 'bg-purple-500' : 'bg-orange-500'" 
                        class="h-full transition-all duration-1000 shadow-[0_0_8px_rgba(255,255,255,0.1)]"></div>
                    </div>
                  </div>

                  <!-- Humanity Bonus -->
                  <div class="space-y-1.5 pt-2">
                    <div class="flex justify-between text-[8px] font-bold uppercase tracking-wider text-emerald-500">
                      <span>4. Humanity Bonus</span>
                      <span class="text-emerald-400">-{{ scanResult.opinion_humanity?.toFixed(1) }}%</span>
                    </div>
                    <div class="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden p-[1px]">
                      <div :style="{ width: Math.min(100, (scanResult.opinion_humanity || 0) * 1) + '%' }" 
                        class="h-full bg-emerald-500 transition-all duration-1000"></div>
                    </div>
                  </div>
                </div>
                
                <p class="text-[8px] text-theme-dim leading-relaxed font-medium mt-2 italic decoration-slate-500/20">
                  *Skor akhir dihitung berdasarkan bobot musyawarah: 55% Semantic, 30% Perplexity, 15% Burstiness, dikurangi Bonus.
                </p>
              </div>

              <!-- Integrity Verdict (Unified) -->
              <div v-if="integrityVerdict" :class="[integrityVerdict.bg, integrityVerdict.border]" class="p-6 rounded-[2rem] border relative overflow-hidden group/verdict shadow-lg transition-all hover:shadow-xl">
                <div class="absolute top-0 right-0 p-4 opacity-10 group-hover/verdict:scale-110 transition-transform">
                   <svg class="w-12 h-12" :class="integrityVerdict.color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path :d="integrityVerdict.icon" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                   </svg>
                </div>
                <div class="relative z-10 space-y-3">
                  <h4 class="text-[9px] font-black uppercase tracking-[0.2em] opacity-80" :class="integrityVerdict.color">Asesmen Integritas</h4>
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-black tracking-tight" :class="integrityVerdict.color">{{ integrityVerdict.status }}</span>
                  </div>
                  <p class="text-[10px] text-theme-dim leading-relaxed font-medium pr-8">
                    {{ integrityVerdict.recommendation }}
                  </p>
                </div>
              </div>

              <!-- Compact Composition -->
              <div v-if="analysisSummary" class="glass-card rounded-[2.5rem] p-8 space-y-6 relative overflow-hidden border border-white/5 shadow-xl transition-colors">
                <div class="flex items-center justify-between">
                  <h4 class="text-[9px] font-black text-theme-dim uppercase tracking-[0.3em]">Text Composition</h4>
                  <span class="text-[8px] text-theme-dim font-mono tracking-widest">{{ scanResult.sentences.length }} SENTENCES</span>
                </div>

                <div class="h-1.5 w-full bg-slate-900 rounded-full flex overflow-hidden p-[1px]">
                  <div :style="{ width: analysisSummary.identical + '%' }" class="h-full bg-red-500 rounded-full transition-all duration-1000 shadow-[0_0_10px_rgba(239,68,68,0.3)]"></div>
                  <div :style="{ width: analysisSummary.paraphrased + '%' }" class="h-full bg-orange-500 rounded-full transition-all duration-1000 shadow-[0_0_10px_rgba(249,115,22,0.3)]"></div>
                  <div :style="{ width: analysisSummary.mixed + '%' }" class="h-full bg-amber-500 rounded-full transition-all duration-1000 shadow-[0_0_10px_rgba(245,158,11,0.3)]"></div>
                  <div :style="{ width: analysisSummary.human + '%' }" class="h-full bg-emerald-500 rounded-full transition-all duration-1000 shadow-[0_0_10px_rgba(16,185,129,0.3)]"></div>
                </div>

                <div class="grid grid-cols-2 gap-y-3 gap-x-4">
                  <div v-for="(val, label, idx) in { 
                    'AI Identic': { val: analysisSummary.identical, color: 'bg-red-500' },
                    'Parafrasa': { val: analysisSummary.paraphrased, color: 'bg-orange-500' },
                    'Campuran': { val: analysisSummary.mixed, color: 'bg-amber-500' },
                    'Manusia': { val: analysisSummary.human, color: 'bg-emerald-500' }
                  }" :key="idx" class="flex items-center gap-2">
                    <div :class="val.color" class="w-1.5 h-1.5 rounded-full"></div>
                    <span class="text-[9px] font-bold text-theme-dim transition-colors"><span class="text-theme-main">{{ val.val }}%</span> {{ label }}</span>
                  </div>
                </div>

                <!-- Action Button -->
                <div class="pt-4 mt-2">
                  <button 
                    @click="downloadReport"
                    class="w-full h-12 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-black text-[10px] uppercase tracking-[0.2em] transition-all transform active:scale-95 flex items-center justify-center gap-3 shadow-lg hover:shadow-indigo-500/20"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    Unduh Laporan PDF
                  </button>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else key="empty" class="glass-card rounded-[3rem] p-12 flex flex-col items-center justify-center text-center space-y-8 min-h-[400px]">
              <div class="relative">
                <div class="w-24 h-24 bg-gradient-to-tr from-purple-600/20 to-blue-600/20 rounded-full flex items-center justify-center text-slate-500 border border-white/5 shadow-2xl relative z-10">
                  <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </div>
                <div class="absolute inset-0 bg-purple-500/10 blur-3xl rounded-full animate-pulse px-4"></div>
              </div>
              <div class="space-y-2 px-6">
                <h3 class="text-xl font-bold text-white font-heading">Siap Verifikasi?</h3>
                <p class="text-sm text-slate-500 leading-relaxed font-light">Karya tulis yang jujur adalah fondasi dari kredibilitas akademik. Masukkan teks Anda untuk mulai.</p>
              </div>
            </div>
          </Transition>

          <!-- History Container -->
          <div class="glass-card rounded-[3rem] p-10 space-y-8">
            <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] px-2 flex justify-between items-center">
              Session History
              <span class="px-3 py-1 bg-white/5 rounded-full text-[10px] font-black text-slate-400 border border-white/5">{{ scanHistory.length }}</span>
            </h3>
            
            <div v-if="scanHistory.length === 0" class="flex flex-col items-center justify-center py-12 text-slate-700 gap-4 border-2 border-dashed border-white/5 rounded-[2.5rem]">
              <svg class="w-10 h-10 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <p class="text-[10px] font-black uppercase tracking-widest opacity-50 px-2 leading-none">Intelligence Required</p>
            </div>
            
            <div v-else class="space-y-4 max-h-[450px] overflow-y-auto pr-3 custom-scrollbar">
              <div 
                v-for="item in scanHistory" 
                :key="item.id" 
                @click="loadScanHistory(item)"
                :class="scanResult?.id === item.id ? 'border-purple-500 bg-slate-900/80' : 'border-white/5 bg-slate-900/40'"
                class="p-5 rounded-3xl border hover:border-purple-500/40 transition-all cursor-pointer group hover:bg-slate-900/60 shadow-lg relative overflow-hidden"
              >
                <div class="flex justify-between items-center mb-4">
                  <div class="flex items-center gap-2">
                    <div :class="getScoreColor(item.ai_probability)" class="w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]"></div>
                    <span class="text-[10px] text-slate-500 font-black tracking-widest uppercase">{{ new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
                  </div>
                  <div class="text-[10px] font-black text-purple-400/50 uppercase tracking-widest">SAVED</div>
                </div>
                
                <div class="flex items-center gap-4 relative z-10 w-full">
                  <div class="w-14 h-14 shrink-0 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center text-xl font-black text-white shadow-xl relative overflow-hidden group-hover:rotate-6 transition-transform">
                    <div class="absolute inset-0 bg-gradient-to-tr from-purple-600/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    {{ Math.round(item.ai_probability) }}%
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{{ new Date(item.created_at).toLocaleDateString() }}</div>
                    <div class="text-xs text-slate-100 font-light truncate leading-relaxed">{{ (item.text_content || '').substring(0, 60) }}...</div>
                  </div>
                </div>
                <!-- Animated Gradient Slide (Simplified) -->
                <div class="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-purple-600 via-fuchsia-600 to-blue-600 w-0 group-hover:w-full transition-all duration-700 opacity-50"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-white/5 bg-slate-950/80 pt-16 pb-8 relative z-10">
      <div class="max-w-7xl mx-auto px-4 grid sm:grid-cols-2 gap-12 mb-16">
        <div class="space-y-6">
          <div class="flex items-center gap-4">
            <img src="/logo.png" alt="SahihAksara" class="w-10 h-10 rounded-lg bg-white p-1" />
            <span class="text-xl font-bold text-white font-heading">SahihAksara</span>
          </div>
          <p class="text-sm text-slate-500 max-w-xs leading-relaxed font-light">
            Membangun ekosistem akademik yang jujur melalui teknologi verifikasi teks mutakhir.
          </p>
        </div>
        <div class="flex sm:justify-end gap-16">
          <div class="space-y-6">
            <h5 class="text-[10px] font-black text-white uppercase tracking-[0.3em]">Halaman</h5>
            <ul class="text-xs text-slate-500 space-y-3 font-medium">
              <li class="hover:text-white cursor-pointer transition-colors"><NuxtLink to="/">Analisis Teks</NuxtLink></li>
              <li class="hover:text-white cursor-pointer transition-colors"><NuxtLink to="/cara-kerja">Cara Kerja</NuxtLink></li>
              <li class="hover:text-white cursor-pointer transition-colors"><NuxtLink to="/kebijakan-privasi">Kebijakan Privasi</NuxtLink></li>
            </ul>
          </div>
          <div class="space-y-6">
            <h5 class="text-[10px] font-black text-white uppercase tracking-[0.3em]">Developer</h5>
            <ul class="text-xs text-slate-500 space-y-3 font-medium">
              <li class="text-slate-400">Universitas Kutai Kartanegara</li>
              <li class="text-slate-400">TIM IT Fahrijal</li>
            </ul>
          </div>
        </div>
      </div>
      <div class="border-t border-white/5 pt-8 text-center px-4">
        <p class="text-[9px] text-slate-600 uppercase tracking-[0.4em] font-medium leading-loose">
          © 2025 SahihAksara. Dikembangkan untuk Integritas Akademik UNIKARTA.
        </p>
      </div>
    </footer>

  </div>
</template>

