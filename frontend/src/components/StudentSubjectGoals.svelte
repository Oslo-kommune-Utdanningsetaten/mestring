<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type {
    UserType,
    ObservationType,
    GoalType,
    GroupType,
    StatusType,
  } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import {
    observationsDestroy,
    goalsDestroy,
    goalsUpdate,
    goalsList,
    goalsCreate,
  } from '../generated/sdk.gen'
  import Link from './Link.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparkbarChart from './SparkbarChart.svelte'
  import GoalEdit from './GoalEdit.svelte'
  import ObservationEdit from './ObservationEdit.svelte'
  import StatusEdit from './StatusEdit.svelte'
  import ButtonMini from './ButtonMini.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import Offcanvas from './Offcanvas.svelte'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import { getLocalStorageItem } from '../stores/localStorage'
  import { formatDateDistance, fetchGoalsForSubjectAndStudent } from '../utils/functions'

  const { subjectId, student, onRefreshRequired } = $props<{
    subjectId: string
    student: UserType
    onRefreshRequired?: Function
  }>()

  let goalsForSubject = $state<GoalDecorated[]>([])
  let sortableInstance: Sortable | null = null
  let goalWip = $state<GoalDecorated | null>(null)
  let statusWip = $state<Partial<StatusType> | null>(null)
  let goalForObservation = $state<GoalDecorated | null>(null)
  let observationWip = $state<ObservationType | {} | null>(null)
  let expandedGoals = $state<Record<string, boolean>>({})
  let goalsListElement = $state<HTMLElement | null>(null)
  let subject = $derived($dataStore.subjects.find(s => s.id === subjectId) || null)
  let isGoalEditorOpen = $state<boolean>(false)
  let isObservationEditorOpen = $state<boolean>(false)
  let isStatusEditorOpen = $state<boolean>(false)
  const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000)
  const today = new Date()

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const fetchGoals = async () => {
    goalsForSubject = await fetchGoalsForSubjectAndStudent(
      subjectId,
      student.id,
      $dataStore.currentUser.allGroups
    )
  }

  const handleEditStatus = async (status: Partial<StatusType> | null) => {
    if (status?.id) {
      statusWip = {
        ...status,
      }
    } else {
      statusWip = {
        subjectId: subjectId,
        studentId: student.id,
        schoolId: $dataStore.currentSchool.id,
        beginAt: sixtyDaysAgo.toISOString().split('T')[0],
        endAt: today.toISOString().split('T')[0],
      }
    }
    isStatusEditorOpen = true
  }

  // Remember, we're only editing personal goals here
  const handleEditGoal = async (goal: GoalDecorated | null) => {
    if (goal.id) {
      goalWip = {
        ...goal,
        subjectId: goal?.subjectId || getLocalStorageItem('preferredSubjectId'),
        studentId: student.id,
        sortOrder: goal?.sortOrder || (goalsForSubject?.length ? goalsForSubject.length + 1 : 1),
        masterySchemaId: goal?.masterySchemaId || $dataStore.defaultMasterySchema?.id,
      }
    } else {
      const personalGoalsCount = goalsForSubject?.filter(g => g.isPersonal).length
      const newGoal = {
        subjectId: subjectId,
        studentId: student.id,
        isPersonal: true,
        sortOrder: personalGoalsCount + 1,
        masterySchemaId: $dataStore.defaultMasterySchema?.id,
        schoolId: $dataStore.currentSchool.id,
        isRelevant: true,
      }

      // If all stars are aligned, just create the goal instantly instead of exposing the user to the create goal form
      const createInstantly =
        !$dataStore.currentSchool.isGoalTitleEnabled &&
        !!$dataStore.defaultMasterySchema?.id &&
        !!subjectId

      if (createInstantly) {
        await goalsCreate({
          body: newGoal,
        })
        return onRefreshRequired()
      } else {
        // open the goal editor with prefilled values
        goalWip = newGoal
      }
    }
    isGoalEditorOpen = true
  }

  const handleCloseEditGoal = () => {
    isGoalEditorOpen = false
    if (onRefreshRequired) onRefreshRequired()
  }

  const handleEditObservation = (goal: GoalDecorated, observation: ObservationType | null) => {
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
  }

  const handleGoalDone = async () => {
    goalForObservation = null
    handleCloseEditGoal()
  }

  const handleCloseEditStatus = () => {
    isStatusEditorOpen = false
  }

  const handleStatusDone = async () => {
    goalForObservation = null
    handleCloseEditStatus()
  }

  const handleObservationDone = async () => {
    handleCloseEditObservation()
  }

  const handleDeleteObservation = async (observationId: string) => {
    try {
      await observationsDestroy({ path: { id: observationId } })
      await fetchGoals()
    } catch (error) {
      console.error('Error deleting observation:', error)
    }
  }

  const handleDeleteGoal = async (goalId: string) => {
    try {
      await goalsDestroy({ path: { id: goalId } })
      await fetchGoals()
    } catch (error) {
      console.error('Error deleting goal:', error)
    }
  }

  const toggleGoalExpansion = (goalId: string) => {
    expandedGoals = {
      ...expandedGoals,
      [goalId]: !expandedGoals[goalId],
    }
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
      await fetchGoals()
    }
  }

  $effect(() => {
    if (student && subjectId) {
      fetchGoals()
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
  <ButtonIcon
    options={{
      iconName: 'goal',
      classes: 'bordered',
      title: 'Legg til nytt individuelt mål',
      onClick: () => handleEditGoal({}),
    }}
  />

  <ButtonIcon
    options={{
      iconName: 'achievement',
      classes: 'bordered',
      title: 'Legg til ny status',
      onClick: () => handleEditStatus(null),
    }}
  />
</div>

{#snippet goalInList(goal: GoalDecorated, index: number)}
  {@const isExpanded = expandedGoals[goal.id] || false}
  <div
    class="list-group-item goal-item {isExpanded ? 'shadow border-2 z-1' : ''}  {goal.isRelevant
      ? ''
      : 'hatched-background'}"
    title={goal.isRelevant ? '' : 'Målet er ikke lenger relevant for eleven'}
  >
    <div class="goal-primary-row">
      <!-- Drag handle -->
      <span class="item">
        {#if goal.isPersonal && goalsForSubject.filter(g => g.isPersonal).length > 1}
          <ButtonMini
            options={{
              size: 'tiny',
              iconName: 'drag',
              title: 'Endre rekkefølge',
              classes: 'row-handle-draggable',
            }}
          />
        {/if}
      </span>

      <!-- Goal order -->
      <span class="item">
        {goal.sortOrder || index + 1}
      </span>

      <!-- Goal type icon -->
      {#if goal.isPersonal}
        <span class="individual-goal-icon item" title="Individuelt mål">
          <pkt-icon name="person"></pkt-icon>
        </span>
      {:else}
        <span class="group-goal-icon item" title="Gruppemål">
          <pkt-icon name="group"></pkt-icon>
        </span>
      {/if}

      <!-- Goal title -->
      <span class="item">
        {$dataStore.currentSchool.isGoalTitleEnabled ? goal.title : ''}
      </span>

      <!-- Stats widgets -->
      <span class="item item--stats d-flex gap-2">
        {#if goal.masteryData}
          <MasteryLevelBadge
            masteryData={goal.masteryData}
            masterySchema={getMasterySchmemaForGoal(goal)}
          />
          <SparkbarChart
            data={goal.observations?.map((o: ObservationType) => o.masteryValue)}
            masterySchema={getMasterySchmemaForGoal(goal)}
          />
        {/if}
      </span>

      <!-- New observation button -->
      <span class="item">
        <ButtonIcon
          options={{
            iconName: 'bullseye',
            title: 'Ny observasjon',
            classes: 'bordered',
            disabled: !goal.isRelevant,
            onClick: () => handleEditObservation(goal, null),
          }}
        />
      </span>

      <!-- Toggle goal info -->
      <span class="item chevron">
        <ButtonIcon
          options={{
            iconName: `chevron-thin-${isExpanded ? 'up' : 'down'}`,
            disabled: !goal.isRelevant,
            title: `${isExpanded ? 'Skjul' : 'Vis'} observasjoner`,
            onClick: () => toggleGoalExpansion(goal.id),
          }}
        />
      </span>
    </div>

    {#if isExpanded}
      <div class="goal-secondary-row">
        {#if goal.observations?.length}
          <div class="student-observations-row mb-2">
            <span>Når</span>
            <span>Verdi</span>
            <span>Handlinger</span>
          </div>
          {#each goal?.observations as observation, index}
            <div class="student-observations-row observation-item">
              <span>
                {formatDateDistance(observation.observedAt)}
              </span>
              <span>
                {observation.masteryValue}
              </span>
              <span>
                <ButtonIcon
                  options={{
                    iconName: 'trash-can',
                    title: 'Slett observasjon',
                    classes: 'bordered',
                    onClick: () => handleDeleteObservation(observation.id),
                  }}
                />
                {#if index === goal?.observations.length - 1}
                  <ButtonIcon
                    options={{
                      iconName: 'edit',
                      title: 'Rediger observasjon',
                      classes: 'bordered',
                      onClick: () => handleEditObservation(goal, observation),
                    }}
                  />
                {/if}
              </span>
            </div>
          {/each}
        {:else}
          <p>Ingen observasjoner for dette målet.</p>
        {/if}
      </div>
      <div class="my-3">
        {#if goal.isPersonal}
          <ButtonMini
            options={{
              iconName: 'edit',
              classes: 'my-2 me-2',
              title: 'Rediger individuelt mål',
              onClick: () => handleEditGoal(goal),
              variant: 'icon-left',
              skin: 'secondary',
            }}
          >
            Rediger individuelt mål
          </ButtonMini>

          <ButtonMini
            options={{
              iconName: 'trash-can',
              classes: 'my-2',
              title: 'Slett individuelt mål',
              onClick: () => handleDeleteGoal(goal.id),
              disabled: goal.observations?.length > 0,
              variant: 'icon-left',
              skin: 'secondary',
            }}
          >
            Slett mål
          </ButtonMini>
        {:else}
          <p>
            Dette målet er ikke individuelt, men gitt for <Link to={`/groups/${goal.groupId}/`}>
              hele gruppa
            </Link>.
          </p>
        {/if}
      </div>
    {/if}
  </div>
{/snippet}

{#if goalsForSubject?.length}
  <div bind:this={goalsListElement} class="list-group mt-2">
    {#each goalsForSubject.filter(goal => goal.isPersonal) as goal, index (`${goal.id}-${expandedGoals[goal.id]}`)}
      {@render goalInList(goal, index)}
    {/each}
  </div>
  <div class="list-group mt-4">
    {#each goalsForSubject.filter(goal => !goal.isPersonal) as goal, index (`${goal.id}-${expandedGoals[goal.id]}`)}
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
    fetchGoals()
  }}
>
  {#if goalWip}
    <GoalEdit goal={goalWip} {student} {subject} isGoalPersonal={true} onDone={handleGoalDone} />
  {/if}
</Offcanvas>

<!-- offcanvas for creating/editing status -->
<Offcanvas
  bind:isOpen={isStatusEditorOpen}
  width="60vw"
  ariaLabel="Rediger status"
  onClosed={() => {
    statusWip = null
  }}
>
  {#if statusWip}
    <StatusEdit
      status={statusWip}
      {student}
      {subject}
      goals={goalsForSubject}
      onDone={handleStatusDone}
    />
  {/if}
</Offcanvas>

<!-- offcanvas for creating/editing observations -->
<Offcanvas
  bind:isOpen={isObservationEditorOpen}
  width="60vw"
  ariaLabel="Rediger observasjon"
  onClosed={() => {
    observationWip = null
    fetchGoals()
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
    grid-template-columns: auto auto auto minmax(0, 1fr) auto auto auto;
    column-gap: 0.5rem;
    align-items: center;
  }

  .goal-primary-row > .item {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.25rem;
  }

  .goal-primary-row > .item.chevron {
    display: flex;
    margin-left: auto;
    justify-self: end;
  }

  .goal-primary-row > .item.item--stats {
    justify-content: flex-end;
    flex-wrap: nowrap;
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
</style>
