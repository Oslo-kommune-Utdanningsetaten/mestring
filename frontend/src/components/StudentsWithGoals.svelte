<script lang="ts">
  import type { GoalType, UserType, SubjectType, ObservationType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { hasUserAccessToFeature } from '../stores/access'
  import { localStorage } from '../stores/localStorage'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import MasteryBarChart from './MasteryBarChart.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import Statuses from './Statuses.svelte'
  import UserNameLink from './UserNameLink.svelte'
  import StudentSubjectChart from './StudentSubjectChart.svelte'

  let {
    students,
    goals,
    goalsWithMasteryByStudentId,
    subject,
    statusesKey = 0,
    onEditObservation,
    onEditStatus,
  }: {
    students: UserType[]
    goals: GoalType[]
    goalsWithMasteryByStudentId: Record<string, GoalDecorated[]>
    subject?: SubjectType | null
    statusesKey?: number
    onEditObservation: (
      goal: GoalDecorated,
      observation: ObservationType | null,
      student: UserType
    ) => void
    onEditStatus: (status: null, student: UserType) => void
  } = $props()

  const isSubjectPolarChartVisible = localStorage<boolean>('isSubjectPolarChartVisible')

  // Sort state
  type SortKey = 'name' | string // 'name' or goalId
  let sortBy = $state<SortKey>('name')
  let sortDirection = $state<'asc' | 'desc'>('asc')

  // Compute grid template columns based on which features are enabled
  const gridTemplateColumns = $derived.by(() => {
    const nameCol = 'minmax(5rem, 10rem)'
    const normalCol = 'minmax(4rem, 10rem)'
    const statusCol = 'minmax(min-content, 18rem)'
    const cols: string[] = [nameCol]
    if ($dataStore.currentSchool?.isStatusEnabled && subject) {
      cols.push(statusCol) // status column needs more space
    }
    if ($isSubjectPolarChartVisible) {
      cols.push(normalCol) // polar chart column
    }
    goals.forEach(() => cols.push(normalCol)) // one column per goal
    return cols.join(' ')
  })

  // Compute observation count per student per goal
  let observationCountByStudentAndGoal = $derived.by(() => {
    const counts: Record<string, Record<string, number>> = {}
    Object.entries(goalsWithMasteryByStudentId).forEach(([studentId, decoratedGoals]) => {
      counts[studentId] = {}
      decoratedGoals.forEach(goal => {
        counts[studentId][goal.id] = goal.observations?.length || 0
      })
    })
    return counts
  })

  // Sorted students list
  let sortedStudents = $derived.by(() => {
    const sorted = [...students]
    sorted.sort((a, b) => {
      let comparison: number
      if (sortBy === 'name') {
        comparison = a.name.localeCompare(b.name, 'no')
      } else {
        // sortBy contains a goalId when not sorting by name
        const goalId = sortBy
        const countA = observationCountByStudentAndGoal[a.id]?.[goalId] ?? 0
        const countB = observationCountByStudentAndGoal[b.id]?.[goalId] ?? 0
        comparison = countA - countB
      }
      return sortDirection === 'asc' ? comparison : -comparison
    })
    return sorted
  })

  const handleHeaderClick = (key: SortKey) => {
    if (sortBy === key) {
      // Toggle direction
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
      // New sort key
      sortBy = key
      sortDirection = key === 'name' ? 'asc' : 'desc' // Default: name asc, observations desc
    }
  }

  const getSortIndicator = (key: SortKey): string => {
    if (sortBy !== key) return ''
    return sortDirection === 'asc' ? ' ▲' : ' ▼'
  }

  const isMasteryBarChartVisible = localStorage<boolean>('isMasteryBarChartVisible')

  const getMasterySchemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const getDecoratedGoalFor = (studentId: string, goalId: string): GoalDecorated | null => {
    const studentGoals = goalsWithMasteryByStudentId[studentId] || []
    return studentGoals.find(g => g.id === goalId) || null
  }

  const getObservationValues = (goal: GoalDecorated | null): number[] => {
    if (!goal?.observations) return []
    const observations: ObservationType[] = goal.observations
    return observations.map(o => o.masteryValue).filter((v): v is number => v != null)
  }
</script>

<div
  class="students-grid my-3"
  aria-label="Elevliste"
  style="grid-template-columns: {gridTemplateColumns}"
>
  <span class="item header header-row">
    <button
      class="column-header-button sortable"
      onclick={() => handleHeaderClick('name')}
      title="Sorter etter elevnavn"
    >
      Elev{getSortIndicator('name')}
    </button>
  </span>
  {#if $dataStore.currentSchool.isStatusEnabled && subject}
    <span class="item header header-row">Status</span>
  {/if}
  {#if $isSubjectPolarChartVisible}
    <span class="item header header-row">Oversikt</span>
  {/if}
  {#each goals as goal (goal.id)}
    <span class="item header header-row">
      <button
        onclick={() => handleHeaderClick(goal.id)}
        class="column-header-button sortable {goal.isRelevant
          ? ''
          : 'hatched-background text-muted'}"
        title="Sorter etter antall observasjoner for dette målet"
      >
        {goal.title || goal.sortOrder}{getSortIndicator(goal.id)}
      </button>
    </span>
  {/each}

  {#each sortedStudents as student (student.id)}
    <span class="item">
      <UserNameLink user={student} />
    </span>
    {#if $dataStore.currentSchool.isStatusEnabled && subject}
      <span class="item centered">
        <div class="status-controls">
          {#key statusesKey}
            <Statuses {student} {subject} />
          {/key}

          {#if $hasUserAccessToFeature( 'status', 'create', { subjectId: subject.id, studentGroupIds: student.groupIds } )}
            <ButtonIcon
              options={{
                iconName: 'achievement',
                classes: 'bordered',
                title: 'Legg til ny status',
                onClick: () => onEditStatus(null, student),
              }}
            />
          {/if}
        </div>
      </span>
    {/if}
    {#if $isSubjectPolarChartVisible && student && subject}
      <span class="item centered p-1">
        <StudentSubjectChart {student} {subject} size="medium" />
      </span>
    {/if}
    {#each goals as goal (goal.id)}
      {@const decoratedGoal = getDecoratedGoalFor(student.id, goal.id)}
      <span class="item gap-1 goal-cell">
        {#if decoratedGoal?.masteryData}
          <MasteryLevelBadge
            masteryData={decoratedGoal.masteryData}
            masterySchema={getMasterySchemaForGoal(goal)}
          />
          {#if $isMasteryBarChartVisible}
            <MasteryBarChart
              data={getObservationValues(decoratedGoal)}
              masterySchema={getMasterySchemaForGoal(goal)}
            />
          {/if}
        {:else}
          <MasteryLevelBadge isBadgeEmpty={true} />
        {/if}
        <span class="add-observation-button">
          {#if $hasUserAccessToFeature( 'observation', 'create', { groupId: goal.groupId, subjectId: subject?.id, studentGroupIds: student.groupIds } )}
            <ButtonIcon
              options={{
                iconName: 'bullseye',
                title: 'Legg til observasjon',
                classes: 'bordered',
                disabled: !goal.isRelevant,
                onClick: () => onEditObservation(decoratedGoal || goal, null, student),
              }}
            />
          {/if}
        </span>
      </span>
    {/each}
  {/each}
</div>

<style>
  .students-grid {
    display: grid;
    grid-auto-rows: minmax(2rem, 1fr);
    align-items: stretch;
    gap: 0;
  }

  .students-grid .item {
    padding: 0rem 0.5rem 0rem 0.5rem;
    min-height: 2rem;
    display: flex;
    align-items: center;
    align-self: stretch;
    justify-content: space-between;
    border-right: 1px solid var(--bs-border-color);
    border-bottom: 1px solid var(--bs-border-color);
    gap: 0.5rem;
  }

  .students-grid .item.header-row {
    padding: 0rem 0.2rem 0rem 0.2rem;
    background-color: var(--bs-light);
    font-weight: 800;
    font-size: 0.8rem;
    overflow-wrap: break-word;
    justify-content: center;
  }

  .sortable {
    cursor: pointer;
    border: none;
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .sortable:hover {
    background-color: var(--bs-gray);
  }

  .status-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
  }

  .add-observation-button {
    display: flex;
  }

  .students-grid .item.centered {
    justify-content: center;
  }

  .students-grid .item.centered .status-controls {
    margin-left: 0;
  }

  .students-grid .goal-cell {
    justify-content: center;
  }

  .column-header-button {
    width: 100%;
    padding: 0.1rem 0.2rem 0.1rem 0.2rem;
    background-color: color-mix(
      in srgb,
      var(--pkt-color-surface-strong-light-green) 70%,
      transparent
    );
    border: 1px solid var(--pkt-color-grays-gray-100);
    z-index: 2;
    min-height: 2.8rem;
  }
</style>
