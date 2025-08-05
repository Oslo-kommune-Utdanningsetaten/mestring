import { writable } from 'svelte/store'

export interface AuthUser {
  id: number | null 
  name: string
  email: string
  feide_id: string
}

export const loggedIn = writable<boolean>(false)
export const currentUser = writable<AuthUser | null>(null)
export const isLoading = writable<boolean>(true)

export const refreshAuth = async (): Promise<void> => {
  isLoading.set(true)
  try {
    const response = await fetch('/api/auth/status', { credentials: 'include' })
    const data = response.ok ? await response.json() : null

    if (data?.authenticated) {
      loggedIn.set(true)
      currentUser.set(data.user)
    } else {
      loggedIn.set(false)
      currentUser.set(null)
    }
  } catch (error) {
    console.error('Error checking auth status:', error)
    loggedIn.set(false)
    currentUser.set(null)
  } finally {
    isLoading.set(false)
  }
}

export const login = (): void => {
  window.location.href = '/auth/feidelogin/'
}

export const logout = (): void => {
  loggedIn.set(false)
  currentUser.set(null)
  
  window.location.href = '/auth/logout/'
}

refreshAuth()