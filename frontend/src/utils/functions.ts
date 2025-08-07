import type { Mastery, GoalDecorated } from '../types/models'
import type { GoalReadable, SubjectReadable, ObservationReadable } from '../generated/types.gen'
import { usersGoalsRetrieve, observationsList, usersGroupsRetrieve } from '../generated/sdk.gen'
import { dataStore } from '../stores/data'

function removeNullValueKeys(obj: { [key: string]: string | null }): {
  [key: string]: string
} {
  return Object.fromEntries(Object.entries(obj).filter(([_, value]) => value !== null)) as {
    [key: string]: string
  }
}

export const getMasteryColorByValue = (value: number, masteryLevels: any[]): string => {
  const masteryLevel = masteryLevels.find(ml => ml.minValue <= value && ml.maxValue >= value)
  return masteryLevel ? masteryLevel.color : 'black'
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
  goals: GoalReadable[],
  allSubjects: SubjectReadable[]
): string[] => {
  const result = new Set<string>()
  goals.forEach((goal: GoalReadable) => {
    const subject = allSubjects.find((subject: SubjectReadable) => subject.id === goal.subjectId)
    if (subject) {
      result.add(subject.displayName)
    }
  })
  return Array.from(result)
}

export const goalsWithCalculatedMastery = async (
  studentId: string,
  studentGoals: GoalReadable[]
): Promise<GoalDecorated[]> => {
  const observationsPromises = studentGoals.map(goal =>
    observationsList({
      query: { goalId: goal.id, studentId: studentId },
    })
  )
  const observationsResults = await Promise.all(observationsPromises)
  const result = [] as GoalDecorated[]
  studentGoals.forEach((goal, index) => {
    const observations = observationsResults[index]?.data || []
    const subjectId = goal.subjectId
    if (!subjectId) {
      console.error(`Goal ${goal.id} has no subjectId!`)
      return
    }

    const decoratedGoal: GoalDecorated = { ...goal }
    decoratedGoal.masteryData = inferMastery(goal, observations)
    decoratedGoal.observations = observations
    result.push(decoratedGoal)
  })
  return result
}

export const subjectIdsViaGroupOrGoal = async (
  studentId: string,
  schoolId: string
): Promise<string[]> => {
  const subjectsId: Set<string> = new Set()
  const userGroups: any = await usersGroupsRetrieve({
    path: { id: studentId },
    query: { roles: 'student', school: schoolId },
  })
  userGroups.data.forEach((group: any) => {
    if (group.subjectId && ['undervisning', 'teaching'].includes(group.type)) {
      subjectsId.add(group.subjectId)
    }
  })
  const userGoals: any = await usersGoalsRetrieve({
    path: { id: studentId },
  })
  userGoals.data.forEach((goal: GoalReadable) => {
    if (goal.subjectId) {
      subjectsId.add(goal.subjectId)
    }
  })
  return Array.from(subjectsId)
}

export const goalsWithCalculatedMasteryBySubjectId = async (
  studentId: string,
  studentGoals: GoalReadable[]
) => {
  const decoratedGoals = await goalsWithCalculatedMastery(studentId, studentGoals)
  let goalsBySubjectId: Record<string, GoalDecorated[]> = {}
  decoratedGoals.forEach((goal: GoalDecorated) => {
    const subjectId = goal.subjectId
    if (!subjectId) {
      console.error(`Goal ${goal.id} has no subjectId!`)
      return
    }
    goalsBySubjectId[subjectId] = goalsBySubjectId[subjectId] || []
    goalsBySubjectId[subjectId].push(goal)
  })
  Object.keys(goalsBySubjectId).forEach(subjectId => {
    goalsBySubjectId[subjectId].sort((a, b) => a.sortOrder - b.sortOrder)
  })
  return goalsBySubjectId
}

export const inferMastery = (
  goal: GoalReadable,
  observationsForGoal: ObservationReadable[]
): Mastery | null => {
  if (observationsForGoal.length === 0) {
    return null
  }
  const firstValue = observationsForGoal[0]?.masteryValue
  const lastValue = observationsForGoal[observationsForGoal.length - 1]?.masteryValue
  const trend = isNumber(lastValue) && isNumber(firstValue) ? lastValue - firstValue : null
  return {
    mastery: lastValue || 0,
    trend: trend || 0,
    title: `${goal.title}: ${lastValue}`,
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

export const isNumber = (value: any) => {
  return typeof value === 'number'
}
