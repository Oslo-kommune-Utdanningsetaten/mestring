import { writable } from 'svelte/store'
import type { UserReadable } from '../generated/types.gen'

export const currentUser = writable<UserReadable | null>(null)
export const isLoggingInUser = writable<boolean>(true)

export const checkAuth = async (): Promise<void> => {
  isLoggingInUser.set(true)
  try {
    const response = await fetch('/auth/status', { credentials: 'include' })
    const data = response.ok ? await response.json() : null
    if (data?.isAuthenticated) {
      currentUser.set(data.user)
    } else {
      currentUser.set(null)
    }
  } catch (error) {
    console.error('Error checking auth status:', error)
    currentUser.set(null)
  } finally {
    isLoggingInUser.set(false)
  }
}

export const login = (): void => {
  window.location.href = '/auth/feidelogin/'
}

export const logout = (): void => {
  currentUser.set(null)
  window.location.href = '/auth/logout/'
}
