import { writable } from 'svelte/store'

// Create a store to track current navigation state
export const currentPath = writable(window.location.pathname)

// Initialize by listening to navigation events
if (typeof window !== 'undefined') {
  // Handle browser back/forward navigation
  window.addEventListener('popstate', () => {
    currentPath.set(window.location.pathname)
  })
}
