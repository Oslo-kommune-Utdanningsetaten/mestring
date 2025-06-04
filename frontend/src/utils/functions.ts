import type { Mastery, GoalDecorated } from '../types/models'
import { type GoalReadable, type SubjectReadable } from '../api/types.gen'
import { usersGoalsRetrieve, observationsList } from '../api/sdk.gen'

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

export async function calculateMasterysForStudent(studentId: string) {
  const { data: goals, error: goalsFetchError } = await usersGoalsRetrieve({
    path: { id: studentId },
  })
  if (goalsFetchError) {
    console.error(`Error fetching goals for student ${studentId}:`, goalsFetchError)
    return {}
  }

  let goalsBySubjectId: Record<string, GoalDecorated[]> = {}

  if (Array.isArray(goals) && goals.length > 0) {
    await Promise.all(
      goals.map(async goal => {
        const subjectId = goal.subjectId
        if (!subjectId) {
          console.error(`Goal ${goal.id} has no subjectId!`)
          return
        }

        // Fetch existing observations for each goal
        const { data: observations, error: observationFetchError } = await observationsList({
          query: { goalId: goal.id, studentId: studentId },
        })
        if (observationFetchError) {
          console.error(
            `Error fetching goals for student ${studentId} and goal ${goal.id}:`,
            observationFetchError
          )
          return
        }

        // Create a decorated goal first
        const decoratedGoal: GoalDecorated = { ...goal }
        // Add observations and mastery if they exist
        if (Array.isArray(observations) && observations.length > 0) {
          decoratedGoal.observations = observations
          decoratedGoal.mastery = inferMastery(decoratedGoal)
        }

        // Always add the goal, even without observations
        const goalsOnThisSubject = goalsBySubjectId[subjectId] || []
        goalsOnThisSubject.push(decoratedGoal)
        goalsBySubjectId = {
          ...goalsBySubjectId,
          [subjectId]: goalsOnThisSubject,
        }
      })
    )
  }
  return goalsBySubjectId
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
