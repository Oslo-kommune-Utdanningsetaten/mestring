// Data structure types
export interface Student {
  id: string
  name: string
  age: number
  goalIds: string[]
  groupIds: string[]
}

export interface Group {
  id: string
  name: string
  type: string
  grade?: number
  section?: string
  teacherIds?: string[]
}

export interface Teacher {
  id: string
  name: string
}

export interface Goal {
  id: string
  title: string
  description: string
  groupId: string
  studentId: string
}

export interface Observation {
  id: string
  createdAt: string
  masteryValue: number
  groupId: string
  goalId: string
  studentId: string
}

export interface MasteryLevel {
  text: string
  minValue: number
  maxValue: number
  color: string
}

export interface AppData {
  students: Student[]
  groups: Group[]
  teachers: Teacher[]
  goals: Goal[]
  observations: Observation[]
  masteryLevels: MasteryLevel[]
}
