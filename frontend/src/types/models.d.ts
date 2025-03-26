// Data structure types
export interface Student {
  id: string
  name: string
  age: number
  groupId: string
  goalIds: string[]
  subjectIds: string[]
}

export interface Group {
  id: string
  name: string
  grade: number
  section: string
  teacherId: string
}

export interface Teacher {
  id: string
  name: string
  groupIds: string[]
}

export interface Goal {
  id: string
  title: string
  description: string
  subjectId: string
  studentId: string
  observationIds: string[]
}

export interface Observation {
  id: string
  date: string
  masteryValue: number
  subjectId: string
  goalId: string
  studentId: string
}

export interface MasteryLevel {
  text: string
  minValue: number
  maxValue: number
  color: string
}

export interface Subject {
  id: string
  name: string
}

export interface AppData {
  students: Student[]
  groups: Group[]
  teachers: Teacher[]
  goals: Goal[]
  observations: Observation[]
  masteryLevels: MasteryLevel[]
  subjects: Subject[]
}
