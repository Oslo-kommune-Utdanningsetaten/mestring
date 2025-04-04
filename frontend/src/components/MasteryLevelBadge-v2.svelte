<script lang="ts">
  import { dataStore } from '../stores/data'
  import type { Goal as GoalType } from '../types/models'

  const { studentGoal } = $props<{ studentGoal: GoalType }>()
  const similarityRange = 5 // +/- 5 similarity threshold

  // Check if the latest observation is less than the first observation
  const firstValue = $derived(studentGoal.observations[0]?.masteryValue)

  const lastValue = $derived(
    studentGoal.observations[studentGoal.observations.length - 1]?.masteryValue
  )

  // check if the last observation is roughly similar to the first observation
  const isFlat = $derived(Math.abs(lastValue - firstValue) < similarityRange)
  const isDecreasing = $derived(lastValue < firstValue && !isFlat)

  const increasingColor = 'var(--bs-success)'
  const flatColor = 'var(--bs-warning)'
  const decreasingColor = 'var(--bs-danger)'

  const indicatorPosition = $derived(Math.min(studentGoal.latestObservation?.masteryValue || 0, 83))
</script>

<span
  class="mastery-level-badge"
  style="background-color: {isFlat ? flatColor : isDecreasing ? decreasingColor : increasingColor};"
  title={`${studentGoal.title}: ${studentGoal.latestObservation?.masteryValue}`}
>
  <span
    class="valueIndicator"
    style="bottom: {indicatorPosition}%; border-color: {isFlat
      ? flatColor
      : isDecreasing
        ? decreasingColor
        : increasingColor};"
  ></span>
</span>

<style>
  .mastery-level-badge {
    display: inline-block;
    position: relative;
    width: 22px;
    height: 22px;
    cursor: pointer;
  }

  .valueIndicator {
    border-width: 1px 1px 1px 1px;
    border-style: solid;
    position: absolute;
    background-color: white;
    left: -2px;
    width: 26px;
    height: 4px;
  }
</style>
