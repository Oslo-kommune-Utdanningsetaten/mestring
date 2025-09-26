<script lang="ts">
  /* SVG Sparkline Component */

  interface Props {
    data: number[]
    width?: number
    height?: number
    min?: number | null
    max?: number | null
    lineColor?: string
    strokeWidth?: number
    title?: string
  }

  // Props with sane defaults
  const {
    data,
    width = 26,
    height = 26,
    min = 0,
    max = 100,
    lineColor = 'rgb(100, 100, 100)',
    strokeWidth = 1.6,
  }: Props = $props()

  const hasSufficientData = $derived(
    Array.isArray(data) && data.length > 1 && data.every(n => Number.isFinite(n))
  )
  const effectiveMin = $derived(min ?? (hasSufficientData ? Math.min(...data) : 0))
  const effectiveMax = $derived(max ?? (hasSufficientData ? Math.max(...data) : 1))
  const title = $derived(hasSufficientData ? data.join(', ') : 'Mangler data')

  const calculatePoints = () => {
    if (!hasSufficientData) return ''

    const low = effectiveMin
    const high = effectiveMax
    const span = high - low || 1
    const stepX = width / (data.length - 1)

    return data
      .map((value, index) => {
        const normalized = (value - low) / span
        const x = index * stepX
        const y = (1 - normalized) * height
        return `${x.toFixed(2)},${y.toFixed(2)}`
      })
      .join(' ')
  }
</script>

{#if hasSufficientData}
  <svg
    class="sparkline-chart"
    {width}
    {height}
    viewBox={`0 0 ${width} ${height}`}
    role="img"
    aria-label={title}
  >
    <title>{title}</title>
    <polyline
      points={calculatePoints()}
      fill="none"
      stroke={lineColor}
      stroke-width={strokeWidth}
      vector-effect="non-scaling-stroke"
      stroke-linejoin="round"
      stroke-linecap="round"
    />
  </svg>
{/if}

<style>
  .sparkline-chart {
    display: inline-block;
  }
</style>
