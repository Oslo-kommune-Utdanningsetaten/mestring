<script lang="ts">
  const { mastery } = $props<{
    mastery: { status: number; trend: number; title: string; groupName: string } | null
  }>()

  const { status, trend, title } = mastery || {}
  const similarityRange = 6 // +/- 5 similarity threshold
  const isFlat = Math.abs(trend) < similarityRange
  const isDecreasing = trend < 0 && !isFlat

  const increasingColor = 'var(--bs-success)'
  const flatColor = 'var(--bs-warning)'
  const decreasingColor = 'var(--bs-danger)'
  const trendColor = isDecreasing ? decreasingColor : isFlat ? flatColor : increasingColor

  const trendBoxSize = 22
  const statusIndicatorHeight = 4
  const statusIndicatorOutcrop = 2
  const statusIndicatorWidth = trendBoxSize + statusIndicatorOutcrop * 2

  // Calculate status indicator position based on available space
  function indicatorPosition(masteryValue: number) {
    const maxY = trendBoxSize - statusIndicatorHeight
    if (masteryValue < 0) return 0
    if (masteryValue > 100) return maxY
    return Math.round((masteryValue / 100) * maxY)
  }
</script>

<span class="badge-container">
  {#if mastery}
    <span
      class="trend-box"
      style="background-color: {trendColor}; width: {trendBoxSize}px; height: {trendBoxSize}px;"
      title={`${title}`}
    >
      <span
        class="status-indicator"
        style="bottom: {indicatorPosition(
          status
        )}px; border-color: {trendColor}; height: {statusIndicatorHeight}px; width: {statusIndicatorWidth}px; left: {-statusIndicatorOutcrop}px;"
      ></span>
    </span>
  {:else}
    <span
      class="trend-box missing-mastery"
      style="width: {trendBoxSize}px; height: {trendBoxSize}px;"
      title="Ingen mål registrert"
    >
      &nbsp;
    </span>
  {/if}
</span>

<style>
  .badge-container {
    position: relative;
    display: inline-block;
    height: 30px;
    margin-right: 5px;
  }

  .trend-box {
    display: inline-block;
    position: relative;
  }

  .status-indicator {
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
