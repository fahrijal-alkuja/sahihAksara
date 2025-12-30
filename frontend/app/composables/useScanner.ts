export const useScanner = () => {
  const { token, logout } = useAuth()
  const { showModal, error, notify } = useNotify()
  const scanResult = useState<any>('scanResult', () => null)
  const isScanning = useState<boolean>('isScanning', () => false)
  const scanHistory = useState<any[]>('scanHistory', () => [])

  const scanText = async (text: string) => {
    if (!text.trim()) return
    if (!token.value) {
      alert('Silakan login terlebih dahulu untuk melakukan scan.')
      return navigateTo('/login')
    }
    
    isScanning.value = true
    try {
      const data = await $fetch<any>('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token.value}` },
        body: { text_content: text }
      })
      
      scanResult.value = data
      fetchHistory() // Refresh history from server
    } catch (err: any) {
      console.error('Scan failed:', err)
      if (err.status === 401) logout()
      const msg = err.data?.detail || 'Gagal melakukan pemindaian.'
      
      if (err.status === 403) {
        showModal(msg, 'warning', 'Upgrade ke Pro Sekarang', '/pricing')
      } else {
        error(msg)
      }
    } finally {
      isScanning.value = false
    }
  }

  const uploadFile = async (file: File) => {
    if (!token.value) return navigateTo('/login')
    
    isScanning.value = true
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const data = await $fetch<any>('http://localhost:8000/analyze-file', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token.value}` },
        body: formData
      })
      
      scanResult.value = data
      fetchHistory()
      return data
    } catch (err: any) {
      console.error('File upload failed:', err)
      if (err.status === 401) logout()
      const msg = err.data?.detail || 'Gagal memproses berkas.'
      
      if (err.status === 403) {
        showModal(msg, 'warning', 'Upgrade ke Pro Sekarang', '/pricing')
      } else {
        error(msg)
      }
    } finally {
      isScanning.value = false
    }
  }

  const fetchHistory = async () => {
    if (!token.value) return
    try {
      const data = await $fetch<any[]>('http://localhost:8000/history', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      if (data) {
        scanHistory.value = data
      }
    } catch (err) {
      console.error('Failed to fetch history:', err)
      if ((err as any).status === 401) logout()
    }
  }

  const clearHistory = async () => {
    if (!token.value) return
    try {
      await $fetch('http://localhost:8000/history', {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token.value}` }
      })
      scanHistory.value = []
      notify('Seluruh riwayat scan berhasil dihapus secara permanen.')
    } catch (err) {
      console.error('Failed to clear history:', err)
      error('Gagal menghapus riwayat.')
    }
  }

  return {
    scanResult,
    isScanning,
    scanHistory,
    scanText,
    uploadFile,
    fetchHistory,
    clearHistory
  }
}
