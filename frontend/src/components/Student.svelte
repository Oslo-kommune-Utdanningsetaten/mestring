<script lang="ts">
  import { dataStore } from '../stores/data'
  import { type GroupReadable, type UserReadable, type GoalReadable } from '../api/types.gen'
  import type { Mastery } from '../types/models'
  import {
    usersRetrieve,
    usersGroupsRetrieve,
    usersGoalsRetrieve,
    observationsList,
  } from '../api/sdk.gen'
  import { urlStringFrom } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import { inferMastery } from '../utils/functions'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let studentGroups = $state<GroupReadable[] | []>([])

  let goalsBySubjectId = $state<Record<string, GoalReadable[]>>({})
  let masterysBySubjectId = $state<Record<string, Mastery[]>>({})

  async function fetchUser(userId: string) {
    try {
      const result = await usersRetrieve({ path: { id: userId } })
      student = result.data!
      fetchGroupsForStudent(student.id)
    } catch (e) {
      console.error(`Could not load student with id ${userId}`, e)
    }
  }

  async function fetchGroupsForStudent(studentId: string) {
    try {
      const result = await usersGroupsRetrieve({
        path: { id: studentId },
        query: { roles: 'student' },
      })
      studentGroups = Array.isArray(result.data) ? result.data : []
    } catch (err) {
      console.error(`Could not load groups for ${studentId}`, err)
      studentGroups = []
    }
  }

  async function calculateMasterysForStudent(studentId: string) {
    const { data: goals, error: goalsFetchError } = await usersGoalsRetrieve({
      path: { id: studentId },
    })
    if (goalsFetchError) {
      console.error(`Error fetching goals for student ${studentId}:`, goalsFetchError)
      return
    }

    goalsBySubjectId = {}
    if (Array.isArray(goals) && goals.length > 0) {
      // We've got all goals for the student, now categorize them by subject
      goals.forEach(async goal => {
        const subjectId = goal.subjectId
        if (!subjectId) {
          console.error(`Goal ${goal.id} has no subjectId!`)
          return
        }
        const goalsOnThisSubject = goalsBySubjectId[subjectId] || []
        goalsOnThisSubject.push(goal)
        goalsBySubjectId = {
          ...goalsBySubjectId,
          [subjectId]: goalsOnThisSubject,
        }
        // Fetch existing observations for each goal
        const { data: observations, error: observationFetchError } = await observationsList({
          query: { goalId: goal.id, studentId: studentId },
        })
        if (observationFetchError) {
          console.error(
            `Error fetching goals for student ${studentId} and goal ${goal.id}:`,
            observationFetchError
          )
          return
        }
        // Create a mastery object for the goal
        let goalMastery = null
        if (Array.isArray(observations) && observations.length > 0) {
          goal.observations = observations
          goalMastery = inferMastery(goal)
        }
        const items = masterysBySubjectId[subjectId] || []
        if (goalMastery !== null) {
          items.push(goalMastery)
          masterysBySubjectId = {
            ...masterysBySubjectId,
            [subjectId]: items,
          }
        }
      })
    }
  }

  $effect(() => {
    if (studentId) {
      fetchUser(studentId)
      calculateMasterysForStudent(studentId)
    }
  })
</script>

<section class="py-3">
  {#if student}
    <h2>{student.name}</h2>
    <!-- Groups -->
    <div class="card shadow-sm">
      <div class="card-header">Grupper</div>
      <div class="card-body">
        {#if studentGroups}
          <ul class="student-info">
            {#each studentGroups as group}
              <li>
                <a
                  href={urlStringFrom(
                    { groupId: group.id },
                    {
                      path: '/students',
                      mode: 'replace',
                    }
                  )}
                >
                  {group.displayName}
                </a>
              </li>
            {/each}
          </ul>
        {:else}
          <div class="alert alert-danger">Ikke medlem av noen grupper</div>
        {/if}
      </div>
    </div>

    <!-- Goals and mastery -->
    <div class="card shadow-sm">
      <div class="card-header">Mål</div>
      <div class="card-body">
        {#if masterysBySubjectId && Object.keys(masterysBySubjectId).length > 0}
          <ul class="student-info">
            {#each Object.keys(masterysBySubjectId) as subjectId}
              <li>
                <strong>{subjectId}</strong>
                {#each masterysBySubjectId[subjectId] as masteryData}
                  <span class="badge-container">
                    <MasteryLevelBadge {masteryData} />
                  </span>
                {/each}
              </li>
            {/each}
          </ul>
        {:else}
          <div class="alert alert-danger">Ingen fag/mål/observasjoner</div>
        {/if}
      </div>
    </div>
  {:else}
    <div class="alert alert-danger">Fant ikke eleven</div>
  {/if}
</section>
