import { get, writable, derived } from 'svelte/store'
import {
  subjectsList,
  schoolsList,
  masterySchemasList,
  rolesList,
  userSchoolsList,
} from '../generated/sdk.gen'
import type { SchoolType, MasterySchemaType, UserType } from '../generated/types.gen'
import {
  getLocalStorageItem,
  setLocalStorageItem,
  removeLocalStorageItem,
} from '../stores/localStorage'
import {
  SUBJECTS_ALLOWED_ALL,
  SUBJECTS_ALLOWED_CUSTOM,
  SCHOOL_ADMIN_ROLE,
  SCHOOL_INSPECTOR_ROLE,
} from '../utils/constants'
import type { AppData } from '../types/models'

// When school changes, reset subjects, user status, and mastery schemas
export const setCurrentSchool = (school: SchoolType) => {
  const currentData = get(dataStore) as AppData
  if (currentData.currentSchool?.id !== school?.id) {
    setLocalStorageItem('currentSchool', school)
    dataStore.update(data => {
      return { ...data, currentSchool: school }
    })
    if (school?.id) {
      registerSubjects(school)
      registerUserStatus(school)
      registerMasterySchemas(school)
    }
  }
}

const setMasterySchemas = (schemas: MasterySchemaType[]) => {
  // Default mastery schema is either system default, or user's preferred, or simply first in list
  const defaultSchema =
    schemas.find(schema => schema.isDefault) ||
    schemas.find(schema => schema.id === getLocalStorageItem('preferredMasterySchemaId')) ||
    (schemas.length > 0 ? schemas[0] : null)
  dataStore.update(data => {
    return { ...data, masterySchemas: schemas, defaultMasterySchema: defaultSchema }
  })
}

export const dataStore = writable<AppData>({
  subjects: [],
  currentSchool: null,
  currentUser: null,
  masterySchemas: [],
})

export const currentUser = derived(dataStore, d => d.currentUser)

export const setCurrentUser = (user: UserType | null) => {
  dataStore.update(data => ({ ...data, currentUser: user }))
}

export const registerUserStatus = async (school: SchoolType) => {
  const user = get(dataStore).currentUser
  const userSchoolsResult = await userSchoolsList({
    query: { user: user.id, school: school.id },
  })
  const userSchools = userSchoolsResult.data || []
  const isSchoolAdmin = !!userSchools.some(userSchool => userSchool.role.name === SCHOOL_ADMIN_ROLE)
  const isSchoolInspector = !!userSchools.some(
    userSchool => userSchool.role.name === SCHOOL_INSPECTOR_ROLE
  )
  dataStore.update(data => ({
    ...data,
    isSchoolAdmin,
    isSchoolInspector,
    isSuperadmin: user.isSuperadmin,
  }))
}

const loadSchool = async () => {
  let schools: SchoolType[] = []
  try {
    const result = await schoolsList()
    schools = result.data || []
  } catch (error) {
    console.error('Error fetching schools:', error)
    return null
  }

  let localStorageSchool = getLocalStorageItem('currentSchool') as SchoolType | null
  const previousSchool: SchoolType | undefined = schools.find(
    school => school.id === localStorageSchool?.id && school.isServiceEnabled
  )

  if (previousSchool) {
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

const registerMasterySchemas = async (school: SchoolType) => {
  try {
    const result = await masterySchemasList({
      query: { school: school.id },
    })
    const schemas = result.data || []
    setMasterySchemas(schemas)
  } catch (error) {
    console.error('Error fetching mastery schemas:', error)
    return null
  }
}

const registerSubjects = async (school: SchoolType): Promise<void> => {
  try {
    const result = await subjectsList({
      query: {
        school: school.id,
      },
    })
    const subjects = (result.data || []).filter(subject => {
      if (school.subjectsAllowed == SUBJECTS_ALLOWED_ALL) return true
      if (school.subjectsAllowed == SUBJECTS_ALLOWED_CUSTOM) {
        return !!subject.ownedBySchoolId
      } else {
        // 'only-group'
        return !subject.ownedBySchoolId
      }
    })
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

const registerRoles = async (): Promise<void> => {
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
    const existingUser = get(dataStore).currentUser
    dataStore.set({
      currentSchool: null,
      currentUser: existingUser,
      subjects: [],
      masterySchemas: [],
      roles: [],
    })
    await registerRoles()
    await loadSchool()
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}
