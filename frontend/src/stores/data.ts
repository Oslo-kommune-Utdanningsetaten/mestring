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
import { fetchUserData } from '../utils/functions'
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
  GROUP_TYPE_BASIS,
  GROUP_TYPE_TEACHING,
} from '../utils/constants'
import type { AppData, UserDecorated, HasUserAccessToFeatureOptions } from '../types/models'

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
  options: HasUserAccessToFeatureOptions = {}
): boolean => {
  const currentData = get(dataStore) as AppData
  const currentSchool = currentData.currentSchool
  if (!currentSchool || !currentSchool.isStatusEnabled) {
    return false
  }
  const currentUser = currentData.currentUser
  if (!currentUser) return false

  const { isSchoolAdmin, isSuperadmin } = currentUser

  if (isSchoolAdmin || isSuperadmin) return true

  if (resource === 'status') {
    if (['create', 'update', 'delete'].includes(action)) {
      // Early negative return if user has no teacher groups
      if (currentUser.teacherGroups.length < 1) return false

      const { subjectId, studentGroupIds } = options
      // Early negative return if no student groups provided
      if (!studentGroupIds) return false

      return currentUser.teacherGroups.some((teacherGroup: GroupType) => {
        // Teaching group
        if (
          teacherGroup.type === GROUP_TYPE_TEACHING &&
          subjectId &&
          teacherGroup.subjectId === subjectId &&
          studentGroupIds.includes(teacherGroup.id)
        ) {
          // User is a teacher of the student in the subject
          return true
        }
        // Basis group
        if (teacherGroup.type === GROUP_TYPE_BASIS && studentGroupIds.includes(teacherGroup.id)) {
          // User is teacher in the basis group to which the student belongs
          return true
        }
        return false
      })
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
    userSchools,
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
