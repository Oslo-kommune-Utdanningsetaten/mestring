<script lang="ts">
  import type { MasteryConfigLevel, MasterySchemaWithConfig } from '../types/models'
  import { getMasteryColorByValue } from '../utils/functions'
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
    min = 0,
    max = 100,
    lineColor = 'rgb(100, 100, 100)',
    title: providedTitle,
  }: Props = $props()

  const masteryLevels = $derived<MasteryConfigLevel[]>(masterySchema?.config?.levels ?? [])
  const hasSufficientData = $derived(
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  )
  const effectiveMin = $derived(min ?? (hasSufficientData ? Math.min(...data) : 0))
  const effectiveMax = $derived(max ?? (hasSufficientData ? Math.max(...data) : 1))
  const title = $derived(providedTitle ?? (hasSufficientData ? data.join(', ') : 'Mangler data'))

  const bars = $derived<BarRect[]>(
    (() => {
      if (!hasSufficientData) return []

      const count = data.length || 1
      const span = effectiveMax - effectiveMin || 1
      const baseWidth = width / count
      const gap = count > 1 ? baseWidth * 0.2 : 0
      const barWidth = Math.max(baseWidth - gap, 0)

      return data.map((value, index) => {
        const normalized = (value - effectiveMin) / span
        const clamped = Math.max(0, Math.min(1, normalized))
        const barHeight = clamped * height
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
