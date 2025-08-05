import { get, writable } from 'svelte/store'
import type { Writable as WritableType } from 'svelte/store'
import {
  subjectsList,
  schoolsList,
  masterySchemasList,
  usersRetrieve,
} from '../generated/sdk.gen'
import type { SchoolReadable, MasterySchemaReadable, UserReadable } from '../generated/types.gen'
import { getLocalStorageItem, setLocalStorageItem } from '../stores/localStorage'
import type { AppData } from '../types/models'
import { currentUser as authUser, loggedIn } from './auth'

const loadUser = async () => {
  try {
    const authUserData = get(authUser)
    const isAuthenticated = get(loggedIn)

    // Try to load authenticated database user
    if (isAuthenticated && authUserData?.id) {
      const { data: user } = await usersRetrieve({ path: { id: String(authUserData.id) } })
      if (user) {
        setCurrentUser(user)
        return
      }
    }
    if (isAuthenticated && authUserData) {
      const sessionUser: UserReadable = {
        id: String(null),
        name: authUserData.name,
        email: authUserData.email,
        feideId: authUserData.feide_id,
        groups: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        maintainedAt: new Date().toISOString(),
        lastActivityAt: null,
        disabledAt: null,
        createdById: '',
        updatedById: '',
      }
      setCurrentUser(sessionUser)
      return
    }
  } catch (error) {
    console.error('Error loading user:', error)
  }
}

export const setCurrentUser = (user: UserReadable) => {
  setLocalStorageItem('currentUser', user)
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
    const currentUser: UserReadable | null = getLocalStorageItem(
      'currentUser'
    ) as UserReadable | null

    dataStore.set({
      currentSchool,
      currentUser,
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
