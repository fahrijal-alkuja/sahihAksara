<template>
  <div class="min-h-screen bg-slate-950 font-sans text-slate-200 selection:bg-purple-500/30 selection:text-white">
    <!-- Navbar (Consistent) -->
    <nav class="fixed top-0 w-full z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
      <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-4 group transition-transform hover:scale-105 active:scale-95">
          <img src="/logo.png" alt="SahihAksara" class="w-10 h-10 rounded-xl bg-white p-1 border border-white/10 shadow-lg" />
          <span class="text-xl font-bold tracking-tight text-white font-heading">SahihAksara</span>
        </NuxtLink>
        <div class="hidden md:flex items-center gap-10">
          <NuxtLink to="/" class="text-[11px] font-black text-slate-400 hover:text-white transition-all uppercase tracking-[0.2em]">Beranda</NuxtLink>
          <NuxtLink to="/" class="text-[11px] font-black text-slate-400 hover:text-white transition-all uppercase tracking-[0.2em]">Analisis Teks</NuxtLink>
          <NuxtLink to="/cara-kerja" class="text-[11px] font-black text-slate-400 hover:text-white transition-all uppercase tracking-[0.2em]">Cara Kerja</NuxtLink>
        </div>
        <NuxtLink to="/" class="px-6 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-[11px] font-black uppercase tracking-widest text-white hover:bg-slate-800 transition-all active:scale-95 shadow-lg">
          Mulai Gratis
        </NuxtLink>
      </div>
    </nav>

    <main class="pt-32 pb-24 px-6">
      <div class="max-w-3xl mx-auto space-y-16">
        <section class="space-y-4">
          <h1 class="text-3xl md:text-4xl font-black text-white font-heading tracking-tight">Kebijakan Privasi</h1>
          <p class="text-slate-500 font-mono text-[10px] uppercase tracking-widest">Terakhir diperbarui: 30 Desember 2025</p>
        </section>

        <section class="prose prose-invert max-w-none space-y-10">
          <div class="glass-card rounded-3xl p-8 border border-white/5 space-y-4">
            <h2 class="text-xl font-bold text-white font-heading flex items-center gap-3">
              <span class="w-1.5 h-6 bg-purple-500 rounded-full"></span>
              Pengenalan
            </h2>
            <p class="text-slate-400 leading-relaxed font-light">
              SahihAksara berkomitmen untuk melindungi privasi Anda. Kebijakan Privasi ini menjelaskan bagaimana kami mengelola data Anda saat menggunakan layanan deteksi AI kami. Aplikasi ini dikembangkan oleh <strong>Universitas Kutai Kartanegara, TIM IT fahrijal</strong> sebagai wujud dedikasi terhadap integritas akademik.
            </p>
          </div>

          <div class="space-y-6">
            <h2 class="text-xl font-bold text-white font-heading flex items-center gap-3 px-2">
              <span class="w-1.5 h-6 bg-blue-500 rounded-full"></span>
              Data Terenkripsi
            </h2>
            <p class="text-slate-400 leading-relaxed font-light px-2">
              Kami memahami sensitivitas teks yang Anda analisis. Semua teks yang dikirimkan untuk pemindaian diproses secara aman. Kami tidak menyimpan teks Anda secara permanen setelah analisis selesai, kecuali jika Anda secara eksplisit menyimpannya dalam riwayat sesi lokal Anda.
            </p>
          </div>

          <div class="space-y-6">
            <h2 class="text-xl font-bold text-white font-heading flex items-center gap-3 px-2">
              <span class="w-1.5 h-6 bg-emerald-500 rounded-full"></span>
              Penggunaan Data
            </h2>
            <p class="text-slate-400 leading-relaxed font-light px-2">
              Data statistik anonim dapat digunakan untuk meningkatkan akurasi model deteksi IndoBERT kami. Data ini tidak akan pernah dikaitkan dengan identitas pribadi Anda.
            </p>
          </div>

          <div class="space-y-6">
            <h2 class="text-xl font-bold text-white font-heading flex items-center gap-3 px-2">
              <span class="w-1.5 h-6 bg-amber-500 rounded-full"></span>
              Hak Kekayaan Intelektual
            </h2>
            <p class="text-slate-400 leading-relaxed font-light px-2">
              Teks yang Anda kirimkan tetap menjadi milik Anda sepenuhnya. SahihAksara tidak mengklaim hak kepemilikan apa pun atas konten yang dianalisis melalui platform kami.
            </p>
          </div>

          <div class="p-8 bg-slate-900/50 rounded-3xl border border-white/5 space-y-4">
            <h2 class="text-xl font-bold text-white font-heading">Tim Pengembang</h2>
            <p class="text-slate-400 leading-relaxed font-light italic">
              "Inovasi untuk kejujuran akademik di Indonesia."
            </p>
            <div class="flex flex-col gap-2 pt-2">
              <span class="text-sm font-bold text-white">Universitas Kutai Kartanegara (UNIKARTA)</span>
              <span class="text-sm text-slate-300">TIM IT: Fahrijal & Team</span>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Footer (Consistent) -->
    <footer class="border-t border-white/5 bg-slate-950/80 pt-16 pb-8">
      <div class="max-w-7xl mx-auto px-6 h-full">
        <div class="flex flex-col md:flex-row justify-between gap-12 mb-16">
          <div class="space-y-6">
            <div class="flex items-center gap-4">
              <img src="/logo.png" alt="SahihAksara" class="w-8 h-8 rounded-lg bg-white p-1" />
              <span class="text-xl font-bold text-white font-heading">SahihAksara</span>
            </div>
            <p class="text-sm text-slate-500 max-w-xs leading-relaxed font-light">
              Membangun ekosistem akademik yang jujur melalui teknologi verifikasi teks mutakhir.
            </p>
          </div>
          <div class="flex gap-16">
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
        <div class="border-t border-white/5 pt-8 text-center">
          <p class="text-[9px] text-slate-600 uppercase tracking-[0.4em] font-medium leading-loose text-center">
            © 2025 SahihAksara. Dikembangkan untuk Integritas Akademik UNIKARTA.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
definePageMeta({
  layout: false
})
</script>

<style scoped>
.glass-card {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(20px);
}
</style>
