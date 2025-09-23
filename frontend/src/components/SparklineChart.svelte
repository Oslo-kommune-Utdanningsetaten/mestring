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

  const {
    data,
    width = 28,
    height = 28,
    min = 0,
    max = 100,
    lineColor = 'rgb(100, 100, 100)',
    strokeWidth = 1.6,
  }: Props = $props()

  const hasData = () =>
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  const effectiveMin = () => min ?? (hasData() ? Math.min(...data) : 0)
  const effectiveMax = () => max ?? (hasData() ? Math.max(...data) : 1)
  const title = $derived(hasData() ? data.join(', ') : 'Mangler data')

  const calculatePoints = () => {
    const valueCount = data.length
    if (!hasData() || valueCount === 1) return ''
    const low = effectiveMin()
    const high = effectiveMax()
    const span = high - low || 1

    const stepX = width / (valueCount - 1)
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

{#if hasData()}
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
  .sparkline-chart.empty {
    opacity: 0.3;
  }
</style>
