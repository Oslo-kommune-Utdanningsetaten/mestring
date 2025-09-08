import { writable } from 'svelte/store'
import { setCurrentUser } from './data'

export const isLoggingInUser = writable<boolean>(true)

export const checkAuth = async (): Promise<void> => {
  isLoggingInUser.set(true)
  try {
    const response = await fetch('/auth/status', { credentials: 'include' })
    const data = response.ok ? await response.json() : null
    setCurrentUser(data?.isAuthenticated ? data.user : null)
  } catch (error) {
    console.error('Error checking auth status:', error)
    setCurrentUser(null)
  } finally {
    isLoggingInUser.set(false)
  }
}

export const login = (): void => {
  window.location.href = '/auth/feidelogin/'
}

export const logout = (): void => {
  setCurrentUser(null)
  window.location.href = '/auth/logout/'
}
