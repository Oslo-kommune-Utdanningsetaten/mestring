import { derived } from 'svelte/store'
import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'
import { ROUTES } from '../utils/routes'
import type { GroupType, SchoolType, SubjectType } from '../generated/types.gen'
import type { UserDecorated, UserRoleType, HasUserAccessToFeatureOptions } from '../types/models'
import { currentUser, currentSchool, subjects } from './data'
import { getCurrentSchoolYear } from '../utils/schoolYear'
import { getPreferredSchoolYear } from './localStorageFunctions'

export const hasUserAccessToPath = derived(
  [currentUser, currentSchool],
  ([$currentUser, $currentSchool]) =>
    (pathString: string) =>
      checkUserAccessToPath($currentUser, $currentSchool, pathString)
)

export const hasUserAccessToFeature = derived(
  [currentUser, currentSchool, subjects],
  ([$currentUser, $currentSchool, $subjects]) =>
    (resource: string, action: string, options: HasUserAccessToFeatureOptions = {}) =>
      checkUserAccessToFeature($currentUser, $currentSchool, $subjects, resource, action, options)
)

const checkUserAccessToPath = (
  currentUser: UserDecorated | null,
  currentSchool: SchoolType | null,
  pathString: string
): boolean => {
  const path = ROUTES.find(route => route.path === pathString)
  const { isPublic, accessibleBy, schoolConfig } = path || {}
  if (isPublic) return true
  if (!currentUser) return false
  if (currentUser.isSuperadmin) return true

  // check for overlapping roles and accessibleBy
  if (accessibleBy) {
    const hasUserRoleAccess = currentUser.roles?.some((role: UserRoleType) =>
      accessibleBy.includes(role)
    )
    if (hasUserRoleAccess && currentSchool && schoolConfig) {
      // check if the school config is enabled
      return Boolean(currentSchool[schoolConfig as keyof SchoolType])
    } else {
      return hasUserRoleAccess
    }
  }
  return false
}

const checkUserAccessToFeature = (
  currentUser: UserDecorated | null,
  currentSchool: SchoolType | null,
  subjects: SubjectType[],
  resource: string,
  action: string,
  options: HasUserAccessToFeatureOptions = {}
): boolean => {
  if (!currentSchool) return false // no school, no access
  if (!currentUser) return false // not logged in, no access
  if (currentUser.isSchoolAdmin || currentUser.isSuperadmin) return true // school admins and superadmins have access to everything

  const { subjectId, studentGroupIds, studentId, goalStudentId, groupId, createdById } = options
  const subject = subjects.find(s => s.id === subjectId)
  const group = groupId ? currentUser.allGroups.find((g: GroupType) => g.id === groupId) : null

  if (groupId && (!group || !group.isValid)) {
    // group is inaccessible to normal users
    return false
  }

  // Disallow create/update/delete actions if the user has selected a different school year than the current one
  // Prevents modifying data in past (or future) school years
  if (
    getCurrentSchoolYear() !== getPreferredSchoolYear() &&
    ['create', 'update', 'delete'].includes(action)
  ) {
    return false
  }

  if (resource === 'status') {
    if (!currentSchool.isStatusEnabled) {
      return false
    }
    if (['create', 'update', 'delete'].includes(action)) {
      return currentUser.teacherGroups.some((teacherGroup: GroupType) => {
        // Teacher teaches the subject to this student
        if (
          [GROUP_TYPE_TEACHING, GROUP_TYPE_BASIS].includes(teacherGroup.type) &&
          subjectId &&
          teacherGroup.subjectId === subjectId &&
          studentGroupIds?.includes(teacherGroup.id)
        ) {
          // User is a teacher of the student in the subject
          return true
        }
        // User is teacher in the basis group to which the student belongs and the subject is owned by the school
        if (
          teacherGroup.type === GROUP_TYPE_BASIS &&
          studentGroupIds?.includes(teacherGroup.id) &&
          subject?.ownedBySchoolId
        ) {
          return true
        }
        return false
      })
    }
  } else if (resource === 'goal') {
    if (['create', 'update', 'delete'].includes(action)) {
      return currentUser.teacherGroups.some((teacherGroup: GroupType) => {
        // Unspecified subject and user is teacher of the student
        // Used when creating an individual goal and the subject is not yet selected
        if (!subject && studentGroupIds?.includes(teacherGroup.id)) {
          return true
        }
        // User is teacher in a group to which the student belongs and (the subject is owned by the school OR the group has a subject)
        // Used when creating an individual goal and the subject is selected
        if (
          studentGroupIds?.includes(teacherGroup.id) &&
          (subject?.ownedBySchoolId ||
            (!!teacherGroup?.subjectId && teacherGroup?.subjectId === subjectId))
        ) {
          return true
        }
        // User is teacher in this group
        // Used when creating/editing a group goal
        if (groupId && groupId === teacherGroup.id) {
          return true
        }
        return false
      })
    }
  } else if (resource === 'observation') {
    if (['create'].includes(action)) {
      // Student check
      if (
        currentSchool.isServiceEnabledForStudents &&
        currentSchool.isCreateEnabledForStudents &&
        currentUser.id === studentId &&
        (groupId
          ? currentUser.studentGroups.some((studentGroup: GroupType) => studentGroup.id === groupId)
          : goalStudentId === studentId)
      )
        return true

      // Teacher check
      return currentUser.teacherGroups.some((teacherGroup: GroupType) => {
        if (
          subjectId &&
          teacherGroup.subjectId === subjectId &&
          studentGroupIds?.includes(teacherGroup.id)
        ) {
          // User is a teacher of the student in the subject
          return true
        }
        // User is teacher in the basis group to which the student belongs and the subject is owned by the school
        if (
          teacherGroup.type === GROUP_TYPE_BASIS &&
          studentGroupIds?.includes(teacherGroup.id) &&
          subject?.ownedBySchoolId
        ) {
          return true
        }
        return false
      })
    } else if (['update', 'delete'].includes(action)) {
      // Student check
      if (
        currentSchool.isServiceEnabledForStudents &&
        currentSchool.isCreateEnabledForStudents &&
        currentUser.id === studentId &&
        currentUser.id === createdById &&
        (groupId
          ? currentUser.studentGroups.some((studentGroup: GroupType) => studentGroup.id === groupId)
          : goalStudentId === studentId)
      )
        return true

      // Teacher check
      return currentUser.teacherGroups.some((teacherGroup: GroupType) => {
        // User is teacher in this group and the observation was created by the user
        if (groupId && groupId === teacherGroup.id && createdById === currentUser.id) {
          return true
        }
      })
    }
  } else if (resource === 'group') {
    if (['compare'].includes(action)) {
      return currentUser.isSchoolAdmin || currentUser.isSchoolInspector
    }
  }
  return false
}
