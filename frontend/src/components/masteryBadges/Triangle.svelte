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
  const masteryIndicatorHeight = 2
  const masteryIndicatorWidth = trendBoxSizeX

  const minTriangleSize = 4
  const maxTriangleSize = trendBoxSizeX

  // Triangle size scales with magnitude of trend value.
  // A full-range trend is very rare, so we consider half range as maxed out
  const maxTrendFractionOfRange = 0.5
  const maxMeaningfulTrend = $derived(calculations.deltaValue * maxTrendFractionOfRange)
  const triangleFraction = $derived(Math.min(Math.abs(trend) / maxMeaningfulTrend, 1))
  const triangleWidth = $derived(
    Math.round(minTriangleSize + triangleFraction * (maxTriangleSize - minTriangleSize))
  )

  // Equilateral triangle: height = width * sqrt(3) / 2
  const triangleHeight = $derived(Math.round((triangleWidth * Math.sqrt(3)) / 2))

  // Calculate mastery indicator position based on available space
  const indicatorPosition = (masteryValue: number) => {
    const maxY = trendBoxSizeY - masteryIndicatorHeight
    if (masteryValue < calculations.minValue) return 0
    if (masteryValue > calculations.maxValue) return maxY
    return Math.round((masteryValue / calculations.maxValue) * maxY)
  }
</script>

<span class="badge-container d-flex align-items-center">
  {#if masteryData}
    <span
      class="trend-box"
      style="width: {trendBoxSizeX}px; height: {trendBoxSizeY}px;"
      title={`${title}`}
    ></span>
    <span
      class="trend-triangle {isDecreasing ? 'down' : 'up'}"
      style={`--triangle-width: ${triangleWidth}px; --triangle-height: ${triangleHeight}px;`}
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

  .trend-triangle {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 0;
    height: 0;
    border-left: calc(var(--triangle-width) / 2) solid transparent;
    border-right: calc(var(--triangle-width) / 2) solid transparent;
  }

  .trend-triangle.up {
    border-bottom: var(--triangle-height) solid var(--bs-secondary);
  }

  .trend-triangle.down {
    border-top: var(--triangle-height) solid var(--bs-secondary);
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
