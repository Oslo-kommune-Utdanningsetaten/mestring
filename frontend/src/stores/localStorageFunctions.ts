import { derived } from 'svelte/store'
import { localStorage } from './localStorage'
import { getCurrentSchoolYear, inferCreatedParams } from '../utils/schoolYear'

export const getPreferredCreatedParams = () => {
  const preferredSchoolYear =
    localStorage<string>('preferredSchoolYear').get() || getCurrentSchoolYear()
  return inferCreatedParams(preferredSchoolYear)
}

// Reactive store, subscribe with $preferredSchoolYear
export const preferredSchoolYear = derived(
  localStorage<string>('preferredSchoolYear'),
  $preferredSchoolYear => $preferredSchoolYear || getCurrentSchoolYear()
)

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

export const getPreferredSchoolYear = () => {
  const preferredSchoolYear = localStorage<string>('preferredSchoolYear').get()
  return preferredSchoolYear || getCurrentSchoolYear()
}

export const isObservationUrlEnabled = () => {
  const result = localStorage<string>('isObservationUrlEnabled').get()
  return Boolean(result)
}

export const isMasteryBarChartVisible = () => {
  const result = localStorage<string>('isMasteryBarChartVisible').get()
  return Boolean(result)
}
