<script lang="ts">
  type BarRect = {
    x: number
    y: number
    width: number
    height: number
    color: string
    xLabel: string | null
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
  }: Props = $props()

  const title = $derived(providedTitle || '')
  const hasSufficientData = $derived(
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  )

  const fontSize = $derived(Math.max(height * 0.09, 8))
  const labelPadding = $derived(fontSize * 1.5)
  const totalHeight = $derived(height + (xLabels.length > 0 ? labelPadding : 0))

  const bars = $derived<BarRect[]>(
    (() => {
      if (!hasSufficientData) return []

      const count = data.length || 1
      const baseWidth = width / count
      const gap = count > 1 ? baseWidth * 0.2 : 0
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
        }
      })
    })()
  )
</script>

{#if hasSufficientData}
  <svg
    class="sparkbar-chart"
    {width}
    height={totalHeight}
    viewBox={`0 0 ${width} ${totalHeight}`}
    role="img"
    aria-label={title}
  >
    <title>{title}</title>
    {#each bars as bar}
      <rect
        x={bar.x}
        y={bar.y}
        width={bar.width}
        height={bar.height}
        fill={bar.color}
        aria-hidden="true"
      />
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
  </svg>
{/if}

<style>
  .sparkbar-chart {
    display: inline-block;
  }
</style>
