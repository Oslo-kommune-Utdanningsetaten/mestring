import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'
import type { AppData } from '../types/models'

// Create a writable store with initial empty values
export const dataStore: Writable<AppData> = writable({
  students: [],
  groups: [],
  teachers: [],
  goals: [],
  observations: [],
  masteryLevels: [],
  subjects: [],
})

// Function to load data from public/data.js
export async function loadData(): Promise<void> {
  try {
    // Dynamic import of the data.js file
    const module = await import('../../public/data.js')
    dataStore.set(module.data)
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

// Load data when this module is imported
loadData()
