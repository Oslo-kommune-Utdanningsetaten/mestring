import type { Mastery } from '../types/models'
import { type GoalReadable, type SubjectReadable } from '../api/types.gen'

function removeNullValueKeys(obj: { [key: string]: string | null }): {
  [key: string]: string
} {
  return Object.fromEntries(Object.entries(obj).filter(([_, value]) => value !== null)) as {
    [key: string]: string
  }
}

export function getMasteryColorByValue(value: number, masteryLevels: any[]): string {
  const masteryLevel = masteryLevels.find(ml => ml.minValue <= value && ml.maxValue >= value)
  return masteryLevel ? masteryLevel.color : 'black'
}

export function urlStringFrom(
  queryParams: { [key: string]: string | null },
  options?: { path?: string; mode?: string }
): string {
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

export function subjectNamesFromStudentGoals(
  goals: GoalReadable[],
  allSubjects: SubjectReadable[]
): string[] {
  const result = new Set<string>()
  goals.forEach((goal: GoalReadable) => {
    const subject = allSubjects.find((subject: SubjectReadable) => subject.id === goal.subjectId)
    if (subject) {
      result.add(subject.displayName)
    }
  })
  return Array.from(result)
}

export function inferMastery(goal: any): Mastery {
  const firstValue = goal.observations[0]?.masteryValue
  const lastValue = goal.observations[goal.observations.length - 1]?.masteryValue
  return {
    mastery: lastValue || 0,
    trend: lastValue - firstValue,
    title: `${goal.title}: ${lastValue}`,
  }
}

export function findAverage(numbers: number[]): number {
  return numbers.reduce((sum, currentValue) => sum + currentValue, 0) / numbers.length
}
