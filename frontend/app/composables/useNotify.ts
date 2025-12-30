export type NotifyType = 'success' | 'error' | 'warning' | 'info'

interface Notification {
  id: string
  message: string
  type: NotifyType
  duration?: number
  isModal?: boolean
  actionLabel?: string
  actionRoute?: string
}

export const useNotify = () => {
  const notifications = useState<Notification[]>('notifications', () => [])

  const notify = (message: string, type: NotifyType = 'info', duration = 5000) => {
    const id = Math.random().toString(36).substring(2, 9)
    notifications.value.push({ id, message, type, duration })

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }
  }

  const showModal = (message: string, type: NotifyType = 'info', actionLabel?: string, actionRoute?: string) => {
    const id = Math.random().toString(36).substring(2, 9)
    notifications.value.push({ 
      id, 
      message, 
      type, 
      isModal: true,
      actionLabel,
      actionRoute
    })
  }

  const remove = (id: string) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return {
    notifications,
    notify,
    showModal,
    remove,
    success: (msg: string) => notify(msg, 'success'),
    error: (msg: string) => notify(msg, 'error'),
    warning: (msg: string) => notify(msg, 'warning'),
    info: (msg: string) => notify(msg, 'info'),
  }
}
