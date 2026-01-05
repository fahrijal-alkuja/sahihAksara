export const useAuth = () => {
  const config = useRuntimeConfig()
  const token = useCookie('auth_token', { maxAge: 60 * 60 * 24 }) // 1 day
  const user = useState<any>('user', () => null)
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const login = async (credentials: any) => {
    try {
      const formData = new FormData()
      formData.append('username', credentials.email)
      formData.append('password', credentials.password)

      const data = await $fetch<any>(`${config.public.apiUrl}/login`, {
        method: 'POST',
        body: formData
      })

      token.value = data.access_token
      await fetchMe()
      return data
    } catch (err: any) {
      console.error('Login failed:', err)
      throw err
    }
  }

  const register = async (userData: any) => {
    try {
      const data = await $fetch<any>(`${config.public.apiUrl}/register`, {
        method: 'POST',
        body: userData
      })
      return data
    } catch (err: any) {
      console.error('Registration failed:', err)
      throw err
    }
  }

  const fetchMe = async () => {
    if (!token.value) return
    try {
      const data = await $fetch<any>(`${config.public.apiUrl}/me`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      user.value = data
    } catch (err) {
      console.error('Failed to fetch user:', err)
      logout()
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    navigateTo('/login')
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchMe,
    logout,
    initiateUpgrade: () => {
      navigateTo('/pricing')
    }
  }
}
