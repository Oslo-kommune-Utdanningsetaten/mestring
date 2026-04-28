import { get, writable, derived } from 'svelte/store'
import {
  subjectsList,
  statusCategoriesList,
  schoolsList,
  masterySchemasList,
  rolesList,
  groupsList,
} from '../generated/sdk.gen'
import type { SchoolType, MasterySchemaType } from '../generated/types.gen'
import { localStorage } from '../stores/localStorage'
import { fetchUserData } from '../utils/functions'
import { SUBJECTS_ALLOWED_ALL, SUBJECTS_ALLOWED_CUSTOM, USER_ROLES } from '../utils/constants'
import type { AppData, UserDecorated } from '../types/models'

const setMasterySchemas = (schemas: MasterySchemaType[]) => {
  // Default mastery schema is either school default, or the user's preferred, or simply first in list
  const defaultSchema =
    schemas.find(schema => schema.isDefault) ||
    schemas.find(schema => schema.id === localStorage<string>('preferredMasterySchemaId').get()) ||
    (schemas.length > 0 ? schemas[0] : null)
  dataStore.update(data => {
    return { ...data, masterySchemas: schemas, defaultMasterySchema: defaultSchema }
  })
}

// When school changes, reset subjects, user status, and mastery schemas
export const setCurrentSchool = (school: SchoolType) => {
  const currentData = get(dataStore) as AppData
  if (currentData.currentSchool?.id !== school?.id) {
    localStorage<SchoolType>('currentSchool').set(school)
    dataStore.update(data => {
      return { ...data, currentSchool: school }
    })
    if (school?.id) {
      registerSubjects(school)
      registerUserStatus(school)
      registerMasterySchemas(school)
      registerStatusCategories(school)
    }
  }
}

export const dataStore = writable<AppData>({
  currentSchool: null,
  currentUser: null,
  subjects: [],
  statusCategories: [],
  masterySchemas: [],
  roles: [],
})

export const currentUser: UserDecorated = derived(dataStore, d => d.currentUser)
export const currentSchool = derived(dataStore, d => d.currentSchool)
export const subjects = derived(dataStore, d => d.subjects)

export const setCurrentUser = (user: UserDecorated | null) => {
  dataStore.update(data => ({ ...data, currentUser: user }))
}

export const registerUserStatus = async (school: SchoolType) => {
  const user = get(dataStore).currentUser
  const [userData, schoolsResult, allGroupsResult] = await Promise.all([
    fetchUserData(user.id, school.id),
    schoolsList({
      query: { isServiceEnabled: true },
    }),
    groupsList({
      query: { school: school.id },
    }),
  ])
  const { teacherGroups, studentGroups, userSchools } = userData
  const allGroups = allGroupsResult.data || []

  const schools = ((schoolsResult.data || []) as SchoolType[]).sort((a, b) =>
    a.displayName.localeCompare(b.displayName)
  )
  const isSchoolAdmin = !!userSchools.some(
    userSchool => userSchool.role.name === USER_ROLES.ADMIN && userSchool.school.id === school.id
  )
  const isSchoolInspector = !!userSchools.some(
    userSchool =>
      userSchool.role.name === USER_ROLES.INSPECTOR && userSchool.school.id === school.id
  )
  const userRoles = [
    studentGroups.length > 0 ? USER_ROLES.STUDENT : null,
    teacherGroups.length > 0 ? USER_ROLES.TEACHER : null,
    isSchoolAdmin ? USER_ROLES.ADMIN : null,
    isSchoolInspector ? USER_ROLES.INSPECTOR : null,
    user.isSuperadmin ? USER_ROLES.SUPERADMIN : null,
  ].filter(Boolean)

  const userDecorated: UserDecorated = {
    ...user,
    schools,
    allGroups,
    teacherGroups,
    studentGroups,
    userSchools,
    isSchoolAdmin,
    isSchoolInspector,
    roles: userRoles,
  }
  setCurrentUser(userDecorated)
}

const loadSchools = async () => {
  let schools: SchoolType[] = []
  try {
    const result = await schoolsList()
    schools = result.data || []
  } catch (error) {
    console.error('Error fetching schools:', error)
    return null
  }

  let localStorageSchool = localStorage<SchoolType>('currentSchool').get()
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
  localStorage<SchoolType>('currentSchool').remove()
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

const registerStatusCategories = async (school: SchoolType) => {
  try {
    const result = await statusCategoriesList({
      query: { school: school.id },
    })
    const categories = result.data || []
    dataStore.update(data => {
      return { ...data, statusCategories: categories }
    })
  } catch (error) {
    console.error('Error fetching status categories:', error)
    dataStore.update(data => {
      return { ...data, statusCategories: [] }
    })
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
        // 'only-feide'
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
    dataStore.update(data => {
      return { ...data, currentUser: existingUser }
    })
    await registerRoles()
    await loadSchools()
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}
