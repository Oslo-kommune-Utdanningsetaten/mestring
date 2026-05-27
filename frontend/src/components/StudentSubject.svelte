<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'

  import type { SubjectType, UserType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'

  import StudentSubjectChart from './StudentSubjectChart.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import GoalObservations from './GoalObservations.svelte'

  const { subject, student, goals } = $props<{
    subject: SubjectType
    student: UserType
    goals: GoalDecorated[]
  }>()

  let { currentUser } = $derived($dataStore)
  let hoveredSubjectId = $state<string | null>(null)
  let hoveredGoalId = $state<string | null>(null)

  let subjectName = $derived(
    subject ? subject.shortName || subject.displayName || subject.grepCode : 'ukjent fag'
  )

  const router = useTinyRouter()
  let expandedGoalIds = $derived<string[]>(router.getQueryParam('expanded')?.split(',') || [])

  const handleToggleGoal = (goalId: string) => {
    const nextExpandedGoals = new Set(expandedGoalIds)
    if (nextExpandedGoals.has(goalId)) {
      nextExpandedGoals.delete(goalId)
    } else {
      nextExpandedGoals.add(goalId)
    }
    expandedGoalIds = Array.from(nextExpandedGoals)
    const newUrl = expandedGoalIds.length
      ? urlStringFrom({ expanded: expandedGoalIds.join(',') }, { mode: 'merge' })
      : urlStringFrom({})
    router.navigate(newUrl)
  }
</script>

<h3 class="mt-3 mb-1">
  {subjectName}
</h3>
<hr class="border border-1 mt-0" />
<div class="subject-card-layout py-3">
  <ul class="goals-list list-unstyled mb-0">
    {#each goals as goal (goal.id)}
      {@const isExpanded = expandedGoalIds.includes(goal.id)}

      <div
        class="list-group-item goal-item {isExpanded
          ? 'shadow border-2 z-1 expanded'
          : ''}  {goal.isRelevant ? '' : 'hatched-background'}"
        title={goal.isRelevant ? '' : 'Målet er ikke lenger relevant for eleven'}
      >
        <li
          class="goal-row d-flex align-items-center justify-content-between gap-2 py-1"
          onmouseenter={() => {
            hoveredGoalId = goal.id
          }}
          onmouseleave={() => {
            hoveredGoalId = null
          }}
        >
          <span>{goal.title}</span>
          <span class="d-flex align-items-center gap-2 flex-shrink-0">
            {#if goal.observations?.length}
              <span
                class="badge rounded-pill bg-secondary"
                class:highlighted={hoveredGoalId === goal.id}
              >
                {goal.observations.length} observasjon{goal.observations.length === 1 ? '' : 'er'}
              </span>
              <ButtonIcon
                options={{
                  iconName: `chevron-thin-${expandedGoalIds.includes(goal.id) ? 'up' : 'down'}`,
                  title: `${expandedGoalIds.includes(goal.id) ? 'Skjul' : 'Vis'} observasjoner`,
                  classes: 'bordered',
                  onClick: () => handleToggleGoal(goal.id),
                }}
              />
            {/if}
          </span>
        </li>
        {#if expandedGoalIds.includes(goal.id) && goal.observations?.length}
          <GoalObservations {goal} {student} {subject} />
        {/if}
      </div>
    {/each}
  </ul>

  <div
    class="chart-wrapper"
    role="img"
    aria-label="Mestringsoversikt for {subjectName}"
    onmouseover={() => {
      hoveredSubjectId = subject.id
    }}
    onmouseleave={() => {
      hoveredSubjectId = null
    }}
    onfocus={() => {
      hoveredSubjectId = subject.id
    }}
    onblur={() => {
      hoveredSubjectId = null
    }}
  >
    <StudentSubjectChart
      student={currentUser}
      {subject}
      isLabelEnabled={hoveredSubjectId === subject.id}
      highlightedGoalId={hoveredGoalId}
    />
  </div>
</div>

<style>
  hr {
    border-color: var(--bs-primary-rgb) !important;
    opacity: 25%;
  }

  .subject-card-layout {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .goals-list {
    width: 100%;
  }

  .goal-row {
    border-bottom: 1px solid var(--bs-border-color);
  }

  .goal-row:last-child {
    border-bottom: none;
  }

  .goal-item {
    background-color: var(--bs-light);
  }

  .goal-item.expanded {
    margin-inline: -0.5rem;
    border-radius: var(--bs-border-radius);
  }

  .highlighted {
    background-color: var(--bs-primary) !important;
  }

  @media (min-width: 768px) {
    .subject-card-layout {
      position: relative;
      padding-right: calc(35% + 1rem);
    }

    .chart-wrapper {
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
      width: 35%;
    }
  }
</style>
