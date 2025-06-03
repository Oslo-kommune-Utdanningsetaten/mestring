<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import { usersGoalsRetrieve, observationsList } from '../api/sdk.gen'
  import type { Mastery } from '../types/models'
  import type { GoalReadable, SubjectReadable } from '../api/types.gen'
  import { inferMastery } from '../utils/functions'

  const router = useTinyRouter()

  let { student, subjectsById } = $props()
  let goalsBySubjectId = $state<Record<string, GoalReadable[]>>({})
  let masterysBySubjectId = $state<Record<string, Mastery[] | null>>({})

  async function calculateMasteryForSubjects(subjectsById: Record<string, SubjectReadable>) {
    const result = {}
    Object.keys(subjectsById).forEach(async subjectId => {
      // fetch all goals for the student in the current subject
      const { data: goals, error: goalsFetchError } = await usersGoalsRetrieve({
        path: { id: student.id },
        query: { subjectId: subjectId },
      })
      if (goalsFetchError) {
        console.error(
          `Error fetching goals for student ${student.id} in subject ${subjectId}:`,
          goalsFetchError
        )
        return
      }
      if (Array.isArray(goals) && goals.length > 0) {
        goalsBySubjectId = {
          ...goalsBySubjectId,
          [subjectId]: goals,
        }
        goals.forEach(async goal => {
          const { data: observations, error: observationFetchError } = await observationsList({
            query: { goalId: goal.id, studentId: student.id },
          })
          if (observationFetchError) {
            console.error(
              `Error fetching observations for goal ${goal.id} in subject ${subjectId}:`,
              observationFetchError
            )
            return
          }
          let goalMastery = null
          if (Array.isArray(observations) && observations.length > 0) {
            goal.observations = observations
            goalMastery = inferMastery(goal)
          }
          const masteryElements = masterysBySubjectId[subjectId] || []
          if (goalMastery !== null) {
            masteryElements.push(goalMastery)
            masterysBySubjectId = {
              ...masterysBySubjectId,
              [subjectId]: masteryElements,
            }
          }
        })
      }
    })
  }

  $effect(() => {
    calculateMasteryForSubjects(subjectsById)
  })
</script>

<div class="student-grid-row">
  <a href={`/students/${student.id}`} class="fw-bold">{student.name}</a>

  <div class="group-grid-columns">
    {#each Object.entries(subjectsById) as [subjectId, subject]}
      <span class="group-grid-column">{subjectId}</span>
    {/each}
  </div>
</div>

<style>
</style>
