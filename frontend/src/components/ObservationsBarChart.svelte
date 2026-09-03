<script lang="ts">
  import { getISOWeek } from 'date-fns'
  import type { ObservationType } from '../generated'
  import { observationsList } from '../generated/sdk.gen'

  import BarChart from './BarChart.svelte'

  interface Props {
    groupId?: string
    schoolId?: string
    width?: number
    height?: number
    title?: string
    fromDate: string
    toDate: string
  }

  // Props with sane defaults
  const {
    groupId,
    schoolId,
    width = 200,
    height = 100,
    title: providedTitle,
    fromDate,
    toDate,
  }: Props = $props()

  let observations = $state<ObservationType[]>([])
  let data = $state<number[]>([])

  let hasSufficientData = $derived(
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  )
  const title = $derived(providedTitle ?? (hasSufficientData ? data.join(', ') : 'Mangler data'))

  let xLabels = $state<string[]>([])
  let yMaxValue = $derived.by(() => (hasSufficientData ? Math.max(...data, 10) : 10))

  const yLabelsAt = $derived.by(() => {
    if (!hasSufficientData || yMaxValue <= 0) return 1

    const targetTicks = 3 // aim for around 3 ticks on the y-axis
    const roughInterval = yMaxValue / targetTicks

    // Find the magnitude (power of 10)
    const magnitude = Math.pow(10, Math.floor(Math.log10(roughInterval)))

    // Normalize to 1-10 range
    const normalized = roughInterval / magnitude

    // Round to nice number (5 or 10)
    const niceFraction = normalized <= 7.5 ? 5 : 10

    const interval = niceFraction * magnitude

    // Ensure at least 1 for integer counts
    return Math.max(1, Math.round(interval))
  })

  const fetchObservations = async () => {
    const query: any = {
      from: fromDate,
      to: toDate,
    }
    if (groupId) {
      query['group'] = groupId
    }
    if (schoolId) {
      query['school'] = schoolId
    }
    const obsResults = await observationsList({ query })
    observations = obsResults.data || []
    calculateDataAndLabels()
  }

  // group observation counts by week number and build week numbers xLabels array
  const calculateDataAndLabels = () => {
    const observationsByWeek: Record<string, number> = {}
    observations.forEach(obs => {
      const date = new Date(obs.observedAt || obs.createdAt)
      const key = `${date.getFullYear()}-W${getISOWeek(date).toString().padStart(2, '0')}`
      observationsByWeek[key] = (observationsByWeek[key] || 0) + 1
    })

    const newData: number[] = []
    const newLabels: string[] = []

    let current = new Date(fromDate)
    const now = new Date()
    const end = new Date(toDate)
    while (current <= end && current <= now) {
      const key = `${current.getFullYear()}-W${getISOWeek(current).toString().padStart(2, '0')}`
      newData.push(observationsByWeek[key] || 0)
      newLabels.push(getISOWeek(current).toString())
      current.setDate(current.getDate() + 7)
    }

    data = newData
    xLabels = newLabels
  }

  $effect(() => {
    fetchObservations()
  })
</script>

{#if hasSufficientData}
  <BarChart
    {data}
    {yMaxValue}
    yResolution={1}
    {width}
    {height}
    {title}
    {xLabels}
    {yLabelsAt}
    xAxis={0.5}
    yAxis={1}
    colorLookup={(value, index) => 'var(--pkt-color-brand-dark-green-1000)'}
    options={{ isValueOnHoverEnabled: true, isGlowOnHoverEnabled: true }}
  ></BarChart>
{/if}

<style>
</style>
