<script lang="ts">
  import { dataStore } from '../stores/data'
  import type {
    GroupReadable,
    UserReadable,
    GoalReadable,
    ObservationReadable,
  } from '../api/types.gen'
  import type { Mastery } from '../types/models'
  import {
    usersRetrieve,
    usersGroupsRetrieve,
    usersGoalsRetrieve,
    observationsList,
  } from '../api/sdk.gen'
  import { urlStringFrom, inferMastery } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparklineChart from './SparklineChart.svelte'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let studentGroups = $state<GroupReadable[] | []>([])

  let goalsBySubjectId = $state<Record<string, GoalReadable[]>>({})
  let masteryByGoalId = $state<Record<string, Mastery>>({})
  let isShowGoalTitleEnabled = $state<boolean>(false)
  let goalTitleColumns = $derived(isShowGoalTitleEnabled ? 5 : 1)

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
        if (Array.isArray(observations) && observations.length > 0) {
          goal.observations = observations
          masteryByGoalId[goal.id] = inferMastery(goal)
        }

        const goalsOnThisSubject = goalsBySubjectId[subjectId] || []
        goalsOnThisSubject.push(goal)
        goalsBySubjectId = {
          ...goalsBySubjectId,
          [subjectId]: goalsOnThisSubject,
        }
      })
    }
  }

  function getSubjectName(subjectId: string): string {
    const subject = $dataStore.subjects.find(s => s.id === subjectId)
    return subject ? subject.displayName : 'ukjent'
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
          <ul class="mb-0">
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
      <div class="card-header">
        Mål <div class="pkt-input-check">
          <div class="pkt-input-check__input">
            <input
              class="pkt-input-check__input-checkbox"
              type="checkbox"
              role="switch"
              id="goalTitleSwitch"
              bind:checked={isShowGoalTitleEnabled}
              style="transform: scale(0.8);"
            />
            <label class="pkt-input-check__input-label" for="goalTitleSwitch">Vis tittel</label>
          </div>
        </div>
      </div>
      {#if goalsBySubjectId && Object.keys(goalsBySubjectId).length > 0}
        <ul class="list-group list-group-flush">
          {#each Object.keys(goalsBySubjectId) as subjectId}
            <li class="list-group-item">
              <h6>{getSubjectName(subjectId)}</h6>
              <ol>
                {#each goalsBySubjectId[subjectId] as goal, index}
                  <li class="row">
                    <div class="col-md-{goalTitleColumns}">
                      {#if isShowGoalTitleEnabled}
                        Mål {index + 1}: {goal.title}
                      {:else}
                        Mål {index + 1}
                      {/if}
                    </div>
                    <div class="col-md-{12 - goalTitleColumns}">
                      {#if masteryByGoalId[goal.id]}
                        <div class="d-flex align-items-center gap-2">
                          <MasteryLevelBadge masteryData={masteryByGoalId[goal.id]} />
                          <SparklineChart
                            data={(
                              goal as GoalReadable & { observations: ObservationReadable[] }
                            ).observations.map((o: ObservationReadable) => o.masteryValue)}
                            lineColor="rgb(100, 100, 100)"
                            label={goal.title}
                          />
                        </div>
                      {:else}
                        <span>ingen observasjoner</span>
                      {/if}
                    </div>
                  </li>
                {/each}
              </ol>
            </li>
          {/each}
        </ul>
      {:else}
        <div class="alert alert-danger">Ingen fag/mål/observasjoner</div>
      {/if}
    </div>
  {:else}
    <div class="alert alert-danger">Fant ikke eleven</div>
  {/if}
</section>

<style>
</style>
