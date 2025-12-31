<script setup lang="ts">
defineProps<{
    show: boolean;
    type: 'warning' | 'error';
    message: string;
}>()
</script>

<template>
    <Transition
        enter-active-class="transition duration-500 ease-out"
        enter-from-class="opacity-0 -translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-4"
    >
        <div v-if="show" class="relative z-50 mb-8">
            <div :class="[
                'glass-panel p-6 border flex items-center gap-6 overflow-hidden relative group',
                type === 'warning' ? 'border-amber-500/30 bg-amber-500/5' : 'border-red-500/30 bg-red-500/5'
            ]">
                <!-- Ambient Glow -->
                <div :class="[
                    'absolute -top-12 -right-12 w-32 h-32 blur-[60px] rounded-full opacity-20 transition-all duration-1000 group-hover:opacity-40',
                    type === 'warning' ? 'bg-amber-500' : 'bg-red-500'
                ]"></div>

                <div :class="[
                    'w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0 border relative z-10',
                    type === 'warning' ? 'bg-amber-500/10 border-amber-500/20 text-amber-500' : 'bg-red-500/10 border-red-500/20 text-red-500'
                ]">
                    <span v-if="type === 'warning'">⚠️</span>
                    <span v-else>🚫</span>
                </div>

                <div class="space-y-1 relative z-10 flex-1">
                    <h4 :class="[
                        'text-[10px] font-black uppercase tracking-[0.3em]',
                        type === 'warning' ? 'text-amber-500' : 'text-red-500'
                    ]">
                        Sistem Gateway Notice
                    </h4>
                    <p class="text-white text-sm font-bold tracking-tight">
                        {{ message }}
                    </p>
                </div>

                <div class="hidden sm:block relative z-10">
                    <span :class="[
                        'px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest border',
                        type === 'warning' ? 'bg-amber-500/10 border-amber-500/20 text-amber-500' : 'bg-red-500/10 border-red-500/20 text-red-500'
                    ]">
                        Maintenance
                    </span>
                </div>
            </div>
        </div>
    </Transition>
</template>
