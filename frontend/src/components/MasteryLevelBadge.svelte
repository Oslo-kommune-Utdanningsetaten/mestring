<script lang="ts">
  import type { Mastery } from '../types/models'

  const { masteryData } = $props<{ masteryData: Mastery | null }>()
  const increasingColor = 'var(--bs-success)'
  const flatColor = 'var(--bs-warning)'
  const decreasingColor = 'var(--bs-danger)'

  const mastery = $derived(masteryData?.mastery ?? 0)
  const trend = $derived(masteryData?.trend ?? 0)
  const title = $derived(masteryData?.title ?? '')

  const similarityRange = 6 // +/- 5 range for flat trend
  const isFlat = $derived(Math.abs(trend) < similarityRange)
  const isDecreasing = $derived(trend < 0 && !isFlat)
  const trendColor = $derived(isDecreasing ? decreasingColor : isFlat ? flatColor : increasingColor)

  const trendBoxSize = 25
  const masteryIndicatorHeight = 4
  const masteryIndicatorOutcrop = 2
  const masteryIndicatorWidth = trendBoxSize + masteryIndicatorOutcrop * 2

  // Calculate mastery indicator position based on available space
  function indicatorPosition(masteryValue: number) {
    const maxY = trendBoxSize - masteryIndicatorHeight
    if (masteryValue < 0) return 0
    if (masteryValue > 100) return maxY
    return Math.round((masteryValue / 100) * maxY)
  }
</script>

<span class="badge-container">
  {#if masteryData}
    <span
      class="trend-box"
      style="background-color: {trendColor}; width: {trendBoxSize}px; height: {trendBoxSize}px;"
      title={`${title}`}
    >
      <span
        class="mastery-indicator"
        style="bottom: {indicatorPosition(
          mastery
        )}px; border-color: {trendColor}; height: {masteryIndicatorHeight}px; width: {masteryIndicatorWidth}px; left: {-masteryIndicatorOutcrop}px;"
      ></span>
    </span>
  {:else}
    <span
      class="trend-box missing-mastery"
      style="width: {trendBoxSize}px; height: {trendBoxSize}px;"
      title="Ingen observasjoner"
    >
      &nbsp;
    </span>
  {/if}
</span>

<style>
  .badge-container {
    position: relative;
    display: inline-block;
    height: 28px;
    margin-right: 5px;
  }

  .trend-box {
    display: inline-block;
    position: relative;
  }

  .mastery-indicator {
    border-width: 1px 1px 1px 1px;
    border-style: solid;
    position: absolute;
    background-color: white;
  }

  .missing-mastery {
    background-color: white;
    border: 1px solid #ccc;
    position: relative;
  }
</style>
