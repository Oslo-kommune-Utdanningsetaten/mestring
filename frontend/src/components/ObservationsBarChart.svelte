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
  }

  // Props with sane defaults
  const { groupId, schoolId, width = 200, height = 100, title: providedTitle }: Props = $props()

  let observations = $state<ObservationType[]>([])
  let data = $state<number[]>([])
  let hasSufficientData = $derived(
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  )
  const title = $derived(providedTitle ?? (hasSufficientData ? data.join(', ') : 'Mangler data'))
  const fromDate = $derived.by(() => {
    const now = new Date()
    return now.getMonth() < 7 ? `${now.getFullYear()}-01-01` : `${now.getFullYear()}-08-01`
  })
  let xLabels = $state<string[]>([])
  let yMaxValue = $derived.by(() => (hasSufficientData ? Math.max(...data, 15) : 10))

  const yLabelsAt = $derived.by(() => {
    if (!hasSufficientData || yMaxValue <= 0) return 1

    const targetTicks = 3 // aim for around 3 ticks on the y-axis
    const roughInterval = yMaxValue / targetTicks

    // Find the magnitude (power of 10)
    const magnitude = Math.pow(10, Math.floor(Math.log10(roughInterval)))

    // Normalize to 1-10 range
    const normalized = roughInterval / magnitude

    // Round to nice number (1, 2, 5, or 10)
    let niceFraction
    if (normalized <= 1.5) {
      niceFraction = 1
    } else if (normalized <= 3.5) {
      niceFraction = 2
    } else if (normalized <= 7.5) {
      niceFraction = 5
    } else {
      niceFraction = 10
    }

    const interval = niceFraction * magnitude

    // Ensure at least 1 for integer counts
    return Math.max(1, Math.round(interval))
  })

  const fetchObservations = async () => {
    const query: any = {
      from: fromDate,
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
    const observationsByWeek: Record<number, number> = {}
    observations.forEach(obs => {
      const week = getISOWeek(new Date(obs.observedAt || obs.createdAt))
      observationsByWeek[week] = (observationsByWeek[week] || 0) + 1
    })
    const beginAtWeek = getISOWeek(new Date(fromDate))
    const endAtWeek = getISOWeek(new Date())
    for (let week = beginAtWeek; week <= endAtWeek; week++) {
      data.push(observationsByWeek[week] || 0)
      xLabels.push(`${week}`)
    }
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
    colorLookup={() => 'var(--pkt-color-brand-dark-green-1000)'}
    options={{ isValueOnHoverEnabled: true, isGlowOnHoverEnabled: true }}
  ></BarChart>
{/if}

<style>
</style>
