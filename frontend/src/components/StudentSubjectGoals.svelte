<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type { UserReadable, ObservationReadable } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { usersRetrieve, observationsDestroy, goalsDestroy } from '../generated/sdk.gen'
  import { calculateMasterysForStudent } from '../utils/functions'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import GoalEdit from './GoalEdit.svelte'
  import ObservationEdit from './ObservationEdit.svelte'

  const { subjectId, studentId } = $props<{ subjectId: string; studentId: string }>()

  let student = $state<UserReadable | null>(null)
  let goals = $state<GoalDecorated[]>([])
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let goalTitleColumns = $derived(isShowGoalTitleEnabled ? 5 : 2)
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

  const getSubjectName = (subjectId: string): string => {
    const subject = $dataStore.subjects.find(s => s.id === subjectId)
    return subject ? subject.displayName : 'ukjent'
  }

  const fetchStudent = async () => {
    try {
      const result = await usersRetrieve({ path: { id: studentId } })
      student = result.data!
    } catch (e) {
      console.error(`Could not load student with id ${studentId}`, e)
    }
  }

  const fetchGoalsForSubject = async () => {
    try {
      const goalsBySubjectId = await calculateMasterysForStudent(studentId)
      goals = goalsBySubjectId[subjectId] || []
    } catch (error) {
      console.error('Error fetching goals:', error)
      goals = []
    }
  }

  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = { ...goal, subjectId, studentId }
  }

  const handleCloseEditGoal = () => {
    goalWip = null
  }

  const handleEditObservation = (goal: GoalDecorated, observation: ObservationReadable | null) => {
    observationWip = observation || {}
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
    fetchGoalsForSubject()
  }

  const handleObservationDone = () => {
    handleCloseEditObservation()
    fetchGoalsForSubject()
  }

  const handleDeleteObservation = async (observationId: string) => {
    try {
      await observationsDestroy({ path: { id: observationId } })
      fetchGoalsForSubject()
    } catch (error) {
      console.error('Error deleting observation:', error)
    }
  }

  const handleDeleteGoal = async (goalId: string) => {
    try {
      await goalsDestroy({ path: { id: goalId } })
      fetchGoalsForSubject()
    } catch (error) {
      console.error('Error deleting goal:', error)
    }
  }

  const toggleGoalExpansion = (goalId: string) => {
    expandedGoals[goalId] = !expandedGoals[goalId]
  }

  $effect(() => {
    fetchStudent()
    fetchGoalsForSubject()
  })
</script>

<div class="d-flex align-items-center gap-2 mb-3">
  <h3>
    {getSubjectName(subjectId)}
  </h3>
  <pkt-button
    size="small"
    skin="tertiary"
    type="button"
    variant="icon-only"
    iconName="plus-sign"
    title="Legg til nytt mål"
    class="mini-button bordered"
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
</div>

{#if goals.length > 0}
  {#each goals as goal, index}
    <div class="row d-flex align-items-center border-bottom mb-3">
      <pkt-button
        size="small"
        skin="tertiary"
        type="button"
        variant="icon-only"
        iconName="chevron-thin-{expandedGoals[goal.id] ? 'down' : 'right'}"
        class="mini-button col-1 rounded"
        title="Vis alle observasjoner"
        onclick={() => toggleGoalExpansion(goal.id)}
        onkeydown={(e: any) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            toggleGoalExpansion(goal.id)
          }
        }}
        role="button"
        tabindex="0"
      ></pkt-button>

      <span class="col-1">{goal.sortOrder || 'x'}</span>
      <span class="col-md-{goalTitleColumns}">
        {isShowGoalTitleEnabled ? goal.title : index + 1}
      </span>
      <span class="col-5 d-flex align-items-center gap-3">
        {#if goal.masteryData}
          <MasteryLevelBadge masteryData={goal.masteryData} />
          <SparklineChart
            data={goal.observations?.map((o: ObservationReadable) => o.masteryValue)}
            lineColor="rgb(100, 100, 100)"
            label={goal.title}
          />
        {/if}

        <pkt-button
          size="small"
          skin="tertiary"
          type="button"
          variant="icon-only"
          iconName="plus-sign"
          class="mini-button bordered"
          title="Legg til ny observasjon"
          onclick={() => handleEditObservation(goal, null)}
          onkeydown={(e: any) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              handleEditObservation(goal, null)
            }
          }}
          role="button"
          tabindex="0"
        >
          Ny observasjon
        </pkt-button>
      </span>
    </div>

    {#if expandedGoals[goal.id]}
      <div class="mx-3">
        {#if goal?.observations.length === 0}
          <div class="bg-info p-3">
            <p>Ingen observasjoner for dette målet</p>

            <pkt-button
              size="small"
              skin="primary"
              variant="icon-left"
              iconName="edit"
              class="my-2 me-2"
              onclick={() => handleEditGoal(goal)}
              onkeydown={(e: any) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  handleEditGoal(goal)
                }
              }}
              role="button"
              tabindex="0"
            >
              Rediger mål
            </pkt-button>

            <pkt-button
              size="small"
              skin="primary"
              variant="icon-left"
              iconName="trash-can"
              class="my-2"
              onclick={() => handleDeleteGoal(goal.id)}
              onkeydown={(e: any) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  handleDeleteGoal(goal.id)
                }
              }}
              role="button"
              tabindex="0"
            >
              Slett mål
            </pkt-button>
          </div>
        {:else}
          <div class="row fw-bold d-flex gap-4 mt-2">
            <span class="col-3">Dato</span>
            <span class="col-1">Verdi</span>
            <span class="col-3">Valg</span>
          </div>
          {#each goal?.observations as observation}
            <div class="row d-flex gap-4 pt-2 observation-item">
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
                  onkeydown={(e: any) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      handleEditObservation(goal, observation)
                    }
                  }}
                  role="button"
                  tabindex="0"
                ></pkt-icon>
                <pkt-icon
                  title="Slet observasjon"
                  class="hover-glow me-2"
                  name="trash-can"
                  onclick={() => handleDeleteObservation(observation.id)}
                  onkeydown={(e: any) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      handleDeleteObservation(observation.id)
                    }
                  }}
                  role="button"
                  tabindex="0"
                ></pkt-icon>
              </span>
            </div>
          {/each}
        {/if}
      </div>
    {/if}
  {/each}
{:else}
  <div class="alert alert-info">Ingen mål for {getSubjectName(subjectId)}</div>
{/if}

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
  div.observation-item > span {
    font-family: 'Courier New', Courier, monospace !important;
  }
</style>
