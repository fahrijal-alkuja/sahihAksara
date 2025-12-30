import { defineNuxtConfig } from 'nuxt/config'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  future: {
    compatibilityVersion: 4,
  },
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'SahihAksara | Indonesian AI Forensic Analysis',
      meta: [
        { name: 'description', content: 'Deteksi forensik konten buatan AI dalam Bahasa Indonesia dengan akurasi tinggi dan laporan profesional.' }
      ],
      script: [
        { src: 'https://app.sandbox.midtrans.com/snap/snap.js', 'data-client-key': 'SB-Mid-client-YourClientKeyHere' } // Note: In production, this should be dynamic or env var
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&display=swap' }
      ]
    }
  }
})
