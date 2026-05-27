<script lang="ts">
  import type { SubjectType, UserType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import StudentSubjectChart from './StudentSubjectChart.svelte'

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
</script>

<h3 class="mt-3 mb-1">
  {subjectName}
</h3>
<hr class="border border-1 mt-0" />
<div class="subject-card-layout py-3">
  <ul class="goals-list list-unstyled mb-0">
    {#each goals as goal (goal.id)}
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
        {#if goal.observations?.length}
          <span
            class="badge rounded-pill bg-secondary flex-shrink-0"
            class:highlighted={hoveredGoalId === goal.id}
          >
            {goal.observations.length} observasjon{goal.observations.length === 1 ? '' : 'er'}
          </span>
        {/if}
      </li>
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
    align-items: center;
  }

  .goals-list {
    width: 60%;
  }

  .goal-row {
    border-bottom: 1px solid var(--bs-border-color);
  }

  .goal-row:last-child {
    border-bottom: none;
  }

  .highlighted {
    background-color: var(--bs-primary) !important;
  }

  @media (min-width: 768px) {
    .subject-card-layout {
      position: relative;
      padding-right: calc(35% + 1rem);
    }

    .goals-list {
      width: 100%;
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
