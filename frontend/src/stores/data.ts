import { get, writable } from 'svelte/store'
import type { Writable as WritableType } from 'svelte/store'
import { subjectsList, schoolsList, masterySchemasList, usersRetrieve } from '../generated/sdk.gen'
import type { SchoolReadable, MasterySchemaReadable, UserReadable } from '../generated/types.gen'
import { getLocalStorageItem, setLocalStorageItem } from '../stores/localStorage'
import type { AppData } from '../types/models'
import { currentUser as authUser } from './auth'

const loadUser = async () => {
  try {
    const authUserData = get(authUser)

    if (!authUserData) {
      console.info('No user')
      return
    }
    setCurrentUser(authUserData)
  } catch (error) {
    console.error('Error loading user:', error)
  }
}

export const setCurrentUser = (user: UserReadable) => {
  dataStore.update(data => {
    return { ...data, currentUser: user }
  })
}

export const setCurrentSchool = (school: SchoolReadable) => {
  setLocalStorageItem('currentSchool', school)
  dataStore.update(data => {
    return { ...data, currentSchool: school }
  })
  if (school?.id) {
    loadSubjectsForSchool(school.id)
  }
}

const setMasterySchemas = (schemas: MasterySchemaReadable[]) => {
  dataStore.update(data => {
    return { ...data, masterySchemas: schemas }
  })
}

// Create a writable store with initial empty values
export const dataStore: WritableType<AppData> = writable({
  subjects: [],
  currentSchool: null,
  currentUser: null,
  masterySchemas: [],
})

const loadDefaultSchool = async () => {
  try {
    const result = await schoolsList()
    const schools = result.data || []
    const defaultSchool = schools.find(school => school.isServiceEnabled) || null
    if (defaultSchool) {
      setCurrentSchool(defaultSchool)
    }
  } catch (error) {
    console.error('Error fetching schools:', error)
    return null
  }
}

const loadMasterySchemas = async () => {
  try {
    const result = await masterySchemasList()
    const schemas = result.data || []
    setMasterySchemas(schemas)
  } catch (error) {
    console.error('Error fetching mastery schemas:', error)
    return null
  }
}

const loadSubjectsForSchool = async (schoolId: string): Promise<void> => {
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

export const loadData = async () => {
  try {
    const currentSchool: SchoolReadable | null = getLocalStorageItem(
      'currentSchool'
    ) as SchoolReadable | null

    dataStore.set({
      currentSchool,
      currentUser: null,
      subjects: [],
      masterySchemas: [],
    })

    await loadUser()

    if (!currentSchool) {
      await loadDefaultSchool()
    }

    // Load subjects if we have a current school
    if (currentSchool?.id) {
      await loadSubjectsForSchool(currentSchool.id)
    }
    await loadMasterySchemas()
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

// Load data when this module is imported
loadData()
