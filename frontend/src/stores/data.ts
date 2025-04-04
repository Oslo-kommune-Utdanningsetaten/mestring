import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'
import type { AppData } from '../types/models'
import type { User } from '../types/models'

const defaultUser = {
  id: 'user-01',
  name: 'Maria Kemp',
  studentId: undefined,
  teacherId: 'teacher-02',
}

// function for updateting the current user
export function setCurrentUser(user: User) {
  dataStore.update(data => {
    return { ...data, currentUser: user }
  })
}

// Create a writable store with initial empty values
export const dataStore: Writable<AppData> = writable({
  students: [],
  groups: [],
  teachers: [],
  goals: [],
  observations: [],
  masteryLevels: [],
  currentUser: null,
})

// Function to load data from public/data.js
export async function loadData(): Promise<void> {
  try {
    // Dynamic import of the data.js file
    const module = await import('../../public/schoolData_v2.js')
    dataStore.set({
      ...module.data,
      currentUser: defaultUser,
    })
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

// Load data when this module is imported
loadData()
