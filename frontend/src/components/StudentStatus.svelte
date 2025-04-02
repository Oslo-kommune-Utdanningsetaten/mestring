<script lang="ts">
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import { dataStore } from '../stores/data'
  import type { Goal as GoalType } from '../types/models'

  const { studentGoals } = $props<{ studentGoals: GoalType }>()

  const studentGoalsWithLatestObservation = $derived(
    studentGoals.map((goal: GoalType): object => {
      const result: any = { ...goal }
      const observations = $dataStore.observations
        .filter(o => o.goalId === goal.id)
        .sort((a, b) => {
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        })
      result.latestObservation = observations[0]
      return result
    })
  )
</script>

<div class="d-flex gap-1 justify-content-start">
  {#each studentGoalsWithLatestObservation as studentGoal}
    <MasteryLevelBadge {studentGoal} />
  {/each}
</div>

<style>
</style>
