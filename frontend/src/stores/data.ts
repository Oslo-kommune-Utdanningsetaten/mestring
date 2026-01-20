import { get, writable, derived } from 'svelte/store'
import {
  subjectsList,
  schoolsList,
  masterySchemasList,
  rolesList,
  userSchoolsList,
  groupsList,
} from '../generated/sdk.gen'
import type { SchoolType, MasterySchemaType, GroupType } from '../generated/types.gen'
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
  TEACHER_ROLE,
  STUDENT_ROLE,
  PUBLIC_PATHS,
  STUDENT_PATHS,
  TEACHER_PATHS,
  RESTRICTED_PATHS,
} from '../utils/constants'
import type { AppData, UserDecorated } from '../types/models'

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

const hasUserAccessToPath = (path: string): boolean => {
  const currentData = get(dataStore) as AppData
  const currentUser = currentData.currentUser
  const trimmedPath = path.split('/')[1]
  // Not logged in can only access public paths
  if (!currentUser) {
    return PUBLIC_PATHS.includes(trimmedPath)
  }
  const { isSchoolAdmin, isSchoolInspector, isSuperadmin } = currentUser
  // Logged in students
  if (STUDENT_PATHS.includes(trimmedPath)) return true
  // Logged in teachers
  if (TEACHER_PATHS.includes(trimmedPath)) return true
  // Inspector or admin can access restricted paths
  if ((isSchoolAdmin || isSchoolInspector) && RESTRICTED_PATHS.includes(trimmedPath)) {
    return true
  }
  // Superadmin can access everything
  return isSuperadmin
}

const hasUserAccessToFeature = (
  resource: string,
  action: string,
  options: Record<string, string> = {}
): boolean => {
  const currentData = get(dataStore) as AppData
  const currentSchool = currentData.currentSchool
  if (!currentSchool || !currentSchool.isStatusEnabled) {
    return false
  }
  const currentUser = currentData.currentUser
  if (!currentUser) {
    return false
  }
  const { isSchoolAdmin, isSchoolInspector, isSuperadmin } = currentUser
  if (resource === 'status') {
    if (['create', 'update', 'delete'].includes(action)) {
      if (isSchoolAdmin || isSuperadmin) {
        return true
      }
      const { studentId, subjectId } = options
      // FIXME: This is a simplified check; the following logic should be implemented
      // Return true if user is teacher of the student in the subject
      // Return true if the user is a teacher of the basis group of the student
      return currentUser.teacherGroups.length > 0
    } else if (action === 'read') {
      return (
        isSchoolAdmin || isSchoolInspector || isSuperadmin || currentUser.teacherGroups.length > 0
      )
    }
  }
  return false
}

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

export const dataStore = writable<AppData>({
  subjects: [],
  currentSchool: null,
  currentUser: null,
  masterySchemas: [],
  roles: [],
  hasUserAccessToPath,
  hasUserAccessToFeature,
})

export const currentUser: UserDecorated = derived(dataStore, d => d.currentUser)

export const setCurrentUser = (user: UserDecorated | null) => {
  dataStore.update(data => ({ ...data, currentUser: user }))
}

export const registerUserStatus = async (school: SchoolType) => {
  const user = get(dataStore).currentUser
  const [
    schoolsResult,
    userSchoolsResult,
    teacherGroupsResult,
    studentGroupsResult,
    allGroupsResult,
  ] = await Promise.all([
    schoolsList({
      query: { isServiceEnabled: true },
    }),
    userSchoolsList({
      query: { user: user.id, school: school.id },
    }),
    groupsList({
      query: { user: user.id, school: school.id, roles: TEACHER_ROLE },
    }),
    groupsList({
      query: { user: user.id, school: school.id, roles: STUDENT_ROLE },
    }),
    groupsList({
      query: { school: school.id },
    }),
  ])
  const schools = schoolsResult.data || []
  const userSchools = userSchoolsResult.data || []
  const teacherGroups = teacherGroupsResult.data || []
  const studentGroups = studentGroupsResult.data || []
  const allGroups = allGroupsResult.data || []

  const isSchoolAdmin = !!userSchools.some(
    userSchool => userSchool.role.name === SCHOOL_ADMIN_ROLE && userSchool.school.id === school.id
  )
  const isSchoolInspector = !!userSchools.some(
    userSchool =>
      userSchool.role.name === SCHOOL_INSPECTOR_ROLE && userSchool.school.id === school.id
  )
  const userDecorated: UserDecorated = {
    ...user,
    schools,
    allGroups,
    teacherGroups,
    studentGroups,
    isSchoolAdmin,
    isSchoolInspector,
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
    dataStore.update(data => {
      return { ...data, currentUser: existingUser }
    })
    await registerRoles()
    await loadSchools()
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}
