// Data structure types which only exist in the frontend

export interface Mastery {
  mastery: number
  trend: number
  title: string
  groupName: string
}

export interface AppData {
  subjects: SubjectReadable[]
  currentSchool: SchoolReadable | null
  currentUser: BasicUserReadable | null
}
