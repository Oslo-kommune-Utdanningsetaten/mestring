import type { Mastery, GoalDecorated } from '../types/models'
import type {
  GoalReadable,
  SubjectReadable,
  ObservationReadable,
  GroupReadable,
  UserReadable,
} from '../generated/types.gen'
import { goalsList, observationsList, groupsList } from '../generated/sdk.gen'
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

// Fetch subjects for the given students to build the grid headers
// based on subjects linked to their goals and groups
export const fetchSubjectsForStudents = async (
  students: UserReadable[],
  allSubjects: SubjectReadable[],
  schoolId: string
): Promise<SubjectReadable[]> => {
  const subjectIds = new Set<string>()

  const data = await Promise.all(
    students.map(async student => {
      const goalsResult = await goalsList({
        query: { student: student.id },
      })
      const goals: GoalReadable[] = goalsResult.data || []
      const groupsResult: any = await groupsList({
        query: { user: student.id, school: schoolId },
      })
      const groups: GroupReadable[] = groupsResult.data || []
      return { goals, groups }
    })
  )

  data.forEach(({ goals, groups }) => {
    goals.forEach(goal => {
      if (goal.subjectId) subjectIds.add(goal.subjectId)
    })
    groups.forEach(group => {
      if (group.subjectId) subjectIds.add(group.subjectId)
    })
  })

  const subjects: SubjectReadable[] = Array.from(subjectIds)
    .map(subjectId => allSubjects.find(s => s.id === subjectId))
    .filter((s): s is SubjectReadable => s !== undefined)

  return subjects
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

export const subjectIdsViaGroupOrGoal = async (
  studentId: string,
  schoolId: string
): Promise<string[]> => {
  const subjectsId: Set<string> = new Set()
  const groupsResult: any = await groupsList({
    query: { user: studentId, school: schoolId },
  })
  const userGroups = groupsResult.data || []
  userGroups.forEach((group: any) => {
    if (group.subjectId && group.type === 'teaching') {
      subjectsId.add(group.subjectId)
    }
  })
  const goalsResult: any = await goalsList({ query: { student: studentId } })
  const userGoals = goalsResult.data || []
  userGoals.forEach((goal: GoalReadable) => {
    if (goal.subjectId) {
      subjectsId.add(goal.subjectId)
    }
  })
  return Array.from(subjectsId)
}

// For a single student, output goals grouped by subjectId, with mastery data calculated
// If a goal does not have a subjectId, look up via the groupId
// Goals are sorted by sortOrder, then personal goals first
export const goalsWithCalculatedMasteryBySubjectId = async (
  studentId: string,
  studentGoals: GoalReadable[],
  groups: GroupReadable[]
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
  goal: GoalReadable,
  observationsForGoal: ObservationReadable[]
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

export const isNumber = (value: any) => {
  return typeof value === 'number'
}

// returns YYYY-MM-DD HH:MM
export const formatDate = (isoDate?: string | null) => {
  if (!isoDate) return ''
  const aDate = new Date(isoDate)
  return (
    aDate.toLocaleDateString('no-NO', { year: '2-digit', month: '2-digit', day: '2-digit' }) +
    ' ' +
    aDate.toLocaleTimeString('no-NO', { hour: '2-digit', minute: '2-digit' })
  )
}
