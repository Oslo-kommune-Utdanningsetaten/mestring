<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type { GroupReadable, UserReadable, ObservationReadable } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import {
    usersRetrieve,
    usersGroupsRetrieve,
    observationsDestroy,
    goalsDestroy,
  } from '../generated/sdk.gen'
  import { urlStringFrom, calculateMasterysForStudent } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import GoalEdit from './GoalEdit.svelte'
  import ObservationEdit from './ObservationEdit.svelte'

  const { studentId } = $props<{ studentId: string }>()
  let student = $state<UserReadable | null>(null)
  let studentGroups = $state<GroupReadable[] | []>([])

  let goalsBySubjectId = $state<Record<string, GoalDecorated>>({})
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let isShowGoalTitleToggleVisible = $state<boolean>(true)
  let goalTitleColumns = $derived(isShowGoalTitleEnabled ? 6 : 2)
  let goalWip = $state<GoalDecorated | null>(null)
  let goalForObservation = $state<GoalDecorated | null>(null)
  let observationWip = $state<ObservationReadable | {} | null>(null)
  let expandedGoals = $state<Record<string, boolean>>({})

  const dateFormat = Intl.DateTimeFormat('nb', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return dateFormat.format(date)
  }

  const fetchUser = async (userId: string) => {
    try {
      const result = await usersRetrieve({ path: { id: userId } })
      student = result.data!
      fetchGroupsForStudent(student.id)
    } catch (e) {
      console.error(`Could not load student with id ${userId}`, e)
    }
  }

  const fetchGroupsForStudent = async (studentId: string) => {
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

  const getSubjectName = (subjectId: string): string => {
    const subject = $dataStore.subjects.find(s => s.id === subjectId)
    return subject ? subject.displayName : 'ukjent'
  }

  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = { ...goal }
  }

  const handleCloseEditGoal = () => {
    goalWip = null
  }

  const handleEditObservation = (goal: GoalDecorated, observation: ObservationReadable | null) => {
    console.log('Editing observation for goal:', goal)
    observationWip = observation || {}
    console.log('Observation:', observationWip)
    goalForObservation = { ...goal }
  }

  const handleCloseEditObservation = () => {
    observationWip = null
  }

  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      if (goalWip) {
        handleCloseEditGoal()
      } else if (observationWip) {
        handleCloseEditObservation()
      }
    }
  }

  const handleGoalDone = () => {
    goalForObservation = null
    handleCloseEditGoal()
    if (studentId) {
      calculateMasterysForStudent(studentId).then(result => {
        goalsBySubjectId = result
      })
    }
  }

  const handleObservationDone = () => {
    handleCloseEditObservation()
    if (studentId) {
      calculateMasterysForStudent(studentId).then(result => {
        goalsBySubjectId = result
      })
    }
  }

  const handleDeleteObservation = async (observationId: string) => {
    try {
      await observationsDestroy({ path: { id: observationId } })
      // Refresh after deletion
      if (studentId) {
        calculateMasterysForStudent(studentId).then(result => {
          goalsBySubjectId = result
        })
      }
    } catch (error) {
      console.error('Error deleting observation:', error)
    }
  }

  const handleDeleteGoal = async (goalId: string) => {
    try {
      await goalsDestroy({ path: { id: goalId } })
      // Refresh after deletion
      if (studentId) {
        calculateMasterysForStudent(studentId).then(result => {
          goalsBySubjectId = result
        })
      }
    } catch (error) {
      console.error('Error deleting goal:', error)
    }
  }

  const toggleGoalExpansion = (goalId: string) => {
    expandedGoals[goalId] = !expandedGoals[goalId]
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
        {#if isShowGoalTitleToggleVisible}
          <div class="pkt-input-check m-2">
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
                Vis tittel på mål
              </label>
            </div>
          </div>
        {/if}
        <ul class="list-group list-group-flush">
          {#each Object.keys(goalsBySubjectId) as subjectId}
            <li class="list-group-item py-3">
              <h6>{getSubjectName(subjectId)}</h6>
              <ol>
                {#each goalsBySubjectId[subjectId] as goal, index}
                  <li class="row">
                    <div class="col-md-{goalTitleColumns} d-flex align-items-center">
                      <pkt-icon
                        title="Vis alle observasjoner"
                        class="hover-glow me-2"
                        name="chevron-thin-{expandedGoals[goal.id] ? 'down' : 'right'}"
                        onclick={() => toggleGoalExpansion(goal.id)}
                      ></pkt-icon>
                      <span>
                        {#if isShowGoalTitleEnabled}
                          Mål {index + 1}: {goal.title}
                        {:else}
                          Mål {index + 1}
                        {/if}
                      </span>
                    </div>
                    <div class="col-md-{12 - goalTitleColumns} d-flex align-items-center gap-3">
                      {#if goal.masteryData}
                        <MasteryLevelBadge masteryData={goal.masteryData} />
                        <SparklineChart
                          data={goal.observations?.map((o: ObservationReadable) => o.masteryValue)}
                          lineColor="rgb(100, 100, 100)"
                          label={goal.title}
                        />
                      {:else}
                        <pkt-icon
                          title="Rediger mål"
                          class="hover-glow me-2"
                          name="edit"
                          onclick={() => handleEditGoal(goal)}
                        ></pkt-icon>
                        <pkt-icon
                          title="Slett mål"
                          class="hover-glow me-2"
                          name="trash-can"
                          onclick={() => handleDeleteGoal(goal.id)}
                        ></pkt-icon>
                      {/if}

                      <pkt-icon
                        title="Ny observasjon"
                        class="hover-glow me-2"
                        name="plus-sign"
                        onclick={() => handleEditObservation(goal, null)}
                      ></pkt-icon>
                    </div>
                    {#if expandedGoals[goal.id]}
                      <div class="p-2 me-5 px-3">
                        {#if goal?.observations.length === 0}
                          Ingen observasjoner for dette målet
                        {:else}
                          <div class="row border-bottom border-dashed fw-bold d-flex gap-4">
                            <span class="col-3">Dato</span>
                            <span class="col-1">Verdi</span>
                            <span class="col-3">Handlinger</span>
                          </div>
                          {#each goal?.observations as observation}
                            <div class="row border-bottom border-dashed d-flex gap-4">
                              <span class="col-3">
                                {formatDate(observation.observedAt)}
                              </span>
                              <span class="col-1 d-flex justify-content-end pe-4">
                                {observation.masteryValue}
                              </span>
                              <span class="col-3">
                                <pkt-icon
                                  title="Rediger observasjon"
                                  class="hover-glow me-2"
                                  name="edit"
                                  onclick={() => handleEditObservation(goal, observation)}
                                ></pkt-icon>
                                <pkt-icon
                                  title="Slet observasjon"
                                  class="hover-glow me-2"
                                  name="trash-can"
                                  onclick={() => handleDeleteObservation(observation.id)}
                                ></pkt-icon>
                              </span>
                            </div>
                          {/each}
                        {/if}
                      </div>
                    {/if}
                  </li>
                {/each}
              </ol>
            </li>
          {/each}
        </ul>
      {:else}
        <div class="alert alert-info m-2">Ingen mål for denne eleven</div>
      {/if}
    </div>
  {:else}
    <div class="m-2">Fant ikke eleven</div>
  {/if}
</section>

<svelte:window on:keydown={handleKeydown} />

<!-- offcanvas for creating/editing goals -->
<div class="custom-offcanvas" class:visible={!!goalWip}>
  <GoalEdit {student} goal={goalWip} onDone={handleGoalDone} />
</div>

<!-- offcanvas for adding an observation -->
<div class="custom-offcanvas" class:visible={!!observationWip}>
  <ObservationEdit
    {student}
    observation={observationWip}
    goal={goalForObservation}
    onDone={handleObservationDone}
  />
</div>

<style>
</style>
