<script lang="ts">
  import { ca } from 'date-fns/locale'
  import type { Mastery, MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'

  const {
    masteryData,
    masterySchema,
    isBadgeEmpty = false,
    isBadgeVoid = false,
  } = $props<{
    masteryData?: Mastery
    masterySchema?: MasterySchemaWithConfig | null
    isBadgeEmpty?: boolean
    isBadgeVoid?: boolean
  }>()

  const mastery = $derived(masteryData?.mastery ?? 0)
  const trend = $derived(masteryData?.trend ?? 0)
  const title = $derived(masteryData?.title ?? '')
  const calculations = $derived(useMasteryCalculations(masterySchema))

  // Trend
  const isFlat = $derived(Math.abs(trend) < calculations.flatTrendThreshold)
  const isDecreasing = $derived(trend < 0 && !isFlat)
  // Colors
  const increasingColor = 'var(--bs-success)'
  const flatColor = 'var(--bs-warning)'
  const decreasingColor = 'var(--bs-danger)'
  const trendColor = $derived(isDecreasing ? decreasingColor : isFlat ? flatColor : increasingColor)
  // Dimensions
  const trendBoxSize = 24
  const masteryIndicatorHeight = 4
  const masteryIndicatorOutcrop = 2
  const masteryIndicatorWidth = trendBoxSize + masteryIndicatorOutcrop * 2
  // Calculate mastery indicator position based on available space
  const indicatorPosition = (masteryValue: number) => {
    const maxY = trendBoxSize - masteryIndicatorHeight
    if (masteryValue < calculations.minValue) return 0
    if (masteryValue > calculations.maxValue) return maxY
    return Math.round((masteryValue / calculations.maxValue) * maxY)
  }
</script>

<span class="badge-container d-flex align-items-center">
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
  {:else if isBadgeEmpty}
    <span
      class="trend-box missing-mastery"
      style="width: {trendBoxSize}px; height: {trendBoxSize}px;"
      title="Observasjoner mangler"
    ></span>
  {:else if isBadgeVoid}
    <span
      class="trend-box missing-mastery void-badge"
      style="width: {trendBoxSize}px; height: {trendBoxSize}px;"
      title="Mål mangler"
    ></span>{/if}
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

  .void-badge {
    background: repeating-linear-gradient(
      -45deg,
      color-mix(in srgb, var(--bs-gray) 50%, transparent),
      color-mix(in srgb, var(--bs-gray) 50%, transparent) 1px,
      white 2px,
      white 4px
    );
  }
</style>
