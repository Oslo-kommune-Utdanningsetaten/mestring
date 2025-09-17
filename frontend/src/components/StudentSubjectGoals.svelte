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
  import GroupSVG from '../assets/group.svg.svelte'
  import PersonSVG from '../assets/person.svg.svelte'
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
  let subject = $derived($dataStore.subjects.find(s => s.id === subjectId) || null)

  const dateFormat = Intl.DateTimeFormat('nb', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return dateFormat.format(date)
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

  // Remember, we're only editing personal goals here
  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = {
      ...goal,
      subjectId,
      studentId: student.id,
      sortOrder: goal?.sortOrder || (goals?.length ? goals.length + 1 : 1),
      masterySchemaId:
        goal?.masterySchemaId || getLocalStorageItem('preferredMasterySchemaId') || '',
    }
  }

  const handleCloseEditGoal = () => {
    goalWip = null
  }

  const handleEditObservation = (goal: GoalDecorated, observation: ObservationReadable | null) => {
    if (observation) {
      // edit observation
      observationWip = observation
    } else {
      // create new observation, prefill with value from previous observation
      const prevousObservations = goal?.observations || []
      const previousObservation = prevousObservations[prevousObservations.length - 1]
      observationWip = { masteryValue: previousObservation?.masteryValue || null }
    }
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
    if (student && subjectId) {
      fetchGoalsForSubject()
    }
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
    {subject ? subject.displayName : 'Ukjent'}
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

{#if !goals?.length}
  <div class="alert alert-info">
    Trykk pluss (+) for å opprette et personlig mål for eleven i dette faget.
  </div>
{:else}
  <div bind:this={goalsListElement} class="list-group">
    {#each goals as goal, index (goal.id)}
      <div class="list-group-item goal-item">
        <div class="goal-primary-row">
          <!-- Drag handle -->
          <span>
            <pkt-icon
              title="Endre rekkefølge"
              class="me-2 row-handle"
              name="drag"
              role="button"
              tabindex="0"
            ></pkt-icon>
          </span>
          <!-- Goal order -->
          <span>
            {goal.sortOrder || index + 1}
          </span>
          <!-- Goal type icon -->
          <span class="goal-type-icon">
            {#if goal.isGroup}
              <GroupSVG />
            {:else}
              <PersonSVG />
            {/if}
          </span>
          <!-- Goal title -->
          <span>
            {isShowGoalTitleEnabled ? goal.title : '🙊'}
          </span>
          <!-- New observation button -->
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
          <!-- Stats widgets -->
          <span class="d-flex align-items-center gap-3">
            {#if goal.masteryData}
              <MasteryLevelBadge masteryData={goal.masteryData} />
              <SparklineChart
                data={goal.observations?.map((o: ObservationReadable) => o.masteryValue)}
                lineColor="rgb(100, 100, 100)"
                label={goal.title}
              />
            {/if}
          </span>
          <!-- Expand goal info -->
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
        </div>

        {#if expandedGoals[goal.id]}
          <div class="goal-secondary-row">
            {#if goal?.observations.length === 0}
              <div class="my-3">
                {#if goal.isGroup}
                  <div>
                    Dette målet er ikke personlig, men gitt for en hel gruppe. Du finner guppa <Link
                      to={`/groups/${goal.groupId}/`}
                    >
                      her
                    </Link>.
                  </div>
                {:else}
                  <p>
                    Ingen observasjoner for dette målet. Trykk pluss (+) for å opprette en
                    observasjon.
                  </p>

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
                <span class="col-3">Handlinger</span>
              </div>
              {#each goal?.observations as observation, index}
                <div class="row d-flex gap-4 pt-2 observation-item">
                  <span class="col-3">
                    {formatDate(observation.observedAt)}
                  </span>
                  <span class="col-1 d-flex justify-content-end pe-4">
                    {observation.masteryValue}
                  </span>
                  <span class="col-3">
                    <pkt-icon
                      title="Slett observasjon"
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
                    {#if index === goal?.observations.length - 1}
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
                    {/if}
                  </span>
                </div>
              {/each}
            {/if}
          </div>
        {/if}
      </div>
    {/each}
  </div>
{/if}

<svelte:window on:keydown={handleKeydown} />

<!-- offcanvas for creating/editing goals -->
<div class="custom-offcanvas" class:visible={!!goalWip}>
  <GoalEdit goal={goalWip} {student} {subject} isGoalPersonal={true} onDone={handleGoalDone} />
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

  .goal-item {
    background-color: var(--bs-light);
  }

  .goal-primary-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 10fr 1fr 2fr 1fr;
    column-gap: 5px;
  }

  .goal-primary-row > :last-child {
    justify-self: end; /* aligns last column's content */
    padding-right: 20px;
  }

  .goal-secondary-row {
    margin-top: 10px;
    margin-left: 6px;
    padding-left: 30px;
    border-left: 3px solid var(--bs-secondary);
  }

  .row-handle {
    cursor: move;
    vertical-align: -8%;
  }

  .goal-type-icon > :global(svg) {
    height: 1.2em;
  }
</style>
