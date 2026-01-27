import type { Mastery, GoalDecorated } from '../types/models'
import type {
  GoalType,
  SubjectType,
  ObservationType,
  GroupType,
  StatusType,
} from '../generated/types.gen'
import { goalsList, observationsList, usersRetrieve } from '../generated/sdk.gen'
import { nb as noLocale } from 'date-fns/locale'
import { format, formatDistanceToNow } from 'date-fns'

function removeNullValueKeys(obj: { [key: string]: string | null }): {
  [key: string]: string
} {
  return Object.fromEntries(Object.entries(obj).filter(([_, value]) => value !== null)) as {
    [key: string]: string
  }
}

export const urlStringFrom = (
  queryParams: { [key: string]: string | null },
  options?: { path?: string; mode?: string }
): string => {
  const path = options?.path || ''
  const prefix = path ? path + '?' : '?'

  // merge or replace
  const mode = options?.mode || 'replace'
  // merge: we keep the current query params and add new ones
  // replace: we discard the current query params and use new ones

  let finalParams = { ...queryParams }

  if (mode === 'merge') {
    const currentUrlParams = new URLSearchParams(window.location.search)
    const currentParams: { [key: string]: string } = {}
    currentUrlParams.forEach((value, key) => {
      currentParams[key] = value
    })
    finalParams = { ...currentParams, ...queryParams }
  }
  // if a key is null, remove it
  finalParams = removeNullValueKeys(finalParams)

  return (
    prefix +
    Object.keys(finalParams)
      .map(key => `${key}=${finalParams[key] ?? ''}`)
      .join('&')
  )
}

export const subjectNamesFromStudentGoals = (
  goals: GoalType[],
  allSubjects: SubjectType[]
): string[] => {
  const result = new Set<string>()
  goals.forEach((goal: GoalType) => {
    const subject = allSubjects.find((subject: SubjectType) => subject.id === goal.subjectId)
    if (subject) {
      result.add(subject.displayName)
    }
  })
  return Array.from(result)
}

export const fetchGoalsForSubjectAndStudent = async (
  subjectId: string,
  studentId: string,
  studentGroups: GroupType[]
): Promise<GoalDecorated[]> => {
  try {
    const goalsResult = await goalsList({ query: { student: studentId, subject: subjectId } })
    const goals = goalsResult.data || []
    const groupIds = goals.map(goal => goal.groupId).filter(Boolean) as string[]
    const groups = studentGroups.filter((group: GroupType) => groupIds.includes(group.id))
    const goalsBySubjectId = await goalsWithCalculatedMasteryBySubjectId(studentId, goals, groups)
    return goalsBySubjectId[subjectId]
  } catch (error) {
    console.error('Error fetching goals:', error)
    return []
  }
}

export const goalsWithCalculatedMastery = async (
  studentId: string,
  studentGoals: (GoalType & { observations?: ObservationType[] })[]
): Promise<GoalDecorated[]> => {
  // Check if observations are already included (from includeObservations=true)
  const hasInlineObservations = studentGoals.some(goal => Array.isArray(goal.observations))

  if (hasInlineObservations) {
    // Use inline observations - no additional API calls needed
    return studentGoals.map(goal => {
      const observations = goal.observations || []
      const decoratedGoal: GoalDecorated = { ...goal }
      decoratedGoal.masteryData = inferMastery(goal, observations)
      decoratedGoal.observations = observations
      return decoratedGoal
    })
  }

  // Fallback: fetch observations separately (legacy behavior)
  const observationsPromises = studentGoals.map(goal =>
    observationsList({
      query: { goal: goal.id, student: studentId },
    })
  )
  const observationsResults = await Promise.all(observationsPromises)
  const result = [] as GoalDecorated[]
  studentGoals.forEach((goal, index) => {
    const observations = observationsResults[index]?.data || []
    const decoratedGoal: GoalDecorated = { ...goal }
    decoratedGoal.masteryData = inferMastery(goal, observations)
    decoratedGoal.observations = observations
    result.push(decoratedGoal)
  })
  return result
}

// For a single student, output goals grouped by subjectId, with mastery data calculated
// If a goal does not have a subjectId, look up via the groupId
// Goals are sorted by sortOrder, then personal goals first
export const goalsWithCalculatedMasteryBySubjectId = async (
  studentId: string,
  studentGoals: GoalType[],
  groups: GroupType[]
) => {
  const decoratedGoals = await goalsWithCalculatedMastery(studentId, studentGoals)
  let goalsBySubjectId: Record<string, GoalDecorated[]> = {}
  decoratedGoals.forEach((goal: GoalDecorated) => {
    let subjectId = goal.subjectId
    if (!subjectId) {
      // goal is not personal, look up subject via group
      if (goal.groupId) {
        const group = groups.find(g => g.id === goal.groupId)
        if (group?.subjectId) {
          subjectId = group.subjectId
        } else {
          return
        }
      }
    }
    goalsBySubjectId[subjectId] = goalsBySubjectId[subjectId] || []
    goalsBySubjectId[subjectId].push(goal)
  })
  Object.keys(goalsBySubjectId).forEach(subjectId => {
    goalsBySubjectId[subjectId]
      .sort((a, b) => a.sortOrder - b.sortOrder)
      .sort((a, b) => {
        if (!a.isPersonal && b.isPersonal) return 1
        if (a.isPersonal && !b.isPersonal) return -1
        return 0
      })
  })
  return goalsBySubjectId
}

export const inferMastery = (
  goal: GoalType,
  observationsForGoal: ObservationType[]
): Mastery | null => {
  if (observationsForGoal.length === 0) {
    return null
  }
  const firstValue = observationsForGoal[0]?.masteryValue
  const lastValue = observationsForGoal[observationsForGoal.length - 1]?.masteryValue
  const trend = isNumber(lastValue) && isNumber(firstValue) ? lastValue - firstValue : 0
  return {
    mastery: lastValue || 0,
    trend: trend,
    title: `Siste verdi: ${lastValue}. Trend: ${trend}.`,
  }
}

export const aggregateMasterys = (goals: GoalDecorated[]): Mastery | null => {
  const masteryValues: number[] = []
  const trendValues: number[] = []
  goals.forEach(goal => {
    if (isNumber(goal.masteryData?.mastery)) {
      masteryValues.push(goal.masteryData.mastery)
    }
    if (isNumber(goal.masteryData?.trend)) {
      trendValues.push(goal.masteryData.trend)
    }
  })
  // if there are no mastery values, there will not be a trend either
  if (masteryValues.length === 0) {
    return null
  }
  return {
    mastery: findAverage(masteryValues),
    trend: findAverage(trendValues),
    title: `Aggregert: ${masteryValues.length}/${goals.length} mål har data`,
  }
}

export const findAverage = (numbers: number[]): number => {
  return numbers.reduce((sum, currentValue) => sum + currentValue, 0) / numbers.length
}

export const abbreviateName = (fullName: string): string => {
  const names = fullName.split(' ')
  const first = names[0]
  const rest = names.slice(1)
  return `${first} ${rest.map(n => n.charAt(0).toUpperCase() + '.').join(' ')}`
}

export const isNumber = (value: any) => {
  return typeof value === 'number'
}

// Count total observations per subject for a set of decorated goals
export const countObservationsBySubjectId = (
  goalsBySubjectId: Record<string, GoalDecorated[]>
): Record<string, number> => {
  const counts: Record<string, number> = {}
  Object.entries(goalsBySubjectId).forEach(([subjectId, goals]) => {
    counts[subjectId] = goals.reduce((sum, goal) => sum + (goal.observations?.length || 0), 0)
  })
  return counts
}

// Calculate be color luminance and determine if text should be white or black
export const getContrastFriendlyTextColor = (bgColor: string) => {
  // Convert hex to RGB
  let r = 0,
    g = 0,
    b = 0

  if (bgColor.startsWith('#')) {
    const hex = bgColor.replace('#', '')
    if (hex.length === 3) {
      r = parseInt(hex[0] + hex[0], 16)
      g = parseInt(hex[1] + hex[1], 16)
      b = parseInt(hex[2] + hex[2], 16)
    } else if (hex.length === 6) {
      r = parseInt(hex.substring(0, 2), 16)
      g = parseInt(hex.substring(2, 4), 16)
      b = parseInt(hex.substring(4, 6), 16)
    }
  } else if (bgColor.startsWith('rgb')) {
    const matches = bgColor.match(/\d+/g)
    if (matches) {
      r = parseInt(matches[0])
      g = parseInt(matches[1])
      b = parseInt(matches[2])
    }
  }

  // Normalize RGB values from 0-255 range to 0-1 range
  const normalize = (val: number) => val / 255
  const [rNorm, gNorm, bNorm] = [normalize(r), normalize(g), normalize(b)]

  // Apply sRGB gamma correction to convert from display space to linear light values
  // Source: https://www.w3.org/TR/WCAG20/#relativeluminancedef
  const gammaCorrect = (val: number) =>
    val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4)

  // Calculate relative luminance (perceived brightness to human eye)
  // Source: https://www.w3.org/TR/WCAG20/#relativeluminancedef
  // Weights based on human eye sensitivity (we're most sensitive to green, least to blue):
  const bgLuminance =
    0.2126 * gammaCorrect(rNorm) + 0.7152 * gammaCorrect(gNorm) + 0.0722 * gammaCorrect(bNorm)

  // Calculate contrast ratios against white and black text
  // Source: https://www.w3.org/TR/WCAG20/#contrast-ratiodef
  const whiteLuminance = 1
  const blackLuminance = 0

  const contrastWithWhite = (whiteLuminance + 0.05) / (bgLuminance + 0.05)
  const contrastWithBlack = (bgLuminance + 0.05) / (blackLuminance + 0.05)

  return contrastWithWhite > contrastWithBlack ? '#ffffff' : '#000000'
}

export const formatDateTime = (isoDate?: string | number | undefined) => {
  if (!isoDate) return null
  return format(new Date(isoDate), 'yyyy-MM-dd HH:mm')
}

export const formatDate = (isoDate?: string | number | undefined) => {
  if (!isoDate) return null
  return format(new Date(isoDate), 'yyyy-MM-dd')
}

export const formatDateHumanly = (isoDate?: string | number | undefined) => {
  if (!isoDate) return null
  return format(new Date(isoDate), 'dd. LLLL yyyy', { locale: noLocale })
}

export const formatMonthName = (isoDate?: string | number | undefined) => {
  if (!isoDate) return null
  return format(new Date(isoDate), 'LLLL', { locale: noLocale })
}

export const formatDateDistance = (isoDate?: string | number | undefined) => {
  if (!isoDate) return null
  return formatDistanceToNow(new Date(isoDate), { addSuffix: true, locale: noLocale })
}
