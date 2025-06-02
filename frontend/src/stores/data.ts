import { get, writable } from 'svelte/store'
import type { Writable as WritableType } from 'svelte/store'
import { subjectsList } from '../api/sdk.gen'
import type { SubjectReadable, SchoolReadable, BasicUserReadable } from '../api/types.gen'
import { getLocalStorageItem, setLocalStorageItem } from '../stores/localStorage'

type AppData = {
  subjects: SubjectReadable[]
  currentSchool: SchoolReadable | null
  currentUser: BasicUserReadable | null
}

const defaultUser = {
  id: 'user-01',
  name: 'Maria Kemp',
  studentId: undefined,
  teacherId: 'teacher-02',
}

// function for updating the current user
export function setCurrentUser(user: BasicUserReadable) {
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

  // Load subjects for this school
  if (school?.id) {
    loadSubjectsForSchool(school.id)
  }
}

// Create a writable store with initial empty values
export const dataStore: WritableType<AppData> = writable({
  subjects: [],
  currentSchool: null,
  currentUser: null,
})

async function loadSubjectsForSchool(schoolId: string): Promise<void> {
  try {
    const result = await subjectsList({
      query: {
        maintenedBySchool: schoolId,
      },
    })

    const subjects = result.data || []

    dataStore.update(data => {
      return { ...data, subjects }
    })
  } catch (error) {
    console.error('Failed to load subjects for school:', error)
    dataStore.update(data => {
      return { ...data, subjects: [] }
    })
  }
}

export async function loadData(): Promise<void> {
  try {
    const currentSchool = getLocalStorageItem('currentSchool')

    dataStore.set({
      currentSchool,
      currentUser: defaultUser,
      subjects: [],
    })

    // Load subjects if we have a current school
    if (currentSchool?.id) {
      await loadSubjectsForSchool(currentSchool.id)
    }
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

// Load data when this module is imported
loadData()
