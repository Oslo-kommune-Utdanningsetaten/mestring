<script lang="ts">
  import type { MasteryConfigLevel, MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations, getMasteryColorByValue } from '../utils/masteryHelpers'
  /* SVG SparkbarChart Component */

  type BarRect = {
    x: number
    y: number
    width: number
    height: number
    color: string
  }

  interface Props {
    masterySchema: MasterySchemaWithConfig | null
    data: number[]
    width?: number
    height?: number
    min?: number | null
    max?: number | null
    lineColor?: string
    title?: string
  }

  // Props with sane defaults
  const {
    masterySchema,
    data,
    width = 26,
    height = 26,
    lineColor = 'rgb(100, 100, 100)',
    title: providedTitle,
  }: Props = $props()

  const masteryLevels = $derived<MasteryConfigLevel[]>(masterySchema?.config?.levels ?? [])
  const hasSufficientData = $derived(
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  )
  const calculations = $derived(useMasteryCalculations(masterySchema))
  const title = $derived(providedTitle ?? (hasSufficientData ? data.join(', ') : 'Mangler data'))

  const bars = $derived<BarRect[]>(
    (() => {
      if (!hasSufficientData) return []

      const count = data.length || 1
      const baseWidth = width / count
      const gap = count > 1 ? baseWidth * 0.2 : 0
      const barWidth = Math.max(baseWidth - gap, 0)

      const yChunkCount = calculations.maxValue / calculations.sliderValueIncrement
      const yChunkHeight = height / yChunkCount

      return data.map((value, index) => {
        const barHeight = yChunkHeight * value
        const x = index * baseWidth + gap / 2
        const y = height - barHeight
        const color =
          Number.isFinite(value) && masteryLevels.length > 0
            ? getMasteryColorByValue(value, masteryLevels)
            : lineColor

        return {
          x,
          y,
          width: barWidth,
          height: barHeight,
          color,
        }
      })
    })()
  )
</script>

{#if hasSufficientData}
  <svg
    class="sparkbar-chart"
    {width}
    {height}
    viewBox={`0 0 ${width} ${height}`}
    role="img"
    aria-label={title}
  >
    <title>{title}</title>
    {#each bars as bar, index (index)}
      <rect
        x={bar.x}
        y={bar.y}
        width={bar.width}
        height={bar.height}
        fill={bar.color}
        aria-hidden="true"
      />
    {/each}
  </svg>
{/if}

<style>
  .sparkbar-chart {
    display: inline-block;
  }
</style>
