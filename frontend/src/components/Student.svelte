<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import { dataStore } from '../stores/data'
  import type { GroupReadable, UserReadable, ObservationReadable } from '../api/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { usersRetrieve, usersGroupsRetrieve, goalsCreate, goalsUpdate } from '../api/sdk.gen'

  import { urlStringFrom, calculateMasterysForStudent } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import GoalEdit from './GoalEdit.svelte'
  import { slide } from 'svelte/transition'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let studentGroups = $state<GroupReadable[] | []>([])

  let goalsBySubjectId = $state<Record<string, GoalDecorated[]>>({})
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let goalWip = $state<GoalDecorated | null>(null)
  let goalTitleColumns = $derived(isShowGoalTitleEnabled ? 5 : 2)

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

  function getSubjectName(subjectId: string): string {
    const subject = $dataStore.subjects.find(s => s.id === subjectId)
    return subject ? subject.displayName : 'ukjent'
  }

  function handleEditGoal(goal: Goal | null) {
    goalWip = goal || {}
  }

  function handleCloseEditGoal() {
    goalWip = null
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && goalWip) {
      handleCloseEditGoal()
    }
  }

  async function handleSaveGoal(goal: any) {
    console.log('Saving goal:', goal)
    try {
      if (goal.id) {
        // Update existing goal
        const result = await goalsUpdate({
          path: { id: goal.id },
          body: goal,
        })
        console.log('Goal updated:', result.data)
      } else {
        // Create new goal
        const result = await goalsCreate({
          body: goal,
        })
        console.log('Goal created:', result.data)
      }

      // Close the edit modal
      handleCloseEditGoal()

      // Refresh the goals data
      if (studentId) {
        calculateMasterysForStudent(studentId).then(result => {
          goalsBySubjectId = result
        })
      }
    } catch (error) {
      console.error('Error saving goal:', error)
      // You might want to show an error message to the user here
    }
  }

  $effect(() => {
    if (studentId) {
      fetchUser(studentId)
      calculateMasterysForStudent(studentId).then(result => {
        goalsBySubjectId = result
      })
    }
  })
</script>

<section class="py-3">
  {#if student}
    <h2>Elev: {student.name}</h2>
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
      <div class="card-header">Mål</div>
      <pkt-button
        size="small"
        skin="primary"
        type="button"
        variant="label-only"
        class="m-2"
        onclick={() => handleEditGoal(null)}
        onkeydown={(e: any) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            handleEditGoal(null)
          }
        }}
        role="button"
        tabindex="0"
      >
        Nytt mål
      </pkt-button>

      {#if goalsBySubjectId && Object.keys(goalsBySubjectId).length > 0}
        <div class="pkt-input-check ms-2">
          <div class="pkt-input-check__input">
            <input
              class="pkt-input-check__input-checkbox"
              type="checkbox"
              role="switch"
              id="goalTitleSwitch"
              bind:checked={isShowGoalTitleEnabled}
              style="transform: scale(0.8);"
            />
            <label class="pkt-input-check__input-label" for="goalTitleSwitch">
              Vis mål som anonyme
            </label>
          </div>
        </div>
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
                      {#if goal.masteryData}
                        <div class="d-flex align-items-center gap-3">
                          <MasteryLevelBadge masteryData={goal.masteryData} />
                          <SparklineChart
                            data={goal.observations?.map(
                              (o: ObservationReadable) => o.masteryValue
                            )}
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
        <div class="alert alert-info">Ingen mål</div>
      {/if}
    </div>
  {:else}
    <div class="alert alert-danger">Fant ikke eleven</div>
  {/if}
</section>

<svelte:window on:keydown={handleKeydown} />

<!-- offcanvas for creating/editing goals -->
<div class="custom-offcanvas shadow-sm" class:visible={!!goalWip}>
  <GoalEdit {student} goal={goalWip} onSave={handleSaveGoal} onCancel={handleCloseEditGoal} />
</div>

<style>
  .custom-offcanvas {
    position: fixed;
    right: -50vw;
    top: 0;
    height: 100vh;
    width: 50vw;
    background: white;
    z-index: 1050;
    border: 2px solid var(--bs-primary);
    transition: right 0.22s ease-in-out;
    pointer-events: none;
  }

  .custom-offcanvas.visible {
    right: 0;
    pointer-events: all;
  }
</style>
