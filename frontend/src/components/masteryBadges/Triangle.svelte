<script lang="ts">
  import type { MasteryData, MasterySchemaWithConfig } from '../../types/models'
  import { useMasteryCalculations, calculateTrendFraction } from '../../utils/masteryHelpers'
  import { t } from '../../stores/translations'

  const {
    masteryData,
    masterySchema,
    title,
    isLastValueVisible,
    isBadgeEmpty = false,
    isBadgeVoid = false,
  }: {
    masteryData?: MasteryData
    masterySchema?: MasterySchemaWithConfig | null
    title: string
    isLastValueVisible: boolean
    isBadgeEmpty?: boolean
    isBadgeVoid?: boolean
  } = $props()

  const mastery = $derived(masteryData?.mastery ?? 0)
  const trend = $derived(masteryData?.trend ?? 0)
  const calculations = $derived(useMasteryCalculations(masterySchema))

  // Trend
  const isFlat = $derived(Math.abs(trend) <= calculations.flatTrendThreshold)
  const isIncreasing = $derived(trend > calculations.flatTrendThreshold)
  const isDecreasing = $derived(trend < calculations.flatTrendThreshold)

  // Dimensions
  const trendBoxSizeX = 30
  const trendBoxSizeY = 30
  const masteryIndicatorHeight = 2
  const masteryIndicatorWidth = trendBoxSizeX

  const minTriangleSize = 8
  const maxTriangleSize = trendBoxSizeX

  // Triangle size scales with the magnitude of the trend.
  const triangleFraction = $derived(calculateTrendFraction(trend, calculations.deltaValue))
  const triangleWidth = $derived(
    Math.round(minTriangleSize + triangleFraction * (maxTriangleSize - minTriangleSize))
  )

  // Flat trend is drawn as a fixed-size square
  const flatSquareSize = minTriangleSize

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

<span class="badge-container d-inline-flex align-items-center" {title}>
  {#if masteryData}
    <span class="trend-box" style="width: {trendBoxSizeX}px; height: {trendBoxSizeY}px;"></span>
    {#if isFlat}
      <span class="trend-square" style={`--square-size: ${flatSquareSize}px;`}></span>
    {:else if isIncreasing}
      <span
        class="trend-triangle up"
        style={`--triangle-width: ${triangleWidth}px; --triangle-height: ${triangleHeight}px;`}
      ></span>
    {:else if isDecreasing}
      <span
        class="trend-triangle down"
        style={`--triangle-width: ${triangleWidth}px; --triangle-height: ${triangleHeight}px;`}
      ></span>
    {/if}
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
      title="{t('observation', { form: 'plu-indef', capitalize: true })} mangler"
    ></span>
  {:else if isBadgeVoid}
    <span
      class="trend-box missing-mastery void-badge"
      style="width: {trendBoxSizeX}px; height: {trendBoxSizeY}px;"
      title="{t('goal', { form: 'sin-indef', capitalize: true })} mangler"
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

  .trend-square {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(45deg);
    width: var(--square-size);
    height: var(--square-size);
    background-color: var(--bs-secondary);
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
