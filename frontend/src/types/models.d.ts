// Data structure types which only exist in the frontend
export type deploymentEnvironment = 'localhost' | 'development' | 'production'

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
  hasUserAccessToPath: (path: string) => boolean
  hasUserAccessToFeature: (
    resource: string,
    action: string,
    options?: HasUserAccessToFeatureOptions
  ) => boolean
  roles: RoleType[]
  defaultMasterySchema?: MasterySchemaType | null
}

export type HasUserAccessToFeatureOptions = {
  subjectId?: string
  studentId?: string
  studentGroupIds?: string[]
  groupId?: string | null
  createdById?: string
}

export type GoalDecorated = GoalType & {
  masteryData?: Mastery | null
  observations?: ObservationType[]
}

export type UserDecorated = UserType & {
  allGroups?: GroupType[]
  teacherGroups?: GroupType[]
  studentGroups?: GroupType[]
  userSchools?: NestedUserSchoolType[]
  schools?: SchoolType[]
  isSchoolAdmin?: boolean
  isSchoolInspector?: boolean
  isSuperadmin?: boolean
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
    fetchedCount: number | undefined
    fetchedAt: string | undefined
    dbCount: number | undefined
    diff: number | undefined
  }
  users: {
    fetchedCount: number | undefined
    fetchedAt: string | undefined
    dbCount: number | undefined
    diff: number | undefined
  }
  memberships: {
    fetchedCount: number | undefined
    fetchedAt: string | undefined
    dbCount: number | undefined
    diff: number | undefined
  }
  lastImportAt: string | undefined
  lastCleanupAt: string | undefined
}
