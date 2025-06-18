// Data structure types which only exist in the frontend

export type Mastery = {
  mastery: number
  trend: number
  title: string
}

export type AppData = {
  subjects: SubjectReadable[]
  currentSchool: SchoolReadable | null
  currentUser: BasicUserReadable | null
  masterySchemas: MasterySchemaReadable[]
}

export type GoalDecorated = GoalReadable & {
  masteryData?: Mastery | null
  observations?: ObservationReadable[]
}

export type MasteryLevel = {
  minValue: number
  maxValue: number
  color: string
  text: string
}

export type MasteryConfigLevel = {
  minValue: number
  maxValue: number
  color: string
  title: string
}

export type MasterySchemaConfig = {
  levels: MasteryConfigLevel[]
  inputIncrement: number
  renderDirection?: 'horizontal' | 'vertical'
  isColorGradientEnabled?: boolean
  isIncrementIndicatorEnabled?: boolean
}
