<script lang="ts">
  import type { MasteryConfigLevel, MasterySchemaWithConfig } from '../types/models'
  import { useMasteryCalculations, getMasteryLevelColorByValue } from '../utils/masteryHelpers'
  import BarChart from './BarChart.svelte'

  interface Props {
    masterySchema: MasterySchemaWithConfig | null
    data: number[]
    width?: number
    height?: number
    lineColor?: string
    title?: string
  }

  // Props with sane defaults
  const {
    masterySchema,
    data,
    width = 30,
    height = 30,
    lineColor = 'rgb(100, 100, 100)',
    title: providedTitle,
  }: Props = $props()

  const hasSufficientData = $derived(
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  )
  const calculations = $derived(useMasteryCalculations(masterySchema))
  const title = $derived(providedTitle ?? (hasSufficientData ? data.join(', ') : 'Mangler data'))

  const colorLookup = (value: number) =>
    Number.isFinite(value)
      ? getMasteryLevelColorByValue(value, masterySchema)
      : lineColor
</script>

<BarChart
  {data}
  yMaxValue={calculations.maxValue}
  yResolution={calculations.sliderValueIncrement}
  {width}
  {height}
  {colorLookup}
  {title}
></BarChart>

<style>
</style>
