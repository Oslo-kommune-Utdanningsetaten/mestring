<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import Sortable, { type SortableEvent } from 'sortablejs'
  import type { GoalDecorated } from '../types/models'
  import type {
    UserType,
    ObservationType,
    GoalType,
    StatusType,
    SubjectType,
  } from '../generated/types.gen'
  import { goalsDestroy, goalsUpdate, goalsCreate } from '../generated/sdk.gen'

  import { dataStore } from '../stores/data'
  import { localStorage } from '../stores/localStorage'
  import {
    getPreferredStatusCategory,
    getPreferredSubjectId,
  } from '../stores/localStorageFunctions'
  import { fetchGoalsForSubjectAndStudent, urlStringFrom, getSubjectName } from '../utils/functions'
  import { hasUserAccessToFeature } from '../stores/access'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'

  import Link from './Link.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import MasteryBarChart from './MasteryBarChart.svelte'
  import StatusEdit from './edit/StatusEdit.svelte'
  import ButtonMini from './ButtonMini.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import Offcanvas from './Offcanvas.svelte'
  import Statuses from '../components/Statuses.svelte'
  import AuthorInfo from './AuthorInfo.svelte'
  import StudentSubjectChart from './StudentSubjectChart.svelte'
  import MasteryLevelTitle from './MasteryLevelTitle.svelte'
  import ObservationVisibilityMarker from './ObservationVisibilityMarker.svelte'
  import ObservationWidgets from './edit/ObservationWidgets.svelte'
  import GoalWidgets from './edit/GoalWidgets.svelte'

  const { student, subject } = $props<{
    student: UserType
    subject: SubjectType
  }>()

  const router = useTinyRouter()

  let goalsForSubject = $state<GoalDecorated[]>([])
  let statusWip = $state<Partial<StatusType> | null>(null)
  let goalsListElement = $state<HTMLElement | null>(null)
  let isStatusEditorOpen = $state<boolean>(false)
  let statusesKey = $state<number>(0) // key used to force re-render of Statuses component
  let chartKey = $state<number>(0) // key used to force re-render of StudentSubjectChart component when goals are updated

  let subjectName = $derived(subject ? getSubjectName(subject) : 'ukjent fag')
  let expandedGoalIds = $derived(router.getQueryParam('expanded')?.split(',') || [])
  let sortableInstance: Sortable | null = null

  const isMasteryBarChartVisible = localStorage<boolean>('isMasteryBarChartVisible')
  const isSubjectPolarChartVisible = localStorage<boolean>('isSubjectPolarChartVisible')
  const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000)
  const today = new Date()

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const fetchGoals = async () => {
    goalsForSubject = await fetchGoalsForSubjectAndStudent(
      subject.id,
      student.id,
      $dataStore.currentSchool?.id!,
      $dataStore.currentUser.allGroups
    )
    chartKey++
  }

  const handleEditStatus = async (status: Partial<StatusType> | null) => {
    if (status?.id) {
      statusWip = {
        ...status,
      }
    } else {
      statusWip = {
        subjectId: subject.id,
        studentId: student.id,
        schoolId: $dataStore.currentSchool.id,
        categoryId: getPreferredStatusCategory(),
        beginAt: sixtyDaysAgo.toISOString().split('T')[0],
        endAt: today.toISOString().split('T')[0],
      }
    }
    isStatusEditorOpen = true
  }

  const handleStatusDone = async () => {
    isStatusEditorOpen = false
    statusesKey++
  }

  const handleToggleGoal = (goalId: string) => {
    const nextExpandedGoals = new Set(expandedGoalIds)
    if (nextExpandedGoals.has(goalId)) {
      nextExpandedGoals.delete(goalId)
    } else {
      nextExpandedGoals.add(goalId)
    }
    const nextExpandedGoalIds = Array.from(nextExpandedGoals)
    const newUrl = nextExpandedGoalIds.length
      ? urlStringFrom(
          { expanded: nextExpandedGoalIds.join(',') },
          { path: `/students/${student.id}`, mode: 'merge' }
        )
      : urlStringFrom({}, { path: `/students/${student.id}` })
    router.navigate(newUrl)
  }

  const handleGoalOrderChange = async (event: SortableEvent) => {
    const { oldIndex, newIndex } = event
    if (oldIndex === undefined || newIndex === undefined) return

    const localGoals = [...goalsForSubject.filter(g => g.isIndividual)] // only individual goals are draggable
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
    if (student && subject) {
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

<div class="d-flex align-items-center gap-2 mt-2">
  <h3>
    {subjectName}
  </h3>

  <GoalWidgets
    {student}
    {subject}
    masterySchema={$dataStore.defaultMasterySchema?.id}
    isIndividual={true}
    isRelevant={true}
    onRefreshRequired={() => fetchGoals()}
    widgets={['create']}
  />

  {#if $hasUserAccessToFeature( 'status', 'create', { subjectId: subject.id, studentGroupIds: student.groupIds } )}
    <ButtonIcon
      options={{
        iconName: 'achievement',
        classes: 'bordered ms-1',
        title: 'Legg til ny status',
        onClick: () => handleEditStatus(null),
      }}
    />
  {/if}

  {#key statusesKey}
    <Statuses {student} {subject} />
  {/key}
</div>

{#if $isSubjectPolarChartVisible}
  <div class="d-flex justify-content-center p-2">
    {#key chartKey}
      <div class="chart-wrapper">
        <StudentSubjectChart {student} {subject} isLabelEnabled={true} />
      </div>
    {/key}
  </div>
{/if}

{#snippet goalInList(goal: GoalDecorated, index: number)}
  {@const isExpanded = expandedGoalIds.includes(goal.id)}
  <div
    class="list-group-item goal-item {isExpanded
      ? 'shadow border-2 expanded'
      : ''}  {goal.isRelevant ? '' : 'hatched-background'}"
    title={goal.isRelevant ? '' : 'Målet er ikke lenger relevant for eleven'}
  >
    <div class="goal-primary-row">
      <!-- Drag handle -->
      <span class="item">
        {#if goal.isIndividual && goalsForSubject.filter(g => g.isIndividual).length > 1}
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
      {#if goal.isIndividual}
        <span class="item" title="Individuelt mål">
          <pkt-icon name="person" aria-hidden="true"></pkt-icon>
        </span>
      {:else}
        <span class="item" title="Gruppemål">
          <pkt-icon name="group" aria-hidden="true"></pkt-icon>
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
          {#if $isMasteryBarChartVisible && !$dataStore.currentUser.isStudent}
            <MasteryBarChart
              data={goal.observations?.map((o: ObservationType) => o.masteryValue)}
              masterySchema={getMasterySchmemaForGoal(goal)}
            />
          {/if}
        {/if}
      </span>

      <!-- New observation button -->
      <span class="item">
        <ObservationWidgets
          {goal}
          {student}
          {subject}
          onRefreshRequired={() => fetchGoals()}
          widgets={['create']}
        />
      </span>

      <!-- Toggle goal info -->
      <span class="item chevron">
        <ButtonIcon
          options={{
            iconName: `chevron-thin-${isExpanded ? 'up' : 'down'}`,
            disabled: !goal.isRelevant,
            title: `${isExpanded ? 'Skjul' : 'Vis'} observasjoner`,
            onClick: () => handleToggleGoal(goal.id),
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
                <span class="bordered">
                  <ObservationVisibilityMarker {observation} />
                  <AuthorInfo item={observation} />
                </span>
              </span>
              <span class="bordered">
                <MasteryLevelTitle {observation} masterySchema={getMasterySchmemaForGoal(goal)} />
              </span>
              <span>
                <ObservationWidgets
                  {observation}
                  {goal}
                  {student}
                  {subject}
                  onRefreshRequired={() => fetchGoals()}
                  widgets={['update', 'delete', 'view', 'productUrl']}
                />
              </span>
            </div>
          {/each}
        {:else}
          <p>Ingen observasjoner for dette målet.</p>
        {/if}
      </div>
      <div class="my-3">
        {#if goal.isIndividual}
          <GoalWidgets
            {goal}
            {student}
            {subject}
            masterySchema={$dataStore.defaultMasterySchema?.id}
            isIndividual={true}
            isRelevant={true}
            onRefreshRequired={() => fetchGoals()}
            widgets={['update', 'delete']}
            disabledWidgets={goal.observations?.length > 0 ? ['delete'] : []}
            buttonSize="large"
          />
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
    {#each goalsForSubject.filter(goal => goal.isIndividual) as goal, index (`${goal.id}-${expandedGoalIds.includes(goal.id)}`)}
      {@render goalInList(goal, index)}
    {/each}
  </div>
  <div class="list-group mt-2">
    {#each goalsForSubject.filter(goal => !goal.isIndividual) as goal, index (`${goal.id}-${expandedGoalIds.includes(goal.id)}`)}
      {@render goalInList(goal, index)}
    {/each}
  </div>
{/if}

<!-- offcanvas for creating/editing status -->
<Offcanvas
  bind:isOpen={isStatusEditorOpen}
  ariaLabel="Rediger status"
  onClosed={() => {
    statusWip = null
  }}
>
  {#if statusWip}
    <StatusEdit status={statusWip} onDone={handleStatusDone} />
  {/if}
</Offcanvas>

<style>
  .chart-wrapper {
    width: 100%;
    height: 20rem;
  }

  div.observation-item > span {
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.95rem;
    letter-spacing: -0.07em;
    padding-left: 0.1rem;
  }

  h3 {
    font-size: 1.5rem;
  }

  .goal-item {
    background-color: var(--bs-light);
  }

  .goal-item.expanded {
    margin-inline: -0.5rem;
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
