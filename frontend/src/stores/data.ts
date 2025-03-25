import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'
import type {
  Student,
  Group,
  Teacher,
  Goal,
  Observation,
  MasteryLevel,
  Subject,
  AppData,
} from '../types/models'

// Create a writable store with initial empty values
export const dataStore: Writable<AppData> = writable({
  students: [],
  groups: [],
  teachers: [],
  goals: [],
  observations: [],
  masteryLevels: [],
  subjects: [],
})

// Function to load data from public/data.js
export async function loadData(): Promise<void> {
  try {
    // Dynamic import of the data.js file
    const module = await import('../../public/data.js')
    dataStore.set(module.data)
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

// Helper functions to get specific data
export function getStudentById(id: string): Promise<Student | undefined> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.students.find(student => student.id === id))
    })
  })
}

export function getGroupById(id: string): Promise<Group | undefined> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.groups.find(group => group.id === id))
    })
  })
}

export function getTeacherById(id: string): Promise<Teacher | undefined> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.teachers.find(teacher => teacher.id === id))
    })
  })
}

export function getStudentsByGroupId(groupId: string): Promise<Student[]> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.students.filter(student => student.groupId === groupId))
    })
  })
}

export function getGoalsByStudentId(studentId: string): Promise<Goal[]> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.goals.filter(goal => goal.studentId === studentId))
    })
  })
}

export function getObservationsByGoalId(goalId: string): Promise<Observation[]> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.observations.filter(observation => observation.goalId === goalId))
    })
  })
}

export function getObservationsByStudentId(studentId: string): Promise<Observation[]> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.observations.filter(observation => observation.studentId === studentId))
    })
  })
}

export function getMasteryLevelByValue(value: number): Promise<MasteryLevel | undefined> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.masteryLevels.find(level => value >= level.minValue && value <= level.maxValue))
    })
  })
}

export function getSubjectById(id: string): Promise<Subject | undefined> {
  return new Promise(resolve => {
    const unsubscribe = dataStore.subscribe(data => {
      unsubscribe()
      resolve(data.subjects.find(subject => subject.id === id))
    })
  })
}

// Load data when this module is imported
loadData()
