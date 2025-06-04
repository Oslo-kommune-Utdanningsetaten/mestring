// Data structure types which only exist in the frontend

export interface Mastery {
  mastery: number
  trend: number
  title: string
}

export interface AppData {
  subjects: SubjectReadable[]
  currentSchool: SchoolReadable | null
  currentUser: BasicUserReadable | null
}

export interface GoalDecorated extends GoalReadable {
  masteryData?: Mastery
  observations?: ObservationReadable[]
  title: string // why do i need to specify this when it exists on GoalReadable?
}
