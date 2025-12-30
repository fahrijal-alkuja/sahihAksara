<template>
  <div class="min-h-screen bg-slate-950 font-sans text-slate-200 selection:bg-purple-500/30 selection:text-white">
    <main class="py-12 px-6">
      <div class="max-w-4xl mx-auto space-y-20">
        <!-- Hero Section -->
        <section class="text-center space-y-6">
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full text-purple-400 text-[10px] font-black uppercase tracking-[0.2em] animate-fade-in">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
            </span>
            Metodologi Deteksi
          </div>
          <h1 class="text-4xl md:text-6xl font-black text-white font-heading leading-tight tracking-tight">
            Bagaimana <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Kami Mendeteksi</span> AI?
          </h1>
          <p class="text-lg text-slate-400 font-light max-w-2xl mx-auto leading-relaxed">
            SahihAksara menggunakan model bahasa mutakhir dan analisis statistik tingkat lanjut untuk membedakan antara pola pikir manusia dan algoritma mesin.
          </p>
        </section>

        <!-- Process Grid -->
        <div class="grid md:grid-cols-2 gap-8">
          <!-- Step 1: IndoBERT MLM -->
          <div class="glass-card rounded-[3rem] p-10 space-y-6 border border-white/5 hover:border-purple-500/30 transition-all group">
            <div class="w-14 h-14 bg-purple-600/20 rounded-2xl flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.675.337a4 4 0 01-1.89.431H8a2 2 0 01-2-2V8a2 2 0 012-2h2.231a4 4 0 012.003.535l.983.54a2 2 0 00.999.27H18a2 2 0 012 2v6a2 2 0 01-1.022.547l-2.387-.477a6 6 0 00-3.86.517l-.675.337a4 4 0 01-1.89.431H8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <h3 class="text-2xl font-bold text-white font-heading">1. IndoBERT MLM Analysis</h3>
            <p class="text-slate-400 leading-relaxed font-light">
              Teks diproses menggunakan model <strong>IndoBERT</strong> (Masked Language Model). Kami mengukur seberapa "terkejut" model tersebut saat mencoba memprediksi setiap kata dalam kalimat Anda.
            </p>
          </div>

          <!-- Step 2: Complexity -->
          <div class="glass-card rounded-[3rem] p-10 space-y-6 border border-white/5 hover:border-blue-500/30 transition-all group">
            <div class="w-14 h-14 bg-blue-600/20 rounded-2xl flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <h3 class="text-2xl font-bold text-white font-heading">2. Complexity (Perplexity)</h3>
            <p class="text-slate-400 leading-relaxed font-light">
              AI biasanya menulis teks dengan tingkat prediktabilitas yang tinggi. Kami mendeteksi tulisan AI melalui skor <strong>Perplexity</strong> yang rendah, yang menunjukkan teks terlalu "sempurna" dan konsisten secara statistik.
            </p>
          </div>

          <!-- Step 3: Variability -->
          <div class="glass-card rounded-[3rem] p-10 space-y-6 border border-white/5 hover:border-amber-500/30 transition-all group">
            <div class="w-14 h-14 bg-amber-600/20 rounded-2xl flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <h3 class="text-2xl font-bold text-white font-heading">3. Variability (Burstiness)</h3>
            <p class="text-slate-400 leading-relaxed font-light">
              Manusia cenderung menulis dengan struktur yang bervariasi—kalimat panjang diikuti kalimat pendek. AI seringkali menghasilkan struktur yang monoton. Kami mengukur ini melalui <strong>Coefficient of Variation</strong>.
            </p>
          </div>

          <!-- Step 4: Hybrid Scoring -->
          <div class="glass-card rounded-[3rem] p-10 space-y-6 border border-white/5 hover:border-emerald-500/30 transition-all group">
            <div class="w-14 h-14 bg-emerald-600/20 rounded-2xl flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <h3 class="text-2xl font-bold text-white font-heading">4. Hybrid Decision Engine</h3>
            <p class="text-slate-400 leading-relaxed font-light">
              Semua sinyal di atas digabungkan menggunakan algoritma heuristik yang kami kalibrasi secara terus-menerus untuk meminimalkan *false positives* dan memberikan hasil seakurat mungkin.
            </p>
          </div>
        </div>

        <!-- Technical Deep Dive -->
        <section class="glass-card rounded-[4rem] p-12 md:p-20 relative overflow-hidden">
          <div class="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
            <svg class="w-64 h-64 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
          </div>
          <div class="max-w-2xl space-y-8 relative z-10">
            <h2 class="text-4xl font-black text-white font-heading leading-tight">Misi Integritas Akademik</h2>
            <div class="space-y-6 text-slate-400 font-light leading-relaxed text-lg">
              <p>
                SahihAksara bukanlah alat penghukum, melainkan instrumen transparansi. Kami percaya bahwa di era kecerdasan buatan, kemampuan manusia untuk berpikir kritis dan menyusun narasi unik harus tetap dihargai.
              </p>
              <p>
                Aplikasi ini dikembangkan sebagai bagian dari komitmen kami terhadap kualitas penulisan ilmiah di Indonesia, memastikan bahwa setiap karya adalah representasi murni dari pemikiran penulisnya.
              </p>
            </div>
            <NuxtLink to="/" class="inline-flex items-center gap-3 px-8 py-4 bg-white text-slate-950 rounded-2xl font-black uppercase tracking-widest hover:bg-slate-200 transition-all active:scale-95 shadow-2xl">
              Mulai Scanning
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 8l4 4m0 0l-4 4m4-4H3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </NuxtLink>
          </div>
        </section>
      </div>
    </main>

    <!-- Footer (Consistent) -->
    <footer class="border-t border-white/5 bg-slate-950/80 pt-16 pb-8">
      <div class="max-w-7xl mx-auto px-6 grid sm:grid-cols-2 gap-12 mb-16">
        <div class="space-y-6">
          <div class="flex items-center gap-4">
            <img src="/logo.png" alt="SahihAksara" class="w-8 h-8 rounded-lg bg-white p-1" />
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
      <div class="border-t border-white/5 pt-8 text-center px-6">
        <p class="text-[9px] text-slate-600 uppercase tracking-[0.4em] font-medium leading-loose">
          © 2025 SahihAksara. Dikembangkan untuk Integritas Akademik.
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.glass-card {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(20px);
}
</style>
