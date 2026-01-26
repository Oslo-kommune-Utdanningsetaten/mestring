<script lang="ts">
  import type { GoalType, UserType, SubjectType, ObservationType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import SparkbarChart from './SparkbarChart.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import Statuses from './Statuses.svelte'

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
    subject: SubjectType
    statusesKey?: number
    onEditObservation: (
      goal: GoalDecorated,
      observation: ObservationType | null,
      student: UserType
    ) => void
    onEditStatus: (status: null, student: UserType) => void
  } = $props()

  // Sort state
  type SortKey = 'name' | string // 'name' or goalId
  let sortBy = $state<SortKey>('name')
  let sortDirection = $state<'asc' | 'desc'>('asc')

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

<div class="teaching-grid my-3" aria-label="Elevliste" style="--columns-count: {goals.length}">
  <button
    class="item header header-row sortable"
    onclick={() => handleHeaderClick('name')}
    title="Sorter etter elevnavn"
  >
    Elev{getSortIndicator('name')}
  </button>
  {#each goals as goal (goal.id)}
    <button
      class="item header header-row sortable"
      onclick={() => handleHeaderClick(goal.id)}
      title="Sorter etter antall observasjoner for dette målet"
    >
      <span class="column-header {goal.isRelevant ? '' : 'hatched-background text-muted'}">
        {goal.title || goal.sortOrder}{getSortIndicator(goal.id)}
      </span>
    </button>
  {/each}
  {#each sortedStudents as student (student.id)}
    <span class="item student-cell">
      <a href={`/students/${student.id}`}>
        {student.name}
      </a>
      {#if $dataStore.currentSchool.isStatusEnabled}
        <div class="status-controls">
          {#if $dataStore.hasUserAccessToFeature( 'status', 'read', { subjectId: subject.id, studentId: student.id } )}
            {#key statusesKey}
              <Statuses {student} {subject} />
            {/key}
          {/if}

          {#if $dataStore.hasUserAccessToFeature( 'status', 'create', { subjectId: subject.id, studentId: student.id } )}
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
      {/if}
    </span>
    {#each goals as goal (goal.id)}
      {@const decoGoal = getDecoratedGoalFor(student.id, goal.id)}
      <span class="item gap-1">
        {#if decoGoal?.masteryData}
          <MasteryLevelBadge
            masteryData={decoGoal.masteryData}
            masterySchema={getMasterySchemaForGoal(goal)}
          />
          <SparkbarChart
            data={getObservationValues(decoGoal)}
            masterySchema={getMasterySchemaForGoal(goal)}
          />
        {:else}
          <MasteryLevelBadge isBadgeEmpty={true} />
        {/if}
        <span class="add-observation-button">
          <ButtonIcon
            options={{
              iconName: 'bullseye',
              title: 'Legg til observasjon',
              classes: 'bordered',
              disabled: !goal.isRelevant,
              onClick: () => onEditObservation(decoGoal || goal, null, student),
            }}
          />
        </span>
      </span>
    {/each}
  {/each}
</div>

<style>
  .teaching-grid {
    display: grid;
    grid-template-columns: 3fr repeat(var(--columns-count, 8), 1fr);
    grid-auto-rows: minmax(5rem, 1fr);
    align-items: stretch;
    gap: 0;
  }

  .teaching-grid .item {
    padding: 0.5rem;
    min-height: 3rem;
    display: flex;
    align-items: center;
    align-self: stretch;
    justify-content: space-between;
    border-right: 1px solid var(--bs-border-color);
    border-bottom: 1px solid var(--bs-border-color);
  }

  .teaching-grid .item.header-row {
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .sortable {
    cursor: pointer;
    border: none;
    border-right: 1px solid var(--bs-border-color);
    border-bottom: 1px solid var(--bs-border-color);
    background-color: var(--bs-light);
    font-weight: 800;
  }

  .sortable:hover {
    background-color: var(--bs-gray-300);
  }

  .student-cell {
    justify-content: space-between;
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }

  .status-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
  }

  .add-observation-button {
    display: flex;
    margin-left: auto;
  }

  .column-header {
    transform: rotate(-60deg);
    font-size: 0.8rem;
    padding: 0.1rem 0.1rem 0.1rem 0.3rem;
    max-width: 5rem;
    background-color: var(--pkt-color-surface-strong-light-green);
    border: 1px solid var(--pkt-color-grays-gray-100);
  }
</style>
