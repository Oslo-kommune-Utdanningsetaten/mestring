<script lang="ts">
  import { dataStore } from '../stores/data'
  import Link from './Link.svelte'
  import type {
    Student as StudentType,
    Subject as SubjectType,
    Group as GroupType,
    Goal as GoalType,
  } from '../types/models'

  const { studentGoals } = $props<{ studentGoals: GoalType }>()
  const masteryLevels = $derived($dataStore.masteryLevels)

  const studentGoalsWithLatestObservation = $derived(
    studentGoals.map((goal: GoalType): object => {
      const result: any = { ...goal }
      const observations = $dataStore.observations
        .filter(o => o.goalId === goal.id)
        .sort((a, b) => {
          return new Date(b.date).getTime() - new Date(a.date).getTime()
        })
      result.latestObservation = observations[0]
      return result
    })
  )

  function getMasterColorByValue(value: number): string {
    const masteryLevel = masteryLevels.find(ml => ml.minValue <= value && ml.maxValue >= value)
    return masteryLevel ? masteryLevel.color : 'black'
  }
</script>

<div class="d-flex gap-1 justify-content-center">
  {#each studentGoalsWithLatestObservation as goal}
    <span
      class="master-level-badge"
      style="background-color: {getMasterColorByValue(goal.latestObservation?.masteryValue)}"
      title={`${goal.title}: ${goal.latestObservation?.masteryValue}`}
    ></span>
  {/each}
</div>

<style>
  .master-level-badge {
    display: inline-block;
    width: 22px;
    height: 22px;
    cursor: pointer;
  }
</style>
