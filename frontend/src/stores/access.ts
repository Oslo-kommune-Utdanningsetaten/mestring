import { derived } from 'svelte/store'
import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'
import { ROUTES } from '../utils/routes'
import type { GroupType, SchoolType, SubjectType } from '../generated/types.gen'
import type { UserDecorated, UserRoleType, HasUserAccessToFeatureOptions } from '../types/models'
import { currentUser, currentSchool, subjects } from './data'

export const hasUserAccessToPath = derived(
  currentUser,
  $currentUser => (pathString: string) => checkUserAccessToPath($currentUser, pathString)
)

export const hasUserAccessToFeature = derived(
  [currentUser, currentSchool, subjects],
  ([$currentUser, $currentSchool, $subjects]) =>
    (resource: string, action: string, options: HasUserAccessToFeatureOptions = {}) =>
      checkUserAccessToFeature($currentUser, $currentSchool, $subjects, resource, action, options)
)

const checkUserAccessToPath = (currentUser: UserDecorated | null, pathString: string): boolean => {
  const path = ROUTES.find(route => route.path === pathString)
  const { isPublic, accessibleBy } = path || {}
  if (isPublic) return true
  if (!currentUser) return false

  // check for overlapping roles and accessibleBy
  if (accessibleBy) {
    return currentUser.roles?.some((role: UserRoleType) => accessibleBy.includes(role))
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

  const { subjectId, studentGroupIds, studentId, groupId, createdById } = options
  const subject = subjects.find(s => s.id === subjectId)

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
      return currentUser.teacherGroups.some((teacherGroup: GroupType) => {
        // Teacher teaches the subject to this student
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
