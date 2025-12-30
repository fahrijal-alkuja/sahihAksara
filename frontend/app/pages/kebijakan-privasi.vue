<template>
  <div class="min-h-screen bg-slate-950 font-sans text-slate-200 selection:bg-purple-500/30 selection:text-white">
    <main class="py-12 px-6">
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

          <div class="glass-card rounded-[2.5rem] p-10 border border-purple-500/20 bg-gradient-to-br from-purple-500/5 to-transparent relative overflow-hidden group">
            <div class="absolute -right-12 -top-12 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl group-hover:bg-purple-500/20 transition-all"></div>
            
            <h2 class="text-2xl font-black text-white font-heading flex items-center gap-4 mb-6">
              <div class="w-12 h-12 bg-purple-500/20 rounded-2xl flex items-center justify-center text-purple-400">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </div>
              Zero-Retention Policy
            </h2>
            
            <div class="grid md:grid-cols-2 gap-8">
              <div class="space-y-4">
                <h3 class="text-sm font-black text-purple-400 uppercase tracking-widest">Proteksi Konten</h3>
                <ul class="space-y-3">
                  <li class="flex items-start gap-3 text-sm text-slate-400 font-light">
                    <span class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 shrink-0"></span>
                    <span><strong>Immediate Purge:</strong> Isi teks Anda langsung dipotong dan diganti label proteksi di database segera setelah analisa selesai.</span>
                  </li>
                  <li class="flex items-start gap-3 text-sm text-slate-400 font-light">
                    <span class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 shrink-0"></span>
                    <span><strong>1-Hour Heatmap:</strong> Detail lokasi AI (heatmap) hanya disimpan selama 60 menit untuk kebutuhan unduh laporan, lalu dihapus total.</span>
                  </li>
                </ul>
              </div>
              <div class="space-y-4">
                <h3 class="text-sm font-black text-blue-400 uppercase tracking-widest">Proteksi Sesi</h3>
                <ul class="space-y-3">
                  <li class="flex items-start gap-3 text-sm text-slate-400 font-light">
                    <span class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 shrink-0"></span>
                    <span><strong>IP Anonymization:</strong> Alamat IP dalam log server disamarkan otomatis untuk mencegah pelacakan identitas.</span>
                  </li>
                  <li class="flex items-start gap-3 text-sm text-slate-400 font-light">
                    <span class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 shrink-0"></span>
                    <span><strong>Auto-Expiry:</strong> Seluruh riwayat metadata yang tersisa akan dihapus permanen secara otomatis setelah 7 hari.</span>
                  </li>
                </ul>
              </div>
            </div>
            
            <div class="mt-8 pt-8 border-t border-white/5">
              <p class="text-[11px] text-slate-500 font-medium italic leading-relaxed">
                "Kami membangun SahihAksara dengan filosofi bahwa data Anda adalah milik Anda. Privasi bukanlah fitur opsional, melainkan pondasi dari sistem kami."
              </p>
            </div>
          </div>

          <div class="space-y-6">
            <h2 class="text-xl font-bold text-white font-heading flex items-center gap-3 px-2">
              <span class="w-1.5 h-6 bg-emerald-500 rounded-full"></span>
              Penggunaan Data
            </h2>
            <p class="text-slate-400 leading-relaxed font-light px-2">
              Data statistik anonim (seperti persentase AI tanpa teks asli) dapat digunakan untuk meningkatkan akurasi model deteksi IndoBERT kami. Data ini tidak akan pernah dikaitkan dengan identitas pribadi Anda.
            </p>
          </div>

          <div class="space-y-6">
            <h2 class="text-xl font-bold text-white font-heading flex items-center gap-3 px-2">
              <span class="w-1.5 h-6 bg-amber-500 rounded-full"></span>
              Hak Kekayaan Intelektual
            </h2>
            <p class="text-slate-400 leading-relaxed font-light px-2">
              Teks yang Anda kirimkan tetap menjadi milik Anda sepenuhnya. SahihAksara tidak mengklaim hak kepemilikan apa pun atas konten yang dianalisis melalui lingkungan kami.
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
</script>

<style scoped>
.glass-card {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(20px);
}
</style>
