import { localStorage } from './localStorage'
import { GROUP_VALIDITY_OPTIONS, MASTERY_BADGE_VARIANTS } from '../utils/constants'
import { getAllSchoolYears, inferCreatedParams } from '../utils/schoolYear'

export const getPreferredCreatedParams = () => {
  const preferredSchoolYear =
    localStorage<string>('preferredSchoolYear').get() || getAllSchoolYears()[-1]
  return inferCreatedParams(preferredSchoolYear)
}

export const getPreferredGroupValidity = () => {
  const preferredGroupValidity =
    localStorage<GROUP_VALIDITY_OPTIONS>('preferredGroupValidity').get()
  const defaultGroupValidity = GROUP_VALIDITY_OPTIONS.ONLY
  return preferredGroupValidity || defaultGroupValidity
}

export const getPreferredSchoolYear = () => {
  const preferredSchoolYear = localStorage<string>('preferredSchoolYear').get()
  const defaultSchoolYear = getAllSchoolYears()[-1]
  return preferredSchoolYear || defaultSchoolYear
}

export const getPreferredMasteryBadgeVariant = () => {
  const preferredMasteryBadgeVariant = localStorage<MASTERY_BADGE_VARIANTS>(
    'preferredMasteryBadgeVariant'
  ).get()
  const defaultMasteryBadgeVariant = MASTERY_BADGE_VARIANTS.BEEHIVE
  return preferredMasteryBadgeVariant || defaultMasteryBadgeVariant
}

export const getPreferredSubjectId = () => {
  const preferredSubjectId = localStorage<string>('preferredSubjectId').get()
  return preferredSubjectId || null
}

export const getPreferredStatusCategory = () => {
  const preferredStatusCategoryId = localStorage<string>('preferredStatusCategoryId').get()
  return preferredStatusCategoryId || null
}

export const getPreferredMasterySchemaId = () => {
  const preferredMasterySchemaId = localStorage<string>('preferredMasterySchemaId').get()
  return preferredMasterySchemaId || null
}
