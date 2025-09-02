<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-button.js'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type { UserReadable, ObservationReadable } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { observationsDestroy, goalsDestroy, goalsUpdate, goalsList } from '../generated/sdk.gen'
  import { goalsWithCalculatedMasteryBySubjectId } from '../utils/functions'
  import Link from './Link.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import GoalEdit from './GoalEdit.svelte'
  import ObservationEdit from './ObservationEdit.svelte'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import { getLocalStorageItem } from '../stores/localStorage'

  const { subjectId, student } = $props<{ subjectId: string; student: UserReadable }>()

  let goals = $state<GoalDecorated[]>([])
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let goalTitleColumns = $derived(isShowGoalTitleEnabled ? 5 : 2)
  let goalWip = $state<GoalDecorated | null>(null)
  let goalForObservation = $state<GoalDecorated | null>(null)
  let observationWip = $state<ObservationReadable | {} | null>(null)
  let expandedGoals = $state<Record<string, boolean>>({})
  let goalsListElement = $state<HTMLElement | null>(null)

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

  const fetchGoalsForSubject = async () => {
    try {
      const result = await goalsList({ query: { student: student.id, subject: subjectId } })
      const studentGoals = result.data || []
      const goalsBySubjectId = await goalsWithCalculatedMasteryBySubjectId(student.id, studentGoals)
      goals = goalsBySubjectId[subjectId]
    } catch (error) {
      console.error('Error fetching goals:', error)
      goals = []
    }
  }

  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = {
      ...goal,
      subjectId,
      studentId: student.id,
      sortOrder: goal.sortOrder || (goals.length ? goals.length + 1 : 1),
      masterySchemaId:
        goal.masterySchemaId || getLocalStorageItem('preferredMasterySchemaId') || '',
    }
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

  const handleGoalDone = async () => {
    goalForObservation = null
    handleCloseEditGoal()
    await fetchGoalsForSubject()
  }

  const handleObservationDone = async () => {
    handleCloseEditObservation()
    await fetchGoalsForSubject()
  }

  const handleDeleteObservation = async (observationId: string) => {
    try {
      await observationsDestroy({ path: { id: observationId } })
      await fetchGoalsForSubject()
    } catch (error) {
      console.error('Error deleting observation:', error)
    }
  }

  const handleDeleteGoal = async (goalId: string) => {
    try {
      await goalsDestroy({ path: { id: goalId } })
      await fetchGoalsForSubject()
    } catch (error) {
      console.error('Error deleting goal:', error)
    }
  }

  const toggleGoalExpansion = (goalId: string) => {
    expandedGoals[goalId] = !expandedGoals[goalId]
  }

  const handleGoalOrderChange = async (event: SortableEvent) => {
    const { oldIndex, newIndex } = event
    if (oldIndex === undefined || newIndex === undefined) return

    const localGoals = [...goals]
    // Remove moved goal and capture it
    const [movedGoal] = localGoals.splice(oldIndex, 1)
    // Insert moved goal at new index
    localGoals.splice(newIndex, 0, movedGoal)
    // for each goal, update its sortOrder if it has changed
    const updatePromises: Promise<any>[] = []
    localGoals.forEach(async (goal, index) => {
      const newSortOrder = index + 1 // for human readability, sortOrder starts at 1
      if (goal.sortOrder !== newSortOrder) {
        goal.sortOrder = newSortOrder
        updatePromises.push(
          goalsUpdate({
            path: { id: goal.id },
            body: goal,
          })
        )
      }
    })
    try {
      await Promise.all(updatePromises)
    } catch (error) {
      console.error('Error updating goal order:', error)
      // Refetch to restore correct state
      await fetchGoalsForSubject()
    }
  }

  $effect(() => {
    if (!student || !subjectId) return
    fetchGoalsForSubject()
  })

  $effect(() => {
    if (goalsListElement) {
      const sortable = new Sortable(goalsListElement, {
        animation: 150,
        handle: '.row-handle',
        onEnd: handleGoalOrderChange,
      })
    }
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
    title="Legg til nytt personlig mål"
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
    Nytt personlig mål
  </pkt-button>
</div>

{#if goals?.length > 0}
  <div bind:this={goalsListElement} class="list-group">
    {#each goals as goal, index (goal.id)}
      <div class="list-group-item goal-list-item">
        <div class="row d-flex align-items-center">
          <span class="col-1">
            <pkt-icon
              title="Endre rekkefølge"
              class="me-2 row-handle"
              name="drag"
              role="button"
              tabindex="0"
            ></pkt-icon>
            <span>
              {goal.sortOrder || index + 1}
            </span>
          </span>
          <span class="col-md-{goalTitleColumns}">
            {isShowGoalTitleEnabled ? goal.title : '🙊'}
          </span>
          <span class="col-1">
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
          <span class="col-4 d-flex align-items-center gap-3">
            {#if goal.masteryData}
              <MasteryLevelBadge masteryData={goal.masteryData} />
              <SparklineChart
                data={goal.observations?.map((o: ObservationReadable) => o.masteryValue)}
                lineColor="rgb(100, 100, 100)"
                label={goal.title}
              />
            {/if}
          </span>
          <span class="col-1 d-flex justify-content-end pe-4">
            <pkt-button
              size="small"
              skin="tertiary"
              type="button"
              variant="icon-only"
              iconName="chevron-thin-{expandedGoals[goal.id] ? 'up' : 'down'}"
              class="mini-button col-1 rounded"
              title="{expandedGoals[goal.id] ? 'Skjul' : 'Vis'} observasjoner"
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
          </span>
        </div>

        {#if expandedGoals[goal.id]}
          <div>
            {#if goal?.observations.length === 0}
              <div class="alert alert-info my-3">
                {#if goal.isGroup}
                  <div>
                    Dette målet er ikke personlig, men gitt for en hel gruppe. Du finner guppa <Link
                      to={`/groups/${goal.groupId}/`}
                    >
                      her
                    </Link>.
                  </div>
                {:else}
                  <p>Ingen observasjoner for dette målet</p>

                  <pkt-button
                    size="small"
                    skin="primary"
                    variant="icon-left"
                    iconName="edit"
                    class="my-2 me-2"
                    title="Rediger personlig mål"
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
                    Rediger personlig mål
                  </pkt-button>

                  <pkt-button
                    size="small"
                    skin="primary"
                    variant="icon-left"
                    iconName="trash-can"
                    class="my-2"
                    title="Slett personlig mål"
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
                {/if}
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
      </div>
    {/each}
  </div>
{:else}
  <div class="alert alert-info">Ingen mål for {getSubjectName(subjectId)}</div>
{/if}

<svelte:window on:keydown={handleKeydown} />

<!-- offcanvas for creating/editing goals -->
<div class="custom-offcanvas" class:visible={!!goalWip}>
  <GoalEdit {student} goal={goalWip} isGoalPersonal={true} onDone={handleGoalDone} />
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

  h3 {
    font-size: 1.5rem;
  }

  .goal-list-item {
    background-color: var(--bs-light);
    row-gap: 0.5rem;
  }

  .row-handle {
    cursor: move;
    vertical-align: -8%;
  }
</style>
