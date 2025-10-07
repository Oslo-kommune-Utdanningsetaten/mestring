<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type { UserReadable, ObservationReadable, GoalReadable } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import {
    observationsDestroy,
    goalsDestroy,
    goalsUpdate,
    goalsList,
    groupsList,
  } from '../generated/sdk.gen'
  import { goalsWithCalculatedMasteryBySubjectId } from '../utils/functions'
  import Link from './Link.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import GoalEdit from './GoalEdit.svelte'
  import ObservationEdit from './ObservationEdit.svelte'
  import GroupSVG from '../assets/group.svg.svelte'
  import PersonSVG from '../assets/person.svg.svelte'
  import ButtonMini from './ButtonMini.svelte'
  import Offcanvas from './Offcanvas.svelte'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import { getLocalStorageItem } from '../stores/localStorage'

  const { subjectId, student } = $props<{ subjectId: string; student: UserReadable }>()

  let goalsForSubject = $state<GoalDecorated[]>([])
  let sortableInstance: Sortable | null = null
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let goalWip = $state<GoalDecorated | null>(null)
  let goalForObservation = $state<GoalDecorated | null>(null)
  let observationWip = $state<ObservationReadable | {} | null>(null)
  let expandedGoals = $state<Record<string, boolean>>({})
  let goalsListElement = $state<HTMLElement | null>(null)
  let subject = $derived($dataStore.subjects.find(s => s.id === subjectId) || null)
  let isGoalEditorOpen = $state<boolean>(false)
  let isObservationEditorOpen = $state<boolean>(false)

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
      const goalsResult = await goalsList({ query: { student: student.id, subject: subjectId } })
      //const studentGoals = (goalsResult.data || []).filter(g => g.isPersonal)
      const goals = goalsResult.data || []
      const groupIds = goals.map(goal => goal.groupId).filter(Boolean) as string[]
      const groupsResult = await groupsList({
        query: { ids: groupIds.join(','), school: $dataStore.currentSchool.id },
      })
      const groups = groupsResult.data || []
      const goalsBySubjectId = await goalsWithCalculatedMasteryBySubjectId(
        student.id,
        goals,
        groups
      )
      goalsForSubject = goalsBySubjectId[subjectId]
    } catch (error) {
      console.error('Error fetching goals:', error)
      goalsForSubject = []
    }
  }

  // Remember, we're only editing personal goals here
  const handleEditGoal = (goal: GoalDecorated | null) => {
    goalWip = {
      ...goal,
      subjectId,
      studentId: student.id,
      sortOrder: goal?.sortOrder || (goalsForSubject?.length ? goalsForSubject.length + 1 : 1),
      masterySchemaId:
        goal?.masterySchemaId || getLocalStorageItem('preferredMasterySchemaId') || '',
    }
    isGoalEditorOpen = true
  }

  const handleCloseEditGoal = () => {
    isGoalEditorOpen = false
    // Don't clear goalWip here - let onClosed handle it after animation
  }

  const handleEditObservation = (goal: GoalDecorated, observation: ObservationReadable | null) => {
    if (observation?.id) {
      // edit existing observation
      observationWip = observation
    } else {
      // create new observation, prefill with value from previous observation
      const prevousObservations = goal?.observations || []
      const previousObservation = prevousObservations[prevousObservations.length - 1]
      observationWip = { masteryValue: previousObservation?.masteryValue || null }
    }
    goalForObservation = { ...goal }
    isObservationEditorOpen = true
  }

  const handleCloseEditObservation = () => {
    isObservationEditorOpen = false
    // Don't clear observationWip here - let onClosed handle it after animation
  }

  const handleGoalDone = async () => {
    goalForObservation = null
    handleCloseEditGoal()
    // fetchGoalsForSubject will be called in onClosed
  }

  const handleObservationDone = async () => {
    handleCloseEditObservation()
    // fetchGoalsForSubject will be called in onClosed
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

    const localGoals = [...goalsForSubject.filter(g => g.isPersonal)] // only personal goals are draggable
    // Remove moved goal and capture it
    const [movedGoal] = localGoals.splice(oldIndex, 1)
    // Insert moved goal at new index
    localGoals.splice(newIndex, 0, movedGoal)
    // update sortOrder for each goal that has changed position
    const updatePromises: Promise<any>[] = localGoals.map(async (goal, index) => {
      const newSortOrder = index + 1 // sortOrder starts at 1
      if (goal.sortOrder !== newSortOrder) {
        goal.sortOrder = newSortOrder
        return goalsUpdate({
          path: { id: goal.id },
          body: goal,
        })
      } else {
        return Promise.resolve() // no update needed
      }
    })
    try {
      await Promise.all(updatePromises)
    } catch (error) {
      console.error('Error updating goal order:', error)
    } finally {
      await fetchGoalsForSubject()
    }
  }

  $effect(() => {
    if (student && subjectId) {
      fetchGoalsForSubject()
    }
  })

  $effect(() => {
    if (goalsListElement && !sortableInstance) {
      sortableInstance = new Sortable(goalsListElement, {
        animation: 150,
        handle: '.row-handle-draggable',
        onEnd: handleGoalOrderChange,
      })
    }
    return () => {
      // clean up if element unmounts
      if (!goalsListElement && sortableInstance) {
        sortableInstance.destroy()
        sortableInstance = null
      }
    }
  })
</script>

<div class="d-flex align-items-center gap-2 mb-3">
  <h3>
    {subject ? subject.displayName : 'Ukjent'}
  </h3>
  <ButtonMini
    options={{
      iconName: 'plus-sign',
      classes: 'mini-button bordered',
      title: 'Legg til nytt personlig mål',
      onClick: () => handleEditGoal(null),
    }}
  />
</div>

{#snippet goalInList(goal: GoalDecorated, index: number)}
  <div class="list-group-item goal-item {expandedGoals[goal.id] ? 'shadow border-2 z-1' : ''}">
    <div class="goal-primary-row">
      <!-- Drag handle -->
      <span>
        {#if goal.isPersonal}
          <ButtonMini
            options={{
              size: 'tiny',
              iconName: 'drag',
              title: 'Endre rekkefølge',
              classes: 'me-2 row-handle-draggable',
              onClick: () => {}, // drag handle only
            }}
          />
        {/if}
      </span>
      <!-- Goal order -->
      <span>
        {goal.sortOrder || index + 1}
      </span>
      <!-- Goal type icon -->
      <span class="goal-type-icon">
        {#if goal.isPersonal}
          <PersonSVG />
        {:else}
          <GroupSVG />
        {/if}
      </span>
      <!-- Goal title -->
      <span>
        {isShowGoalTitleEnabled ? goal.title : '🙊'}
      </span>
      <!-- New observation button -->
      <ButtonMini
        options={{
          iconName: 'plus-sign',
          classes: 'mini-button bordered',
          title: 'Ny observasjon',
          onClick: () => handleEditObservation(goal, null),
        }}
      />
      <!-- Stats widgets -->
      <span class="d-flex align-items-center gap-3 align-items-center">
        {#if goal.masteryData}
          <MasteryLevelBadge masteryData={goal.masteryData} />
          <SparklineChart
            data={goal.observations?.map((o: ObservationReadable) => o.masteryValue)}
          />
        {/if}
      </span>
      <!-- Expand goal info -->
      <ButtonMini
        options={{
          iconName: `chevron-thin-${expandedGoals[goal.id] ? 'up' : 'down'}`,
          classes: 'mini-button rounded justify-end',
          title: `${expandedGoals[goal.id] ? 'Skjul' : 'Vis'} observasjoner`,
          onClick: () => toggleGoalExpansion(goal.id),
        }}
      />
    </div>

    {#if expandedGoals[goal.id]}
      {#if goal?.observations.length === 0}
        <div class="my-3">
          {#if !goal.isPersonal}
            <p>
              Dette målet er ikke personlig, men gitt for <Link to={`/groups/${goal.groupId}/`}>
                hele gruppa
              </Link>.
            </p>
          {:else}
            <p>
              Ingen observasjoner for dette målet. Trykk pluss (+) for å opprette en observasjon.
            </p>

            <ButtonMini
              options={{
                iconName: 'edit',
                classes: 'my-2 me-2',
                title: 'Rediger personlig mål',
                onClick: () => handleEditGoal(goal),
                variant: 'icon-left',
                skin: 'primary',
              }}
            >
              Rediger personlig mål
            </ButtonMini>

            <ButtonMini
              options={{
                iconName: 'trash-can',
                classes: 'my-2',
                title: 'Slett personlig mål',
                onClick: () => handleDeleteGoal(goal.id),
                variant: 'icon-left',
                skin: 'primary',
              }}
            >
              Slett mål
            </ButtonMini>
          {/if}
        </div>
      {:else}
        <div class="goal-secondary-row">
          <div class="student-observations-row mb-2">
            <span>Dato</span>
            <span>Verdi</span>
            <span>Handlinger</span>
          </div>
          {#each goal?.observations as observation, index}
            <div class="student-observations-row observation-item">
              <span>
                {formatDate(observation.observedAt)}
              </span>
              <span>
                {observation.masteryValue}
              </span>
              <span>
                <ButtonMini
                  options={{
                    size: 'tiny',
                    iconName: 'trash-can',
                    title: 'Slett observasjon',
                    classes: 'hover-glow me-2',
                    onClick: () => handleDeleteObservation(observation.id),
                  }}
                />
                {#if index === goal?.observations.length - 1}
                  <ButtonMini
                    options={{
                      size: 'tiny',
                      iconName: 'edit',
                      title: 'Rediger observasjon',
                      classes: 'hover-glow me-2',
                      onClick: () => handleEditObservation(goal, observation),
                    }}
                  />
                {/if}
              </span>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  </div>
{/snippet}

{#if !goalsForSubject?.length}
  <div class="alert alert-info">
    Trykk pluss (+) for å opprette et personlig mål for eleven i dette faget.
  </div>
{:else}
  <div bind:this={goalsListElement} class="list-group mt-2">
    {#each goalsForSubject.filter(goal => goal.isPersonal) as goal, index (goal.id)}
      {@render goalInList(goal, index)}
    {/each}
  </div>
  <div class="list-group mt-4">
    {#each goalsForSubject.filter(goal => !goal.isPersonal) as goal, index (goal.id)}
      {@render goalInList(goal, index)}
    {/each}
  </div>
{/if}

<!-- offcanvas for creating/editing goals -->
<Offcanvas
  bind:isOpen={isGoalEditorOpen}
  ariaLabel="Rediger mål"
  onClosed={() => {
    goalWip = null
    fetchGoalsForSubject()
  }}
>
  {#if goalWip}
    <GoalEdit goal={goalWip} {student} {subject} isGoalPersonal={true} onDone={handleGoalDone} />
  {/if}
</Offcanvas>

<!-- offcanvas for creating/editing observations -->
<Offcanvas
  bind:isOpen={isObservationEditorOpen}
  width="60vw"
  ariaLabel="Rediger observasjon"
  onClosed={() => {
    observationWip = null
    fetchGoalsForSubject()
  }}
>
  {#if observationWip}
    <ObservationEdit
      {student}
      observation={observationWip}
      goal={goalForObservation}
      onDone={handleObservationDone}
    />
  {/if}
</Offcanvas>

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

  .goal-secondary-row {
    margin-top: 10px;
    margin-left: 6px;
    padding-left: 30px;
    border-left: 3px solid var(--bs-secondary);
  }

  .student-observations-row {
    display: grid;
    grid-template-columns: 5fr 3fr 5fr;
    column-gap: 5px;
    align-items: center;
  }

  :global(.row-handle-draggable) {
    cursor: move;
    vertical-align: -8%;
  }

  .goal-type-icon > :global(svg) {
    height: 1.2em;
  }
</style>
