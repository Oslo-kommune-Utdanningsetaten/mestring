// Data structure types which only exist in the frontend

export type Mastery = {
  mastery: number
  trend: number
  title: string
}

export type AppData = {
  subjects: SubjectType[]
  currentSchool: SchoolType | null
  currentUser: BasicUserType | null
  masterySchemas: MasterySchemaType[]
  defaultMasterySchema?: MasterySchemaType | null
  roles?: RoleType[]
  isSchoolAdmin?: boolean
  isSchoolInspector?: boolean
  isSuperadmin?: boolean
}

export type GoalDecorated = GoalType & {
  masteryData?: Mastery | null
  observations?: ObservationType[]
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
  flatTrendThreshold: number
  isColorGradientEnabled?: boolean
  isIncrementIndicatorEnabled?: boolean
  isValueIndicatorEnabled?: boolean
  isMasteryValueInputEnabled?: boolean
  isMasteryDescriptionInputEnabled?: boolean
  isFeedforwardInputEnabled?: boolean
}

export type MasterySchemaWithConfig = MasterySchemaType & {
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
