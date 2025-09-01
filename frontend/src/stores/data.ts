import { get, writable } from 'svelte/store'
import type { Writable as WritableType } from 'svelte/store'
import { subjectsList, schoolsList, masterySchemasList, rolesList } from '../generated/sdk.gen'
import type { SchoolReadable, MasterySchemaReadable } from '../generated/types.gen'
import {
  getLocalStorageItem,
  setLocalStorageItem,
  removeLocalStorageItem,
} from '../stores/localStorage'
import type { AppData } from '../types/models'
import { currentUser } from './auth'

let masterySchemasCache = null as MasterySchemaReadable[] | null

export const refreshCurrentUser = () => {
  const user = get(currentUser)
  const currentData = get(dataStore)
  if (currentData.currentUser?.id !== user?.id) {
    dataStore.update(data => {
      return { ...data, currentUser: user }
    })
  }
}

export const setCurrentSchool = (school: SchoolReadable) => {
  const currentData = get(dataStore)
  if (currentData.currentSchool?.id !== school?.id) {
    setLocalStorageItem('currentSchool', school)
    dataStore.update(data => {
      return { ...data, currentSchool: school }
    })
    if (school?.id) {
      loadSubjectsForSchool(school.id)
    }
  }
}

const setMasterySchemas = (schemas: MasterySchemaReadable[]) => {
  masterySchemasCache = schemas
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

const loadSchool = async () => {
  let schools: SchoolReadable[] = []
  try {
    const result = await schoolsList()
    schools = result.data || []
  } catch (error) {
    console.error('Error fetching schools:', error)
    return null
  }

  let previousSchool = getLocalStorageItem('currentSchool') as SchoolReadable | null
  const isPreviousSchoolValid =
    previousSchool &&
    schools.find(school => school.id === previousSchool.id && school.isServiceEnabled)

  if (isPreviousSchoolValid) {
    // Previously used school is still valid, set it as current school
    setCurrentSchool(previousSchool)
    return
  }
  // Just grab the first school that is enabled
  const selectedSchool = schools.find(school => school.isServiceEnabled)
  if (selectedSchool) {
    setCurrentSchool(selectedSchool)
    return
  }
  console.warn('No valid school found')
  removeLocalStorageItem('currentSchool')
}

const refreshMasterySchemas = async (hardRefresh: boolean) => {
  if (hardRefresh) {
    masterySchemasCache = null
  }
  if (masterySchemasCache) {
    return
  }
  try {
    const result = await masterySchemasList()
    const schemas = result.data || []
    setMasterySchemas(schemas)
  } catch (error) {
    console.error('Error fetching mastery schemas:', error)
    masterySchemasCache = null
    return null
  }
}

const loadSubjectsForSchool = async (schoolId: string): Promise<void> => {
  try {
    const result = await subjectsList({
      query: {
        school: schoolId,
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

const loadRoles = async (): Promise<void> => {
  try {
    const result = await rolesList()
    const roles = result.data || []
    dataStore.update(data => {
      return { ...data, roles }
    })
  } catch (error) {
    console.error('Failed to load roles:', error)
    dataStore.update(data => {
      return { ...data, roles: [] }
    })
  }
}

export const loadData = async () => {
  try {
    dataStore.set({
      currentSchool: null,
      currentUser: null,
      subjects: [],
      masterySchemas: [],
      roles: [],
    })

    await refreshCurrentUser()
    await loadRoles()
    await loadSchool()
    await refreshMasterySchemas(false)
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}
