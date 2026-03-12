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
    yLabelsAt={5}
    xAxis={0.5}
    yAxis={1}
    colorLookup={() => 'var(--pkt-color-brand-dark-green-1000)'}
    options={{ isValueOnHoverEnabled: true, isGlowOnHoverEnabled: true }}
  ></BarChart>
{/if}

<style>
</style>
