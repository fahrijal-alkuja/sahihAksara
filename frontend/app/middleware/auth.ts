export default defineNuxtRouteMiddleware((to, from) => {
  const { token } = useAuth()
  
  // If not authenticated, redirect to login
  if (!token.value) {
    return navigateTo('/login')
  }
})
