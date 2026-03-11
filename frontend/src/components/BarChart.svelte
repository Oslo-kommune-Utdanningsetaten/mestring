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
    title: providedTitle,
    xLabels = [],
    colorLookup = yValue => 'rgb(100, 100, 100)',
    options = { isValueOnHoverEnabled: false, isGlowOnHoverEnabled: false },
  }: Props = $props()

  const title = $derived(providedTitle || '')
  const fontSize = $derived(Math.max(height * 0.09, 8))
  const labelPadding = $derived(fontSize * 1.5)
  const totalHeight = $derived(height + (xLabels.length > 0 ? labelPadding : 0))
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
        const x = index * baseWidth + gap / 2
        const y = height - barHeight
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
</script>

<svg
  class="bar-chart"
  {width}
  height={totalHeight}
  viewBox={`0 0 ${width} ${totalHeight}`}
  role="img"
  aria-label={title}
>
  <title>{title}</title>
  {#each bars as bar, index}
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
      <text
        x={bar.x + bar.width / 2}
        y={height + fontSize * 1.2}
        text-anchor="middle"
        font-size={fontSize}
        fill="currentColor"
      >
        {bar.xLabel}
      </text>
    {/if}
  {/each}
  {#if options.isValueOnHoverEnabled && hoverIndex >= 0}
    {@const bar = bars[hoverIndex]}
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
