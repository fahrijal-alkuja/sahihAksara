<template>
  <div class="flex flex-col items-center py-10 space-y-12">
    <!-- Circular Scanner Animation -->
    <div class="relative w-48 h-48">
      <div class="absolute inset-0 rounded-full border-4 border-slate-800/50"></div>
      <div class="absolute inset-0 rounded-full border-4 border-t-purple-500 border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
      <div class="absolute inset-4 rounded-full border-2 border-slate-800/30 animate-pulse"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <div class="w-12 h-1 bg-purple-500/50 rounded-full animate-bounce mb-2"></div>
        <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Analyzing</div>
      </div>
    </div>

    <!-- Shimmering Text Feedback -->
    <div class="w-full space-y-6">
      <div class="flex justify-between items-center">
        <div class="h-2 bg-slate-800 rounded-full w-24 animate-pulse"></div>
        <div class="h-2 bg-slate-800 rounded-full w-12 animate-pulse"></div>
      </div>
      <div class="space-y-3">
        <div class="h-3 bg-gradient-to-r from-slate-800 to-slate-900 rounded-lg w-full shimmer"></div>
        <div class="h-3 bg-gradient-to-r from-slate-800 to-slate-900 rounded-lg w-[90%] shimmer" style="animation-delay: 0.1s"></div>
        <div class="h-3 bg-gradient-to-r from-slate-800 to-slate-900 rounded-lg w-[75%] shimmer" style="animation-delay: 0.2s"></div>
      </div>
    </div>

    <!-- Metrics Placeholder -->
    <div class="grid grid-cols-2 gap-4 w-full pt-4">
      <div class="h-24 bg-slate-900/50 rounded-[2rem] border border-white/5 animate-pulse flex flex-col items-center justify-center gap-2">
        <div class="h-1.5 bg-slate-800 rounded-full w-12"></div>
        <div class="h-4 bg-slate-800 rounded-lg w-20"></div>
      </div>
      <div class="h-24 bg-slate-900/50 rounded-[2rem] border border-white/5 animate-pulse flex flex-col items-center justify-center gap-2">
        <div class="h-1.5 bg-slate-800 rounded-full w-12"></div>
        <div class="h-4 bg-slate-800 rounded-lg w-20"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shimmer {
  background-size: 200% 100%;
  animation: loading-shimmer 2s infinite;
}

@keyframes loading-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
