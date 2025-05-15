import { get, writable } from 'svelte/store'
import type { Writable as WritableType } from 'svelte/store'
import type { AppData, User } from '../types/models'
import { type SchoolReadable } from '../api/types.gen'
import { getLocalStorageItem, setLocalStorageItem } from '../stores/localStorage'
import { set } from 'date-fns'

const defaultUser = {
  id: 'user-01',
  name: 'Maria Kemp',
  studentId: undefined,
  teacherId: 'teacher-02',
}

// function for updating the current user
export function setCurrentUser(user: User) {
  dataStore.update(data => {
    return { ...data, currentUser: user }
  })
}

// function for updating the current user
export function setCurrentSchool(school: SchoolReadable) {
  setLocalStorageItem('currentSchool', school)
  dataStore.update(data => {
    return { ...data, currentSchool: school }
  })
}

// Create a writable store with initial empty values
export const dataStore: WritableType<AppData> = writable({
  students: [],
  groups: [],
  teachers: [],
  goals: [],
  observations: [],
  masteryLevels: [],
  currentSchool: null,
  currentUser: null,
})

// Function to load data from public/data.js
export async function loadData(): Promise<void> {
  try {
    // Dynamic import of the data.js file
    const module = await import('../../public/schoolData_v2.js')
    dataStore.set({
      ...module.data,
      currentSchool: getLocalStorageItem('currentSchool'),
      currentUser: defaultUser,
    })
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

// Load data when this module is imported
loadData()
