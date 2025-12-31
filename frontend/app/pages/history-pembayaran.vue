<script setup lang="ts">
const { user, fetchMe, token } = useAuth()

interface Transaction {
    id: number;
    order_id: string;
    amount: number;
    plan_type: string;
    status: string;
    snap_token?: string;
    created_at: string;
}

const transactions = ref<Transaction[]>([])
const loading = ref(true)

const { notify, warning, error: notifyError } = useNotify()

declare global {
  interface Window {
    snap: any
  }
}

const reopenSnap = (token: string) => {
    if (typeof window.snap !== 'undefined') {
        window.snap.pay(token, {
            onSuccess: function(result: any) {
                notify('Pembayaran berhasil! Akun Anda telah diupgrade.', 'success')
                fetchPaymentHistory()
                fetchMe()
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
    } else {
        notifyError('Snap Midtrans tidak bermuatan. Silakan muat ulang halaman.')
    }
}

const fetchPaymentHistory = async () => {
    try {
        const response = await fetch('http://localhost:8000/payments/history', {
            headers: {
                'Authorization': `Bearer ${token.value}`
            }
        })
        if (response.ok) {
            transactions.value = await response.json()
        }
    } catch (error) {
        console.error('Failed to fetch payment history:', error)
    } finally {
        loading.value = false
    }
}


onMounted(async () => {
    await fetchMe()
    await fetchPaymentHistory()
})

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('id-ID', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount)
}

const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
        case 'settlement':
            return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
        case 'pending':
            return 'text-amber-400 bg-amber-400/10 border-amber-400/20'
        case 'expire':
        case 'deny':
        case 'cancel':
            return 'text-red-400 bg-red-400/10 border-red-400/20'
        default:
            return 'text-slate-400 bg-slate-400/10 border-slate-400/20'
    }
}

definePageMeta({
    layout: 'default',
    middleware: ['auth']
})
</script>

<template>
    <div class="max-w-7xl mx-auto px-6 py-12 space-y-12 relative z-10">
        <!-- Header -->
        <div class="glass-panel p-10 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden group">
            <div class="absolute -top-24 -right-24 w-64 h-64 bg-purple-600/10 blur-[100px] rounded-full group-hover:bg-purple-600/20 transition-all duration-1000"></div>
            
            <div class="flex items-center gap-6 relative z-10">
                <NuxtLink to="/dashboard" class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white hover:bg-white/10 transition-all active:scale-95">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </NuxtLink>
                <div>
                    <h1 class="text-3xl font-black font-heading tracking-tight mb-1">History Pembayaran</h1>
                    <p class="text-content-muted font-medium tracking-wide">Lihat semua riwayat transaksi Anda di sini.</p>
                </div>
            </div>
            
            <div class="relative z-10">
                <span class="text-[10px] font-black text-content-muted px-4 py-2 bg-white/5 rounded-full border border-white/5 uppercase tracking-[0.2em]">
                    {{ transactions.length }} Transaksi Terdaftar
                </span>
            </div>
        </div>

        <!-- History Table -->
        <div class="glass-panel overflow-hidden border-purple-500/10">
            <div v-if="loading" class="p-20 text-center">
                <div class="inline-block w-8 h-8 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mb-4"></div>
                <p class="text-content-muted font-bold uppercase tracking-widest text-xs">Memuat Data Transaksi...</p>
            </div>
            
            <div v-else-if="transactions.length === 0" class="p-20 text-center space-y-4 flex flex-col items-center">
                <div class="w-20 h-20 rounded-full bg-white/5 border border-white/5 flex items-center justify-center text-slate-700 mb-4 blur-[0.5px]">
                    <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </div>
                <h3 class="text-lg font-bold text-content-muted">Belum Ada Transaksi</h3>
                <p class="text-sm text-content-muted max-w-xs font-medium text-center">Anda belum pernah melakukan pembayaran. Silakan upgrade ke Pro untuk mendapatkan fitur lengkap.</p>
                <NuxtLink to="/pricing" class="mt-4 px-8 py-3 bg-purple-600 hover:bg-purple-50 text-white hover:text-purple-600 font-black text-[10px] uppercase tracking-widest rounded-xl transition-all active:scale-95 border border-purple-500/30">
                    Upgrade ke Pro Sekarang
                </NuxtLink>
            </div>

            <div v-else class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead>
                        <tr class="bg-white/5 text-content-muted text-[10px] font-black uppercase tracking-[0.3em] border-b border-white/5">
                            <th class="px-10 py-6">Order ID</th>
                            <th class="px-10 py-6">Paket</th>
                            <th class="px-10 py-6">Jumlah</th>
                            <th class="px-10 py-6 text-center">Status</th>
                            <th class="px-10 py-6 text-right">Tanggal</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-white/5">
                        <tr v-for="tx in transactions" :key="tx.id" class="hover:bg-white/[0.03] transition-all duration-300 group">
                            <td class="px-10 py-8 align-middle">
                                <div class="flex flex-col gap-1">
                                    <span class="text-sm font-bold text-white font-mono group-hover:text-purple-400 transition-colors uppercase">{{ tx.order_id }}</span>
                                    <span class="text-[9px] text-content-muted font-black uppercase tracking-widest">Transaction #{{ tx.id }}</span>
                                </div>
                            </td>
                            <td class="px-10 py-8 align-middle">
                                <span class="text-xs font-bold text-white uppercase tracking-wider">{{ tx.plan_type === 'monthly' ? 'Bulanan' : 'Harian' }}</span>
                            </td>
                            <td class="px-10 py-8 align-middle">
                                <span class="text-sm font-black text-white font-heading">{{ formatAmount(tx.amount) }}</span>
                            </td>
                            <td class="px-10 py-8 align-middle text-center">
                                <div class="flex flex-col items-center gap-2">
                                    <span :class="['px-5 py-2 rounded-xl text-[9px] font-black uppercase tracking-[0.15em] border backdrop-blur-md inline-block min-w-[120px]', getStatusColor(tx.status)]">
                                        {{ tx.status }}
                                    </span>
                                    <button 
                                        v-if="tx.status.toLowerCase() === 'pending' && tx.snap_token"
                                        @click="reopenSnap(tx.snap_token)"
                                        class="flex items-center gap-1.5 text-[8px] font-black uppercase tracking-widest text-emerald-400 hover:text-white transition-colors"
                                    >
                                        <svg class="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                                        Bayar Sekarang
                                    </button>
                                </div>
                            </td>
                            <td class="px-10 py-8 align-middle text-right">
                                <span class="text-xs font-bold text-content-muted font-mono">{{ formatDate(tx.created_at) }}</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
