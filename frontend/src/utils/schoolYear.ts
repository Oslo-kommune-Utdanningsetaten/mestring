import { GROUP_VALIDITY_OPTIONS } from './constants'

export const calculateSchoolYearMilestones = (customDate?: Date) => {
  const date = customDate || new Date()
  const year = date.getFullYear()
  const month = date.getMonth()
  const schoolStartYear = month < 7 ? year - 1 : year

  return {
    startAt: `${schoolStartYear}-08-15`,
    midyearAt: `${schoolStartYear + 1}-01-15`,
    endAt: `${schoolStartYear + 1}-06-30`,
  }
}

// Returns an array of ascending school years since launch e.g. ["2025-2026", "2026-2027"]
export const getAllSchoolYears = (asOfDate?: Date) => {
  const firstYearStart = 2025 // Mestring was launched in 2025, so no older data exists
  const currentYearStart = Number(calculateSchoolYearMilestones(asOfDate).startAt.split('-')[0])
  const schoolYears: string[] = []
  for (let year = firstYearStart; year <= currentYearStart; year++) {
    schoolYears.push(`${year}-${year + 1}`)
  }
  return schoolYears
}

// Convenience function to get the current school year
export const getCurrentSchoolYear = () => {
  return getAllSchoolYears().reverse()[0]
}

// Assuming schoolYear is a string like "2025-2026" or "2025-2027"
// Return createdBefore and createdAfter params
export const inferCreatedParams = (yearRange: string) => {
  if (yearRange === 'all') {
    return {}
  }
  const firstYear = Number(yearRange.split('-')[0])
  const lastYear = Number(yearRange.split('-')[1])
  const { startAt: createdAfter } = calculateSchoolYearMilestones(new Date(`${firstYear}-08-15`))
  const { endAt: createdBefore } = calculateSchoolYearMilestones(new Date(`${lastYear - 1}-08-15`))
  return { createdAfter, createdBefore }
}

export const inferGroupValidityParams = (schoolYear: string) => {
  const params: Record<'valid', string> = { valid: '' }
  if (schoolYear === 'all') {
    // All years selected --> include all groups regardless of validity
    params.valid = GROUP_VALIDITY_OPTIONS.INCLUDE
  } else if (schoolYear === getCurrentSchoolYear()) {
    // Current year selected --> only include valid groups
    params.valid = GROUP_VALIDITY_OPTIONS.ONLY
  } else {
    // Past year selected --> only include invalid groups
    params.valid = GROUP_VALIDITY_OPTIONS.EXCLUDE
  }
  return params
}
