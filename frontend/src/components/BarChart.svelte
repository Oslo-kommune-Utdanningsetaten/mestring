<script lang="ts">
  type BarRect = {
    x: number
    y: number
    width: number
    height: number
    color: string
    xLabel: string | null
    value: number
  }

  interface Props {
    data: number[]
    yMaxValue: number
    yResolution: number
    width: number
    height: number
    title?: string
    xLabels?: string[]
    yLabelsAt?: number
    xAxis?: number
    yAxis?: number
    colorLookup?: (value: number) => string
    options?: {
      isValueOnHoverEnabled?: boolean
      isGlowOnHoverEnabled?: boolean
    }
  }

  // Props with sane defaults
  const {
    data,
    yMaxValue,
    yResolution,
    width,
    height,
    title,
    xLabels = [],
    yLabelsAt,
    xAxis = 0,
    yAxis = 0,
    colorLookup = yValue => 'rgb(100, 100, 100)',
    options = { isValueOnHoverEnabled: false, isGlowOnHoverEnabled: false },
  }: Props = $props()

  const fontSize = $derived(Math.max(height * 0.09, 8))
  const topPadding = $derived(xLabels.length > 0 ? fontSize : 0)
  const bottomPadding = $derived(fontSize * 1.5)
  const leftPadding = $derived(yLabelsAt ? fontSize * 1.5 : 0)
  const totalHeight = $derived(height + topPadding + (xLabels.length > 0 ? bottomPadding : 0))
  const totalWidth = $derived(width + leftPadding)
  const gapLabelRatio = 0.2
  let hoverIndex = $state<number>(-1)

  const bars = $derived<BarRect[]>(
    (() => {
      const count = data.length || 1
      const baseWidth = width / count
      const gap = count > 1 ? baseWidth * gapLabelRatio : 0
      const barWidth = Math.max(baseWidth - gap, 0)

      const yChunkCount = yMaxValue / yResolution
      const yChunkHeight = height / yChunkCount

      return data.map((value, index) => {
        const barHeight = yChunkHeight * value
        const x = index * baseWidth + gap / 2 + leftPadding
        const y = height - barHeight + topPadding
        const color = colorLookup(value)

        return {
          x,
          y,
          width: barWidth,
          height: barHeight,
          color,
          xLabel: xLabels[index] || null,
          value,
        }
      })
    })()
  )

  const yLabels = $derived<Array<{ value: number; y: number }>>(
    (() => {
      if (!yLabelsAt || yLabelsAt <= 0) return []

      const labels: Array<{ value: number; y: number }> = []
      const yLabelStepHeight = (height * yResolution) / yMaxValue
      for (let value = yLabelsAt; value <= yMaxValue; value += yLabelsAt) {
        const y = height - yLabelStepHeight * value + topPadding
        labels.push({ value, y })
      }
      return labels
    })()
  )
</script>

<svg
  class="bar-chart"
  width={totalWidth}
  height={totalHeight}
  viewBox={`0 0 ${totalWidth} ${totalHeight}`}
  role="img"
  aria-label={title}
>
  <title>{title}</title>
  {#each bars as bar, index}
    <!-- bars -->
    <rect
      class:bar={options.isGlowOnHoverEnabled}
      x={bar.x}
      y={bar.y}
      width={bar.width}
      height={bar.height}
      fill={bar.color}
      aria-hidden="true"
      onmouseenter={() => (hoverIndex = index)}
      onmouseleave={() => (hoverIndex = -1)}
    ></rect>
    {#if bar.xLabel}
      <!-- x-axis labels-->
      <text
        x={bar.x + bar.width / 2}
        y={height + topPadding + fontSize * 1.2}
        text-anchor="middle"
        font-size={fontSize}
        fill="currentColor"
      >
        {bar.xLabel}
      </text>
    {/if}
  {/each}
  {#if xAxis > 0}
    <!-- x-axis -->
    <line
      x1={leftPadding}
      y1={height + topPadding}
      x2={width + leftPadding}
      y2={height + topPadding}
      stroke="currentColor"
      stroke-width={xAxis}
      vector-effect="non-scaling-stroke"
    />
  {/if}
  {#if yAxis > 0}
    <!-- y-axis -->
    <line
      x1={leftPadding}
      y1={topPadding}
      x2={leftPadding}
      y2={height + topPadding}
      stroke="currentColor"
      stroke-width={yAxis}
      vector-effect="non-scaling-stroke"
    />
  {/if}
  {#each yLabels as label}
    <!-- y-axis ticks -->
    <line
      x1={leftPadding}
      y1={label.y}
      x2={leftPadding + fontSize * 0.2}
      y2={label.y}
      stroke="currentColor"
      stroke-width={1}
      vector-effect="non-scaling-stroke"
    />
    <!-- y-axis labels -->
    <text
      x={leftPadding - fontSize * 0.3}
      y={label.y}
      text-anchor="end"
      dominant-baseline="middle"
      font-size={fontSize}
      fill="currentColor"
    >
      {label.value}
    </text>
  {/each}
  {#if yLabels.length > 0}{/if}
  {#if options.isValueOnHoverEnabled && hoverIndex >= 0}
    {@const bar = bars[hoverIndex]}
    <!-- on hover bar values -->
    <circle
      class="tooltip-bg"
      cx={bar.x + bar.width / 2}
      cy={totalHeight / 2}
      r={fontSize}
      fill="rgba(200, 200, 200, 0.7)"
      pointer-events="none"
    />
    <text
      class="tooltip-text"
      x={bar.x + bar.width / 2}
      y={totalHeight / 2}
      text-anchor="middle"
      dominant-baseline="central"
      font-size={fontSize}
      font-weight="bold"
      fill="black"
      pointer-events="none"
    >
      {bar.value}
    </text>
  {/if}
</svg>

<style>
  .bar-chart {
    display: inline-block;
  }

  .bar {
    transition:
      opacity 0.1s ease,
      filter 0.1s ease;
  }

  .bar:hover {
    opacity: 0.8;
    filter: brightness(1.2);
  }

  .tooltip-bg,
  .tooltip-text {
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
</style>
