<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'

  import type { SubjectType, UserType, GoalType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'
  import { urlStringFrom } from '../utils/functions'

  import StudentSubjectChart from './StudentSubjectChart.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import GoalObservations from './GoalObservations.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'

  const {
    subject,
    student,
    goals,
    isTitleEnabled = true,
  } = $props<{
    subject: SubjectType
    student: UserType
    goals: GoalDecorated[]
    isTitleEnabled?: boolean
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
      ? urlStringFrom(
          { expanded: expandedGoalIds.join(',') },
          { path: window.location.pathname, mode: 'merge' }
        )
      : urlStringFrom({}, { path: window.location.pathname })
    router.navigate(newUrl)
  }

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return $dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }
</script>

{#if isTitleEnabled}
  <h3 class="mt-3 mb-1">
    {subjectName}
  </h3>
  <hr class="border border-1 mt-0" />
{/if}
<div class="subject-card-layout py-3">
  <ul class="goals-list list-unstyled mb-0">
    {#each goals as goal (goal.id)}
      {@const isExpanded = expandedGoalIds.includes(goal.id)}
      {@const masterySchema = getMasterySchmemaForGoal(goal)}
      <div
        class="list-group-item goal-item {isExpanded ? 'shadow expanded' : ''}"
        class:hatched-background={!goal.isRelevant}
        title={goal.isRelevant ? '' : 'Målet er ikke lenger relevant for eleven'}
        role="listitem"
        onmouseenter={() => {
          hoveredGoalId = goal.id
        }}
        onmouseleave={() => {
          hoveredGoalId = null
        }}
      >
        <li class="goal-row d-flex align-items-center justify-content-between gap-2 py-1">
          <span class="d-flex align-content-center gap-2">
            {goal.title || goal.sortOrder}
            {#if isExpanded}
              {#if goal.isIndividual}
                <span title="Individuelt mål">
                  <pkt-icon class="goal-type-icon" name="person" aria-hidden="true"></pkt-icon>
                </span>
              {:else}
                <span title="Gruppemål">
                  <pkt-icon class="goal-type-icon" name="group" aria-hidden="true"></pkt-icon>
                </span>
              {/if}
            {/if}
          </span>

          <span class="d-flex align-items-center gap-2 flex-shrink-0">
            {#if goal.observations?.length}
              <span
                class="badge rounded-pill bg-secondary"
                class:highlighted={hoveredGoalId === goal.id}
              >
                {goal.observations.length} observasjon{goal.observations.length === 1 ? '' : 'er'}
              </span>

              <!-- Mastery Badge -->
              {#if goal.masteryData}
                <MasteryLevelBadge masteryData={goal.masteryData} {masterySchema} />
              {/if}

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
    margin-inline: -1.5rem;
    margin-bottom: 1.25rem;
    border-radius: var(--bs-border-radius);
    border-color: var(--bs-border-color);
    border-width: 0.2px !important;
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
