<script lang="ts">
  import type { MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations } from '../utils/masteryHelpers'

  interface Props {
    data: number[]
    width?: number
    height?: number
    masterySchema: MasterySchemaWithConfig | null
    lineColor?: string
    strokeWidth?: number
    title?: string
  }

  // Props with sane defaults
  const {
    data,
    width = 26,
    height = 26,
    masterySchema,
    lineColor = 'rgb(100, 100, 100)',
    strokeWidth = 1.6,
  }: Props = $props()

  const hasSufficientData = $derived(
    Array.isArray(data) && data.length > 1 && data.every(n => Number.isFinite(n))
  )
  const title = $derived(hasSufficientData ? data.join(', ') : 'Mangler data')
  const calculations = $derived(useMasteryCalculations(masterySchema))

  const calculatePoints = () => {
    if (!hasSufficientData) return ''

    const stepX = width / (data.length - 1)
    const yChunkCount = calculations.maxValue / calculations.sliderValueIncrement
    const yChunkHeight = height / yChunkCount

    return data
      .map((value, index) => {
        const x = index * stepX
        const y = height - yChunkHeight * value //(1 - normalized) * height
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
