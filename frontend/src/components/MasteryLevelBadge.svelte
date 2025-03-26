<script lang="ts">
  import { dataStore } from '../stores/data'
  import type { Goal as GoalType } from '../types/models'
  import { getMasteryColorByValue } from '../utils/functions'

  const { studentGoal } = $props<{ studentGoal: GoalType }>()
  const masteryLevels = $derived($dataStore.masteryLevels)
</script>

<span
  class="master-level-badge"
  style="background-color: {getMasteryColorByValue(
    studentGoal.latestObservation?.masteryValue,
    masteryLevels
  )}"
  title={`${studentGoal.title}: ${studentGoal.latestObservation?.masteryValue}`}
></span>

<style>
  .master-level-badge {
    display: inline-block;
    width: 22px;
    height: 22px;
    cursor: pointer;
  }
</style>
