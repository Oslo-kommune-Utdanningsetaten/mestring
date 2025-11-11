<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type { UserType, ObservationType, GoalType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import {
    observationsDestroy,
    goalsDestroy,
    goalsUpdate,
    goalsList,
    groupsList,
    goalsCreate,
  } from '../generated/sdk.gen'
  import { goalsWithCalculatedMasteryBySubjectId } from '../utils/functions'
  import Link from './Link.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparklineChart from './SparklineChart.svelte'
  import SparkbarChart from './SparkbarChart.svelte'
  import GoalEdit from './GoalEdit.svelte'
  import ObservationEdit from './ObservationEdit.svelte'
  import GroupSVG from '../assets/group.svg.svelte'
  import PersonSVG from '../assets/person.svg.svelte'
  import ButtonMini from './ButtonMini.svelte'
  import Offcanvas from './Offcanvas.svelte'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import { getLocalStorageItem } from '../stores/localStorage'
  import { formatDateDistance } from '../utils/functions'

  const { subjectId, student, onRefreshRequired } = $props<{
    subjectId: string
    student: UserType
    onRefreshRequired?: Function
  }>()

  let goalsForSubject = $state<GoalDecorated[]>([])
  let sortableInstance: Sortable | null = null
  let isShowGoalTitleEnabled = $state<boolean>(true)
  let goalWip = $state<GoalDecorated | null>(null)
  let goalForObservation = $state<GoalDecorated | null>(null)
  let observationWip = $state<ObservationType | {} | null>(null)
  let expandedGoals = $state<Record<string, boolean>>({})
  let goalsListElement = $state<HTMLElement | null>(null)
  let subject = $derived($dataStore.subjects.find(s => s.id === subjectId) || null)
  let isGoalEditorOpen = $state<boolean>(false)
  let isObservationEditorOpen = $state<boolean>(false)

  const fetchGoalsForSubject = async () => {
    try {
      const goalsResult = await goalsList({ query: { student: student.id, subject: subjectId } })
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

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
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

  const handleObservationDone = async () => {
    handleCloseEditObservation()
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
      title: 'Legg til nytt individuelt mål',
      onClick: () => handleEditGoal({}),
    }}
  />
</div>

{#snippet goalInList(goal: GoalDecorated, index: number)}
  <div
    class="list-group-item goal-item {expandedGoals[goal.id]
      ? 'shadow border-2 z-1'
      : ''}  {goal.isRelevant ? '' : 'hatched-background'}"
    title={goal.isRelevant ? '' : 'Målet er ikke lenger relevant for eleven'}
  >
    <div class="goal-primary-row">
      <!-- Drag handle -->
      <span class="item">
        {#if goal.isPersonal}
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
        <span class="goal-type-icon item" title="Individuelt mål">
          <PersonSVG />
        </span>
      {:else}
        <span class="goal-type-icon item" title="Gruppemål">
          <GroupSVG />
        </span>
      {/if}

      <!-- Goal title -->
      <span class="item">
        {isShowGoalTitleEnabled ? goal.title : '🙊'}
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
      <span class="item item--right">
        <ButtonMini
          options={{
            iconName: 'plus-sign',
            classes: 'mini-button bordered',
            title: 'Ny observasjon',
            disabled: !goal.isRelevant,
            onClick: () => handleEditObservation(goal, null),
          }}
        />
      </span>

      <!-- Toggle goal info -->
      <span class="item item--right">
        <ButtonMini
          options={{
            iconName: `chevron-thin-${expandedGoals[goal.id] ? 'up' : 'down'}`,
            classes: 'mini-button rounded',
            title: `${expandedGoals[goal.id] ? 'Skjul' : 'Vis'} observasjoner`,
            onClick: () => toggleGoalExpansion(goal.id),
          }}
        />
      </span>
    </div>

    {#if expandedGoals[goal.id]}
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

  .goal-primary-row > .item.item--right {
    justify-content: flex-end;
  }

  .goal-primary-row > .item.item--stats {
    justify-content: flex-end;
    flex-wrap: nowrap;
  }

  .goal-primary-row .item.mt-1 {
    margin-top: 0;
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
  }

  .goal-type-icon > :global(svg) {
    height: 1.2em;
  }
</style>
