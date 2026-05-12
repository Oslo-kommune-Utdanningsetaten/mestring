<script lang="ts">
  import BarChart from './BarChart.svelte'
  import { increasingColor, flatColor, decreasingColor } from '../utils/constants'

  interface Props {
    data: number[]
    width?: number
    height?: number
    lineColor?: string
    yResolution?: number
  }

  // Props with sane defaults
  const {
    data,
    width = 30,
    height = 30,
    lineColor = 'rgb(100, 100, 100)',
    yResolution = 1,
  }: Props = $props()

  // The highest number in the dataset
  const yMaxValue = $derived(Math.max(...data))
  const hasSufficientData = $derived(Array.isArray(data) && data.length && yMaxValue)
  const title = $derived(data?.join(', ') || 'Mangler data')
  const xLabels = ['↓', '↔', '↑']

  // Look up colors based on index (0: decreasing, 1: flat, 2: increasing)
  const colorLookup = (trend: number, index: number) => {
    return index === 0 ? decreasingColor : index === 1 ? flatColor : increasingColor
  }
</script>

{#if hasSufficientData}
  <BarChart
    {data}
    {width}
    {height}
    {colorLookup}
    {title}
    {yMaxValue}
    {yResolution}
    {xLabels}
    xAxis={0.2}
  ></BarChart>
{/if}

<style>
</style>
