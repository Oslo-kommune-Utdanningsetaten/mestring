<script lang="ts">
  import type { MasteryData, MasterySchemaWithConfig } from '../../types/models'
  import { useMasteryCalculations } from '../../utils/masteryHelpers'

  const {
    masteryData,
    masterySchema,
    isBadgeEmpty = false,
    isBadgeVoid = false,
    isLastValueVisible = true,
  } = $props<{
    masteryData?: MasteryData
    masterySchema?: MasterySchemaWithConfig | null
    isBadgeEmpty?: boolean
    isBadgeVoid?: boolean
    isLastValueVisible?: boolean
  }>()

  const mastery = $derived(masteryData?.mastery ?? 0)
  const trend = $derived(masteryData?.trend ?? 0)
  const title = $derived(
    [masterySchema?.title, masteryData?.title, 'Trend: ' + trend].filter(Boolean).join('\n')
  )
  const calculations = $derived(useMasteryCalculations(masterySchema))

  // Trend
  const isFlat = $derived(Math.abs(trend) < calculations.flatTrendThreshold)
  const isDecreasing = $derived(trend < 0 && !isFlat)

  // Dimensions
  const trendBoxSizeX = 30
  const trendBoxSizeY = 30
  const masteryIndicatorHeight = 4
  const masteryIndicatorWidth = trendBoxSizeX

  // Circle size scales with magnitude of trend value.
  // A full-range trend is very rare, so we consider half range as maxed out
  const minCircleSize = 4
  const maxCircleSize = trendBoxSizeX
  const maxTrendFractionOfRange = 0.2
  const maxMeaningfulTrend = $derived(calculations.deltaValue * maxTrendFractionOfRange)
  const circleFraction = $derived(Math.min(Math.abs(trend) / maxMeaningfulTrend, 1))
  const circleSize = $derived(
    Math.round(minCircleSize + circleFraction * (maxCircleSize - minCircleSize))
  )

  // Calculate mastery indicator position based on available space
  const indicatorPosition = (masteryValue: number) => {
    const maxY = trendBoxSizeY - masteryIndicatorHeight
    if (masteryValue < calculations.minValue) return 0
    if (masteryValue > calculations.maxValue) return maxY
    return Math.round((masteryValue / calculations.maxValue) * maxY)
  }
</script>

<span class="badge-container d-inline-flex align-items-center" {title}>
  {#if masteryData}
    <span class="trend-box" style="width: {trendBoxSizeX}px; height: {trendBoxSizeY}px;"></span>
    <span
      class="trend-circle {isDecreasing ? 'filled' : 'hollow'}"
      style="width: {circleSize}px; height: {circleSize}px;"
    ></span>
    {#if isLastValueVisible}
      <span
        class="mastery-indicator"
        style="bottom: {indicatorPosition(
          mastery
        )}px; width: {masteryIndicatorWidth}px; height: {masteryIndicatorHeight}px; left: 0px;"
      ></span>
    {/if}
  {:else if isBadgeEmpty}
    <span
      class="trend-box missing-mastery"
      style="width: {trendBoxSizeX}px; height: {trendBoxSizeY}px;"
      title="Observasjoner mangler"
    ></span>
  {:else if isBadgeVoid}
    <span
      class="trend-box missing-mastery void-badge"
      style="width: {trendBoxSizeX}px; height: {trendBoxSizeY}px;"
      title="Mål mangler"
    ></span>
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
    border: 1px solid var(--bs-border-color, #dee2e6);
    box-sizing: border-box;
  }

  .trend-circle {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 50%;
  }

  .filled {
    border-radius: 50%;
    background-color: var(--bs-secondary);
  }

  .hollow {
    border: 1px solid var(--bs-secondary);
  }

  .mastery-indicator {
    border: 1px solid var(--bs-secondary);
    border-radius: 0px;
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
