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
  roles?: RoleReadable[]
  isSchooladmin?: boolean
  isSuperadmin?: boolean
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
  isTitleInputEnabled?: boolean
  isMasteryValueInputEnabled?: boolean
  isMasteryDescriptionInputEnabled?: boolean
  isFeedforwardInputEnabled?: boolean
}

export type MasterySchemaWithConfig = MasterySchemaReadable & {
  config?: MasterySchemaConfig
}

export type SchoolImportStatus = {
  groups: {
    fetchedCount: number | null
    fetchedAt: string | null
    dbCount: number | null
    diff: number | null
  }
  users: {
    fetchedCount: number | null
    fetchedAt: string | null
    dbCount: number | null
    diff: number | null
  }
  memberships: {
    fetchedCount: number | null
    fetchedAt: string | null
    dbCount: number | null
    diff: number | null
  }
  lastImportAt: string | null
}
