<script setup>
const { isAuthenticated, user, logout, token } = useAuth()
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
  if (score > 70) return 'bg-red-500/20 text-red-100 ring-1 ring-red-500/30'
  if (score > 40) return 'bg-orange-500/15 text-orange-100 ring-1 ring-orange-500/20'
  if (score > 15) return 'bg-amber-500/10 text-amber-100/90'
  return 'text-emerald-400/90 hover:bg-emerald-500/5 transition-colors'
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
    if (s.score > 70) counts.identical++
    else if (s.score > 40) counts.paraphrased++
    else if (s.score > 15) counts.mixed++
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

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-purple-500/30 overflow-x-hidden">
    <!-- Decorative Background Elements -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div class="absolute -top-24 -left-24 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px] animate-glow"></div>
      <div class="absolute top-1/2 -right-24 w-96 h-96 bg-blue-600/15 rounded-full blur-[120px] animate-glow" style="animation-delay: -4s"></div>
      <div class="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-fuchsia-600/10 rounded-full blur-[150px] animate-glow" style="animation-delay: -2s"></div>
      <div class="absolute top-1/3 left-1/2 -translate-x-1/2 w-full h-full bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950 pointer-events-none"></div>
    </div>

    <!-- No more local navbar, handled globally -->

    <main class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <!-- Hero Section -->
      <div class="text-center mb-20 space-y-8 animate-in fade-in slide-in-from-top-4 duration-1000">
        <div class="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-slate-900/50 border border-white/10 text-purple-400 text-[10px] font-black uppercase tracking-[0.3em] backdrop-blur-md shadow-xl">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-purple-500"></span>
          </span>
          V3.0 Powered by IndoBERT
        </div>
        <h1 class="text-5xl sm:text-7xl font-black transition-colors tracking-tighter leading-[0.9] font-heading drop-shadow-2xl">
          Ulas Keaslian <br class="hidden sm:block" />
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-white to-blue-400">Karya Tulis Anda</span>
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto font-light leading-relaxed tracking-wide">
          Satu-satunya detektor AI yang dirancang khusus untuk <span class="text-slate-100 font-medium border-b border-purple-500/50">Bahasa Indonesia</span>. Mendeteksi pola GPT, Gemini, dan model AI lainnya dengan akurasi kelas dunia.
        </p>
      </div>

      <div class="grid lg:grid-cols-3 gap-12 items-start">
        <!-- Input & Results Area -->
        <div class="lg:col-span-2 space-y-12">
          <div class="glass-card rounded-[3rem] p-2 bg-gradient-to-br from-white/10 via-white/5 to-transparent relative overflow-hidden group">
            <!-- Decorative Inner Glow -->
            <div class="absolute -top-24 -right-24 w-64 h-64 bg-purple-600/20 rounded-full blur-[80px] group-hover:bg-purple-600/30 transition-all duration-700"></div>
            
            <div class="bg-slate-950/60 rounded-[2.8rem] p-10 backdrop-blur-3xl border border-white/5 relative z-10">
              <div class="absolute top-0 right-0 p-8">
                <div class="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse shadow-[0_0_10px_rgba(168,85,247,0.5)]"></div>
              </div>
              
              <textarea
                v-model="textInput"
                class="w-full h-[450px] bg-transparent border-none focus:ring-0 text-xl resize-none placeholder:text-slate-500 leading-relaxed font-light transition-colors selection:bg-purple-500/40"
                placeholder="Tempelkan naskah Anda di sini untuk memulai verifikasi keaslian..."
              ></textarea>
              
              <input 
                type="file" 
                ref="fileInput" 
                class="hidden" 
                accept=".pdf,.docx,.txt"
                @change="handleFileUpload"
              />
              
              <div class="flex flex-col sm:flex-row items-center justify-between mt-8 pt-8 border-t border-white/5 gap-6">
                <div class="flex items-center gap-6">
                  <div class="flex flex-col">
                    <span class="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-1">Status Dokumen</span>
                    <span class="text-xs text-slate-300 font-mono flex items-center gap-2">
                       <span class="w-1 h-1 rounded-full bg-slate-500"></span>
                       {{ textInput.length }} Karakter Terdeteksi
                    </span>
                  </div>
                  <div v-if="textInput.length > 0 && textInput.length < 50" class="px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                    <span class="text-[10px] text-amber-500 font-black uppercase tracking-widest animate-pulse">
                      Min. 50 Karakter
                    </span>
                  </div>
                </div>
                
                <div class="flex items-stretch gap-4 w-full sm:w-auto">
                  <button 
                    @click="triggerFileUpload"
                    class="group/btn flex items-center justify-center gap-3 px-6 py-5 rounded-2xl bg-white/5 border border-white/5 hover:border-purple-500/30 transition-all active:scale-95 h-[64px] min-w-[200px]"
                  >
                    <svg class="w-5 h-5 text-slate-400 group-hover/btn:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    <span class="text-[10px] font-black uppercase tracking-widest text-slate-500 group-hover/btn:text-slate-200">UPLOAD DOC (.PDF / .DOCX)</span>
                  </button>
                  
                  <button
                    @click="handleScan"
                    :disabled="isScanning || textInput.length < 50"
                    class="group relative flex-1 sm:flex-none px-12 py-5 bg-white text-slate-950 font-black uppercase tracking-[0.2em] text-xs rounded-2xl shadow-[0_20px_40px_rgba(255,255,255,0.1)] transition-all hover:scale-105 hover:bg-slate-100 disabled:opacity-30 disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center justify-center gap-3 active:scale-95 overflow-hidden h-[64px]"
                  >
                    <div v-if="isScanning" class="w-5 h-5 border-3 border-slate-900/30 border-t-slate-900 rounded-full animate-spin"></div>
                    <span class="relative z-10">{{ isScanning ? 'Manganalisa...' : 'Verifikasi Teks' }}</span>
                    <svg v-if="!isScanning" class="w-5 h-5 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
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
                </div>
              </div>
              
              <div class="p-10 bg-slate-950/40 rounded-[2.5rem] border border-white/5 leading-[1.8] text-xl font-light text-slate-300 shadow-inner max-h-[500px] overflow-y-auto custom-scrollbar">
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

            <div v-else-if="scanResult" key="result" class="glass-card rounded-[3rem] p-10 space-y-10 relative overflow-hidden group border-purple-500/20 shadow-[0_30px_60px_-15px_rgba(0,0,0,0.7)]">
              <div :class="getScoreColor(scanResult.ai_probability)" class="absolute -right-20 -top-20 w-40 h-40 opacity-20 blur-[80px] rounded-full animate-pulse"></div>
              
              <div class="flex items-center justify-between">
                <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Detection Matrix</h3>
                <div :class="getScoreColor(scanResult.ai_probability)" class="text-[10px] font-black px-4 py-1.5 bg-white/5 rounded-full border border-white/10 backdrop-blur-md shadow-xl flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                  {{ scanResult.status.toUpperCase() }}
                </div>
              </div>
              
              <div class="flex flex-col items-center py-6 relative">
                <!-- Rotating Background Glow -->
                <div class="absolute inset-0 bg-gradient-to-tr from-purple-600/10 via-blue-600/10 to-fuchsia-600/10 blur-[100px] animate-pulse"></div>
                
                <div class="relative w-64 h-64 flex items-center justify-center group-hover:scale-110 transition-transform duration-1000">
                  <!-- Outer Ring Glow -->
                  <div :class="getScoreColor(scanResult.ai_probability)" class="absolute inset-0 rounded-full blur-[40px] opacity-20 group-hover:opacity-40 transition-opacity"></div>
                  
                  <div class="absolute inset-0 rounded-full border border-white/5 bg-slate-900/10 backdrop-blur-3xl shadow-[inset_0_0_60px_rgba(0,0,0,0.8)]"></div>
                  <svg class="w-full h-full transform -rotate-90 relative z-10 filter drop-shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                    <circle cx="128" cy="128" r="110" fill="none" stroke="currentColor" stroke-width="14" class="text-slate-900/40" />
                    <circle cx="128" cy="128" r="110" fill="none" stroke="currentColor" stroke-width="14" 
                      :stroke-dasharray="691" 
                      :stroke-dashoffset="691 - (691 * (scanResult.ai_probability) / 100)"
                      :class="getStrokeColor(scanResult.ai_probability)"
                      class="transition-all duration-[2500ms] cubic-bezier(0.4, 0, 0.2, 1)" 
                      stroke-linecap="round"
                    />
                  </svg>
                  <div class="absolute inset-0 flex flex-col items-center justify-center z-20">
                    <span class="text-7xl font-black transition-colors leading-none font-heading tracking-tighter drop-shadow-lg">{{ Math.round(scanResult.ai_probability) }}<span class="text-3xl text-slate-500">%</span></span>
                    <span class="text-[10px] text-content-muted uppercase tracking-[0.4em] mt-6 font-black scale-110">AI Signature</span>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-5">
                <div class="bg-slate-900/40 p-5 rounded-[2.2rem] border border-white/5 text-center shadow-lg group/metric hover:border-purple-500/20 transition-all hover:-translate-y-1 relative overflow-hidden">
                  <div class="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover/metric:opacity-100 transition-opacity"></div>
                  <div class="text-[9px] text-content-muted font-black uppercase tracking-widest mb-2 relative z-10 transition-colors group-hover/metric:text-purple-400">Word Density</div>
                  <div class="text-xl font-mono transition-colors font-bold tracking-tight relative z-10">{{ scanResult.perplexity?.toFixed(3) }}</div>
                  <div class="text-[8px] text-slate-600 uppercase mt-1 relative z-10">Complexity</div>
                </div>
                <div class="bg-slate-900/40 p-5 rounded-[2.2rem] border border-white/5 text-center shadow-lg group/metric hover:border-blue-500/20 transition-all hover:-translate-y-1 relative overflow-hidden">
                  <div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover/metric:opacity-100 transition-opacity"></div>
                  <div class="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-2 relative z-10 transition-colors group-hover/metric:text-blue-400">Structural Flex</div>
                  <div class="text-xl font-mono text-white font-bold tracking-tight relative z-10">{{ scanResult.burstiness?.toFixed(3) }}</div>
                  <div class="text-[8px] text-slate-600 uppercase mt-1 relative z-10">Variability</div>
                </div>
              </div>

              <div class="p-6 bg-slate-950/50 rounded-3xl border border-white/5 space-y-4">
                <h4 class="text-xs font-bold text-slate-400 flex items-center gap-2 italic uppercase tracking-wider">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  Analisis Singkat
                </h4>
                <p class="text-xs text-slate-400 leading-relaxed">
                  {{ scanResult.ai_probability > 70
                    ? 'Teks memiliki pola linguistik yang sangat teratur dan dapat diprediksi, ciri khas dari model bahasa AI.' 
                    : scanResult.ai_probability > 40 
                    ? 'Terdapat indikasi struktural yang mirip dengan teks buatan AI, namun dengan beberapa variasi manusia.' 
                    : 'Teks menunjukkan variasi struktur dan pola bahasa yang alami, khas dari tulisan tangan manusia.' 
                  }}
                </p>
              </div>

              <!-- Integrity Verdict (Unified with PDF) -->
              <div v-if="integrityVerdict" :class="[integrityVerdict.bg, integrityVerdict.border]" class="p-6 rounded-3xl border space-y-3 relative overflow-hidden group/verdict">
                <div class="absolute top-0 right-0 p-4 opacity-10 group-hover/verdict:scale-110 transition-transform">
                   <svg class="w-12 h-12" :class="integrityVerdict.color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path :d="integrityVerdict.icon" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                   </svg>
                </div>
                <h4 class="text-[10px] font-black uppercase tracking-[0.2em] opacity-70" :class="integrityVerdict.color">
                  Asesmen Integritas
                </h4>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-black tracking-tight" :class="integrityVerdict.color">{{ integrityVerdict.status }}</span>
                </div>
                <p class="text-[11px] text-slate-400 leading-relaxed font-medium pr-8">
                  {{ integrityVerdict.recommendation }}
                </p>
              </div>

              <!-- Composition Analysis (Polished) -->
              <div v-if="analysisSummary" class="p-8 bg-slate-950/60 rounded-[2.5rem] border border-white/10 space-y-6 shadow-2xl relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4 opacity-5">
                   <svg class="w-20 h-20" fill="currentColor" viewBox="0 0 24 24"><path d="M11 2v20c-5.07 0-9.22-3.8-9.88-8.74L1 13H11V2M13 2.05L13 11H22.05C21.43 6.01 17.5 2.25 12.63 2.02M13 13V22.05C17.99 21.43 21.75 17.5 21.98 12.63L13 13Z"/></svg>
                </div>
                <div class="flex items-center justify-between mb-2">
                  <h4 class="text-[10px] font-black text-slate-200 uppercase tracking-[0.2em]">Text Composition</h4>
                  <span class="text-[10px] text-slate-500 font-mono">{{ scanResult.sentences.length }} Sentences</span>
                </div>

                <div class="h-4 w-full bg-slate-800/50 rounded-full flex overflow-hidden border border-white/5 p-1 shadow-inner">
                  <div :style="{ width: analysisSummary.identical + '%' }" class="h-full bg-red-500 rounded-full transition-all duration-1000 hover:scale-y-110 shadow-[0_0_15px_rgba(239,68,68,0.5)]"></div>
                  <div :style="{ width: analysisSummary.paraphrased + '%' }" class="h-full bg-orange-500 rounded-full transition-all duration-1000 hover:scale-y-110 shadow-[0_0_15px_rgba(249,115,22,0.5)]"></div>
                  <div :style="{ width: analysisSummary.mixed + '%' }" class="h-full bg-amber-500 rounded-full transition-all duration-1000 hover:scale-y-110 shadow-[0_0_15px_rgba(245,158,11,0.5)]"></div>
                  <div :style="{ width: analysisSummary.human + '%' }" class="h-full bg-emerald-500 rounded-full transition-all duration-1000 hover:scale-y-110 shadow-[0_0_15px_rgba(16,185,129,0.5)]"></div>
                </div>

                <div class="grid grid-cols-2 gap-y-4 gap-x-6">
                  <div class="flex items-center gap-3">
                    <div class="w-1.5 h-1.5 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.6)]"></div>
                    <div class="flex flex-col">
                      <span class="text-[11px] font-black text-white px-1 leading-none">{{ analysisSummary.identical }}% AI Identic</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-1.5 h-1.5 bg-orange-500 rounded-full shadow-[0_0_8px_rgba(249,115,22,0.6)]"></div>
                    <div class="flex flex-col">
                      <span class="text-[11px] font-black text-white px-1 leading-none">{{ analysisSummary.paraphrased }}% Parafrasa</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-1.5 h-1.5 bg-amber-500 rounded-full shadow-[0_0_8px_rgba(245,158,11,0.6)]"></div>
                    <div class="flex flex-col">
                      <span class="text-[11px] font-black text-white px-1 leading-none">{{ analysisSummary.mixed }}% Campuran</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
                    <div class="flex flex-col">
                      <span class="text-[11px] font-black text-white px-1 leading-none">{{ analysisSummary.human }}% Manusia</span>
                    </div>
                  </div>
                </div>

                <!-- Report Action -->
                <div class="pt-6 border-t border-white/5 space-y-4">
                  <button 
                    @click="downloadReport"
                    class="w-full flex items-center justify-center gap-3 py-4.5 rounded-[1.5rem] bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-black text-xs uppercase tracking-[0.2em] transition-all transform active:scale-[0.97] group/report shadow-[0_15px_30px_-10px_rgba(79,70,229,0.4)] border border-white/20 focus:outline-none focus:ring-4 focus:ring-indigo-500/30 relative overflow-hidden"
                  >
                    <div class="absolute inset-0 bg-white/10 opacity-0 group-hover/report:opacity-100 transition-opacity"></div>
                    <svg class="w-4.5 h-4.5 group-hover:translate-y-0.5 transition-transform relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    <span class="relative z-10">Unduh Laporan PDF (.pdf)</span>
                  </button>
                  <p class="text-[9px] text-slate-500 text-center font-medium uppercase tracking-widest opacity-60">Laporan resmi SahihAksara &copy; 2025</p>
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
              <div v-for="item in scanHistory" :key="item.id" class="p-5 bg-slate-900/40 rounded-3xl border border-white/5 hover:border-purple-500/40 transition-all cursor-pointer group hover:bg-slate-900/60 shadow-lg relative overflow-hidden">
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

