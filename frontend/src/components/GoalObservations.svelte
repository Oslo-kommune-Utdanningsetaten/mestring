<script lang="ts">
  import type { ObservationType, UserType, GoalType, SubjectType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { dataStore } from '../stores/data'

  import AuthorInfo from './AuthorInfo.svelte'
  import MasteryLevelTitle from './MasteryLevelTitle.svelte'
  import ObservationWidgets from './ObservationWidgets.svelte'

  const { student, goal, subject, onRefreshNeeded } = $props<{
    student: UserType
    goal: GoalDecorated
    subject: SubjectType
    onRefreshNeeded: () => void
  }>()

  let masterySchema = $derived($dataStore.masterySchemas.find(ms => ms.id === goal.masterySchemaId))
  let observations = $derived(
    goal.observations
      ? goal.observations.toSorted((goalA: GoalType, goalB: GoalType) => {
          // sort observations by createdAt ascending
          const dateA = new Date(goalA.createdAt)
          const dateB = new Date(goalB.createdAt)
          return dateA.getTime() - dateB.getTime()
        })
      : []
  )
</script>

<div class="goal-secondary-row">
  {#if observations.length}
    {#each observations as observation}
      <div class="student-observations-row observation-item">
        <span>
          <AuthorInfo item={observation} />
        </span>

        <span>
          <MasteryLevelTitle {observation} {masterySchema} />
        </span>

        <span>
          <ObservationWidgets
            {observation}
            {goal}
            {student}
            {subject}
            onRefreshRequired={() => onRefreshNeeded()}
            widgets={['view', 'update', 'delete']}
          />
        </span>
      </div>
    {/each}
  {:else}
    <p>Ingen observasjoner for dette målet.</p>
  {/if}
</div>

<style>
  div.observation-item > span {
    font-size: 0.85rem;
  }

  .goal-secondary-row {
    margin-top: 10px;
    margin-left: 6px;
    padding-left: 20px;
    border-left: 3px solid var(--bs-secondary);
  }

  .student-observations-row {
    display: grid;
    grid-template-columns: 8fr 5fr 4fr;
    column-gap: 0.5rem;
    align-items: center;
  }

  .student-observations-row > span:last-child {
    justify-self: end;
  }
</style>
