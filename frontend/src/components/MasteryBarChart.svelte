<script lang="ts">
  import type { MasterySchemaWithConfig } from '../types/models'
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

  const title = $derived.by(() => {
    if (providedTitle) return providedTitle
    if (!calculations.isMasteryValueVisible) return ''
    if (hasSufficientData) return data.join(', ')
    return 'Mangler data'
  })

  const colorLookup = (value: number, index: number) =>
    Number.isFinite(value) ? getMasteryLevelColorByValue(value, masterySchema) : lineColor
</script>

<BarChart
  {data}
  yMaxValue={calculations.maxValue}
  yResolution={calculations.inputValueIncrement}
  {width}
  {height}
  {colorLookup}
  {title}
></BarChart>

<style>
</style>
